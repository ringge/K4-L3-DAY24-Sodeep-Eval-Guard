from __future__ import annotations

"""Phase B: LLM-as-Judge — pairwise, swap-and-average, Cohen κ, bias analysis."""

import json
import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, JUDGE_MODEL, HUMAN_LABELS_PATH


@dataclass
class JudgeResult:
    question: str
    answer_a: str
    answer_b: str
    winner_pass1: str       # "A" | "B" | "tie"  (original order)
    winner_pass2: str       # "A" | "B" | "tie"  (after swap, ALREADY converted back)
    final_winner: str       # consensus after swap-and-average
    reasoning_pass1: str
    reasoning_pass2: str
    position_consistent: bool  # True if both passes agree on same answer
    scores_pass1: dict = field(default_factory=dict)  # {"A": float, "B": float}
    scores_pass2: dict = field(default_factory=dict)


# ─── Task 5: Pairwise Judge ───────────────────────────────────────────────────

API_BUDGET_USD = 0.10
_CUMULATIVE_COST_USD = 0.0
_TOTAL_PROMPT_TOKENS = 0
_TOTAL_COMPLETION_TOKENS = 0
_CALL_COUNT = 0
# Conservative rate ($1.00 / 1M input, $4.00 / 1M output) to strictly protect the $0.10 limit
_PROMPT_COST_PER_1M = 1.00
_COMPLETION_COST_PER_1M = 4.00


def _check_and_record_cost(resp) -> None:
    """Track token usage from live OpenAI responses and abort if budget ($0.10) is exceeded."""
    global _CUMULATIVE_COST_USD, _TOTAL_PROMPT_TOKENS, _TOTAL_COMPLETION_TOKENS, _CALL_COUNT
    usage = getattr(resp, "usage", None)
    if usage is None:
        return
    prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
    completion_tokens = getattr(usage, "completion_tokens", 0) or 0
    call_cost = (
        prompt_tokens * _PROMPT_COST_PER_1M + completion_tokens * _COMPLETION_COST_PER_1M
    ) / 1_000_000
    _CALL_COUNT += 1
    _TOTAL_PROMPT_TOKENS += prompt_tokens
    _TOTAL_COMPLETION_TOKENS += completion_tokens
    _CUMULATIVE_COST_USD += call_cost
    print(
        f"  [API Call #{_CALL_COUNT:02d}] in={prompt_tokens} out={completion_tokens} tokens | "
        f"cumulative~${_CUMULATIVE_COST_USD:.5f} / limit=${API_BUDGET_USD:.2f}",
        flush=True,
    )
    if _CUMULATIVE_COST_USD > API_BUDGET_USD:
        raise RuntimeError(
            f"ALERT: API cost exceeded limit ${API_BUDGET_USD:.2f} "
            f"(current: ${_CUMULATIVE_COST_USD:.6f}). Aborted immediately!"
        )


def _install_live_openai_guard() -> None:
    """Wrap live OpenAI Completions.create so all Phase B calls obey the $0.10 limit and model params."""
    try:
        from openai.resources.chat.completions import Completions
    except Exception:
        return
    if getattr(Completions.create, "_phase_b_guarded", False):
        return
    orig_create = Completions.create

    def guarded_create(self, *args, **kwargs):
        if _CUMULATIVE_COST_USD >= API_BUDGET_USD:
            raise RuntimeError(
                f"CẢNH BÁO: Chi phí API đã chạm giới hạn ${API_BUDGET_USD:.2f} "
                f"(hiện tại: ${_CUMULATIVE_COST_USD:.6f}). Đã dừng thực thi!"
            )
        model_name = str(kwargs.get("model", "")).lower()
        if "luna" in model_name and kwargs.get("temperature") == 0:
            kwargs = {k: v for k, v in kwargs.items() if k != "temperature"}
        resp = orig_create(self, *args, **kwargs)
        _check_and_record_cost(resp)
        return resp

    guarded_create._phase_b_guarded = True
    Completions.create = guarded_create


_install_live_openai_guard()


def pairwise_judge(question: str, answer_a: str, answer_b: str, reference: str = "") -> dict:
    """Task 5: Gọi LLM để chọn answer tốt hơn (A hoặc B) theo 3 tiêu chí.

    Tiêu chí đánh giá:
        - Độ chính xác (accuracy): có khớp với thực tế chính sách không?
        - Độ đầy đủ (completeness): có trả lời đủ câu hỏi không?
        - Tính súc tích (conciseness): có thừa / thiếu thông tin không?

    Returns:
        {"winner": "A"|"B"|"tie", "reasoning": str, "scores": {"A": float, "B": float}}
    """
    if _CUMULATIVE_COST_USD >= API_BUDGET_USD:
        raise RuntimeError(
            f"CẢNH BÁO: Chi phí API đã chạm giới hạn ${API_BUDGET_USD:.2f} "
            f"(hiện tại: ${_CUMULATIVE_COST_USD:.6f}). Đã dừng thực thi!"
        )

    prompt_template = """Bạn là một expert đánh giá chất lượng câu trả lời RAG.

Câu hỏi: {question}
Chính sách/đáp án tham chiếu: {reference}

Answer A:
{answer_a}

Answer B:
{answer_b}

Đánh giá dựa trên 3 tiêu chí: độ chính xác (so với đáp án tham chiếu), độ đầy đủ, tính súc tích.
Trả lời JSON (chỉ JSON, không text khác):
{{"winner": "A" hoặc "B" hoặc "tie", "reasoning": "giải thích ngắn gọn", "scores": {{"A": 0.0-1.0, "B": 0.0-1.0}}}}
"""

    from openai import OpenAI
    client = OpenAI()
    resp = client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[
            {"role": "system", "content": "Bạn là expert đánh giá RAG. Chỉ trả lời JSON hợp lệ."},
            {
                "role": "user",
                "content": prompt_template.format(
                    question=question,
                    answer_a=answer_a,
                    answer_b=answer_b,
                    reference=reference,
                ),
            },
        ],
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    return {
        "winner": data["winner"],
        "reasoning": str(data["reasoning"]),
        "scores": {
            "A": float(data["scores"]["A"]),
            "B": float(data["scores"]["B"]),
        },
    }


# ─── Task 6: Swap-and-Average ─────────────────────────────────────────────────

def swap_and_average(question: str, answer_a: str, answer_b: str, reference: str = "") -> JudgeResult:
    """Task 6: Chạy pairwise 2 lần (hoán đổi thứ tự), lấy kết quả nhất quán.

    Lý do: LLM thường có position bias (ưu tiên answer xuất hiện trước).
    Bằng cách swap, ta phát hiện và giảm bias này.

    Logic:
        Pass 1: judge(q, A, B) → winner_1 (trong không gian A/B)
        Pass 2: judge(q, B, A) → winner_2_raw (trong không gian B/A)
        Convert: nếu winner_2_raw="A" thì thực ra là B (vì đã swap)
        Final:   nếu winner_1 == winner_2 → final = winner_1
                 nếu khác nhau → final = "tie"
    """
    pass1 = pairwise_judge(question, answer_a, answer_b, reference=reference)
    pass2_raw = pairwise_judge(question, answer_b, answer_a, reference=reference)

    swap_map = {"A": "B", "B": "A", "tie": "tie"}
    winner_pass2 = swap_map[pass2_raw["winner"]]

    position_consistent = (pass1["winner"] == winner_pass2)
    final = pass1["winner"] if position_consistent else "tie"

    return JudgeResult(
        question=question,
        answer_a=answer_a,
        answer_b=answer_b,
        winner_pass1=pass1["winner"],
        winner_pass2=winner_pass2,
        final_winner=final,
        reasoning_pass1=pass1["reasoning"],
        reasoning_pass2=pass2_raw["reasoning"],
        position_consistent=position_consistent,
        scores_pass1=pass1["scores"],
        scores_pass2={"A": pass2_raw["scores"]["B"], "B": pass2_raw["scores"]["A"]},
    )


# ─── Task 7: Cohen's κ ────────────────────────────────────────────────────────

def cohen_kappa(judge_labels: list[int], human_labels: list[int]) -> float:
    """Task 7: Tính Cohen's κ giữa LLM judge và human labels.

    Args:
        judge_labels:  nhãn từ LLM judge (0 = bad answer, 1 = good answer)
        human_labels:  nhãn từ human_labels_10q.json

    Returns:
        κ ∈ [-1, 1]
        Thang đo Landis-Koch: <0=poor, 0-0.2=slight, 0.2-0.4=fair,
                               0.4-0.6=moderate, 0.6-0.8=substantial, 0.8-1=almost perfect
    """
    n = len(judge_labels)
    if n == 0 or n != len(human_labels):
        raise ValueError("judge_labels and human_labels must be non-empty lists of equal length")
    p_o = sum(j == h for j, h in zip(judge_labels, human_labels)) / n
    p_e = (
        (judge_labels.count(1) / n) * (human_labels.count(1) / n)
        + (judge_labels.count(0) / n) * (human_labels.count(0) / n)
    )
    return (p_o - p_e) / (1 - p_e) if p_e != 1 else (1.0 if p_o == 1.0 else 0.0)


# ─── Task 8: Bias Report ──────────────────────────────────────────────────────

def bias_report(judge_results: list[JudgeResult]) -> dict:
    """Task 8: Đo lường position bias và verbosity bias.

    Position bias: LLM chọn answer theo vị trí (A hay B) thay vì chất lượng.
        → Đo bằng % cases where position_consistent = False

    Verbosity bias: LLM ưu tiên answer dài hơn dù không chính xác hơn.
        → Đo bằng: trong các case A thắng, A có dài hơn B không? Tương tự cho B.

    Returns:
        {
          "total_judged": int,
          "position_bias_rate": float,        # 0-1, cao = bias nhiều
          "position_bias_count": int,
          "verbosity_bias": float,            # 0-1, > 0.6 = đáng lo ngại
          "verbosity_details": {
            "a_wins_a_longer": int,           # A thắng VÀ A dài hơn
            "b_wins_b_longer": int,           # B thắng VÀ B dài hơn
            "total_decisive": int,            # tổng case có winner rõ ràng
          },
          "interpretation": str,
        }
    """
    total = len(judge_results)
    if total == 0:
        return {
            "total_judged": 0,
            "position_bias_rate": 0.0,
            "position_bias_count": 0,
            "verbosity_bias": 0.0,
            "verbosity_details": {
                "a_wins_a_longer": 0,
                "b_wins_b_longer": 0,
                "total_decisive": 0,
            },
            "interpretation": "Không có cặp câu trả lời nào được đánh giá.",
        }

    position_bias_count = sum(1 for r in judge_results if not r.position_consistent)
    position_bias_rate = round(position_bias_count / total, 3)

    a_wins_a_longer = sum(
        1 for r in judge_results
        if r.final_winner == "A" and len(r.answer_a) > len(r.answer_b)
    )
    b_wins_b_longer = sum(
        1 for r in judge_results
        if r.final_winner == "B" and len(r.answer_b) > len(r.answer_a)
    )
    decisive = sum(1 for r in judge_results if r.final_winner != "tie")
    verbosity_bias = round((a_wins_a_longer + b_wins_b_longer) / decisive, 3) if decisive > 0 else 0.0

    interpretation = (
        "Position bias cao — nên dùng swap-and-average."
        if position_bias_rate > 0.3
        else "Position bias thấp — judge ổn định."
    )
    return {
        "total_judged": total,
        "position_bias_rate": position_bias_rate,
        "position_bias_count": position_bias_count,
        "verbosity_bias": verbosity_bias,
        "verbosity_details": {
            "a_wins_a_longer": a_wins_a_longer,
            "b_wins_b_longer": b_wins_b_longer,
            "total_decisive": decisive,
        },
        "interpretation": interpretation,
    }


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from scripts.run_experiments import main
    raise SystemExit(main(["--phase", "b", *sys.argv[1:]]))
