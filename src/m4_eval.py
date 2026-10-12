from __future__ import annotations

"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os, sys, json
import math
from copy import deepcopy
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
from dataclasses import asdict, dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH, OPENAI_API_KEY, OPENAI_BASE_URL, EVALUATOR_MODEL, EMBEDDING_MODEL


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    """Evaluate four metrics with real evaluator metadata; fail on invalid results."""
    metric_names = ("faithfulness", "answer_relevancy", "context_precision", "context_recall")
    if not questions or not (len(questions) == len(answers) == len(contexts) == len(ground_truths)):
        raise ValueError("RAGAS inputs must be non-empty lists of equal length")

    from ragas import evaluate
    from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
    from datasets import Dataset
    from langchain_openai import ChatOpenAI
    from ragas.embeddings import HuggingfaceEmbeddings

    dataset = Dataset.from_dict({
        "question": questions, "answer": answers,
        "contexts": contexts, "ground_truth": ground_truths,
    })
    llm = ChatOpenAI(model=EVALUATOR_MODEL, api_key=OPENAI_API_KEY,
                     base_url=OPENAI_BASE_URL, temperature=0)
    embeddings = HuggingfaceEmbeddings(model_name=EMBEDDING_MODEL)
    # Isolate metric instances so a previous evaluation cannot supply stale models.
    metrics = deepcopy([faithfulness, answer_relevancy, context_precision, context_recall])
    result = evaluate(dataset, metrics=metrics, llm=llm, embeddings=embeddings,
                      raise_exceptions=True)
    df = result.to_pandas()
    if len(df) != len(questions):
        raise ValueError("RAGAS returned an unexpected number of rows")

    per_question = []
    for position, (_, row) in enumerate(df.iterrows()):
        if (row["question"] != questions[position] or row["answer"] != answers[position]
                or list(row["contexts"]) != contexts[position]
                or row["ground_truth"] != ground_truths[position]):
            raise ValueError(f"RAGAS source/order mismatch at row {position}")
        scores = {name: float(row[name]) for name in metric_names}
        if any(not math.isfinite(value) or not 0 <= value <= 1 for value in scores.values()):
            raise ValueError(f"RAGAS metrics must be finite values in [0,1] at row {position}")
        per_question.append(EvalResult(
            question=row["question"], answer=row["answer"], contexts=list(row["contexts"]),
            ground_truth=row["ground_truth"], **scores,
        ))

    return {
        **{name: sum(getattr(row, name) for row in per_question) / len(per_question)
           for name in metric_names},
        "per_question": per_question,
        "metadata": {"evaluator_models": list(dict.fromkeys([llm.model_name, embeddings.model_name]))},
    }


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    """Analyze bottom-N worst questions using Diagnostic Tree."""
    if bottom_n <= 0:
        return []
    diagnostic_tree = {
        "faithfulness": ("LLM hallucinating", "Tighten prompt, lower temperature"),
        "context_recall": ("Missing relevant chunks", "Improve chunking or add BM25"),
        "context_precision": ("Too many irrelevant chunks", "Add reranking or metadata filter"),
        "answer_relevancy": ("Answer doesn't match question", "Improve prompt template"),
    }
    failures = []
    for result in eval_results:
        scores = {name: getattr(result, name) for name in diagnostic_tree}
        worst_metric = min(scores, key=scores.get)
        diagnosis, suggested_fix = diagnostic_tree[worst_metric]
        failures.append({"question": result.question, "worst_metric": worst_metric,
                         "score": scores[worst_metric], "avg_score": sum(scores.values()) / len(scores),
                         "diagnosis": diagnosis, "suggested_fix": suggested_fix})
    return sorted(failures, key=lambda failure: failure["avg_score"])[:bottom_n]


def save_report(results: dict, failures: list[dict], path: str = "reports/ragas_report.json"):
    """Save aggregate scores, full per-question evidence, and failures to JSON."""
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "per_question": [asdict(result) for result in results.get("per_question", [])],
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
