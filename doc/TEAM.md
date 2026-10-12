# Nhóm thực hiện K4 Track 3A

Tên nhóm: Sodeep

Repo chung: https://github.com/ringge/K4-L3-DAY24-Sodeep-Eval-Guard

Trưởng nhóm/người nộp: Trần Kim Phương - 2A202602565

Ngày lab/deadline áp dụng: 23h59 Oct 12, 2026 — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Trần Kim Phương | 2A202602565 | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 2 | Trần Gia Thành | 2A202602626 | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 3 | Bùi Tiến Cường | 2A202602539 | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 4 | Đinh Kim Thái | 2A202602417 | {{Phase/file/hàm}} | {{Commit/PR/report}} |

Người tích hợp/chạy batch/nộp link: {{Họ tên, công việc và bằng chứng}}.

## Môi trường và chuẩn bị trước lớp

- **OS/Python/compiler:** máy kiểm tra chạy macOS 15.7.9 (build 24G830),
  Darwin 24.6.0, kiến trúc arm64; Python 3.11.16; Apple clang 17.0.0
  (`clang-1700.0.13.5`), Command Line Tools tại `/Library/Developer/CommandLineTools`.
  Xác nhận bằng `sw_vers`, `uname -sr`, `uname -m`, `python --version`
  và `clang --version`.
- **Virtualenv/dependencies/imports:** sử dụng `.venv/bin/python`; `sys.prefix`
  trỏ vào `.venv` và khác `sys.base_prefix`, xác nhận đang chạy trong virtualenv.
  `python -m pip check` báo `No module named pip`; kiểm tra thay thế bằng
  `uv pip check --python .venv/bin/python` cho kết quả `Checked 155 packages`
  và `All installed packages are compatible`.
  Các phiên bản đã cài gồm RAGAS 0.1.22, NeMo Guardrails 0.10.0, Annoy 1.17.3,
  LangChain 0.2.17, langchain-core 0.2.43, langchain-community 0.2.19,
  langchain-openai 0.1.25, OpenAI SDK 1.109.1, NumPy 1.26.4, PyArrow 19.0.1,
  sentence-transformers 5.7.0, qdrant-client 1.9.2, spaCy 3.8.16,
  presidio-analyzer và presidio-anonymizer 2.2.364.
  Import thực tế `ragas`, `nemoguardrails`, `presidio_analyzer`,
  `presidio_anonymizer`, `spacy`, `sentence_transformers`, `qdrant_client`
  và `annoy` đều thành công.
- **Models:** cache Hugging Face đã có config, tokenizer và weights của
  `BAAI/bge-m3` (`pytorch_model.bin`) và `BAAI/bge-reranker-v2-m3`
  (`model.safetensors`); kiểm tra bằng `huggingface_hub.try_to_load_from_cache`.
  Đây là bằng chứng cache, không khẳng định đã chạy inference trong lần kiểm tra này.
  Cấu hình generation/enrichment/evaluator/judge hiện tại đều là `gpt-6-luna`.
  `spacy.load("en_core_web_lg")` còn lỗi `[E050] Can't find model 'en_core_web_lg'`;
  cần tải model này trước khi chạy Presidio đầy đủ.
- **Qdrant:** `docker compose -f infra/docker-compose.yml ps` xác nhận container
  `infra-qdrant-1` đang chạy image `qdrant/qdrant:v1.9.7`, mở cổng 6333/6334.
  `curl -fsS http://localhost:6333/` trả phiên bản 1.9.7;
  `curl -fsS http://localhost:6333/collections/lab24_production` trả trạng thái
  `green`, `optimizer_status=ok`, 112 points, vector 1024 chiều, distance `Cosine`.
- **50 answers:** đã có `artifacts/answers_50q.json` theo luồng chuẩn bị
  `python scripts/setup_answers.py --live`. Kiểm tra trực tiếp bằng
  `src.report_contracts.validate_answers` với `fixtures/test_set_50q.json`
  thành công: 50 bản ghi (20 factual, 20 multi_hop, 10 adversarial), mỗi bản ghi
  có 3 contexts; cả 50 ghi `generation_mode=llm`, `generation_model=gpt-6-luna`,
  không có bản ghi `extractive_fallback`. Lần kiểm tra này chỉ xác thực artifact
  hiện có, không sinh lại answers hay gọi API có phí. Nếu generation lỗi, setup
  dùng context đầu tiên làm extractive fallback và ghi model là `null`;
  không dùng ground truth thay answer.
- **Giới hạn full NeMo/runtime:** import NeMo và
  `RailsConfig.from_path("guardrails")` thành công.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### TranGiaThanh - 2A202602626

- Phần được giao và phần thực tế đã làm: Phase A, hoàn thiện Tasks 1–4 trong `src/phase_a_ragas.py` (nhóm 50 câu, nối evaluator m4, chọn bottom 10, phân tích ma trận worst_metric và nhóm yếu theo mean); điền `doc/reports/failure_clusters.md` từ kết quả RAGAS và đối chiếu các câu tiêu biểu với answer, contexts, reference.
- Bằng chứng: commit `f6a0cd7` cho `src/phase_a_ragas.py`, commit `cc16d08` cho `doc/reports/failure_clusters.md`; dữ liệu phân tích ở `artifacts/ragas_50q.json`.
- Cách kiểm tra: đối chiếu `artifacts/ragas_50q.json` với nguồn: 50 per_question, đủ bốn metric/câu, 20 factual/20 multi_hop/10 adversarial, 10 bottom rows theo thứ tự và matrix có tổng cột 20/20/10. Artifact ghi `run_kind=live`; chưa có bằng chứng trong phần việc này về kết quả lệnh `python -m pytest tests/test_phase_a.py`.
- Điều đã học: số câu 20/20/10 là kích thước nhóm, không phải mức chất lượng; nhóm yếu nhất phải chọn theo mean thấp nhất. Metric thấp nhất chỉ định hướng chẩn đoán, còn nguyên nhân cần đọc answer, contexts và reference; model generation và evaluator phải ghi tách vai trò.
- Giới hạn/cách xử lý: nhóm adversarial có 10 câu và mean 0.7211 chỉ thấp hơn multi_hop 0.7283 khoảng 0.0072; báo cáo phân tích từng ID thay vì coi chênh lệch nhỏ là kết luận chắc chắn. Hash bytes của hai file nguồn hiện tại khác metadata do xuống dòng CRLF trên Windows; sau khi chuẩn hóa về LF, cả hai hash khớp artifact.
- Nguồn/AI hỗ trợ nếu có: Codex hỗ trợ triển khai Tasks 1–4, điền báo cáo và rà soát số liệu; kiểm tra lại bằng mã nguồn, `ragas_50q.json`, `answers_50q.json` và các trường hợp bottom 10.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
