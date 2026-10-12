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
| 1 | Trần Kim Phương | 2A202602565 | {{Phase/file/hàm}} | {{Commit/PR/report}} artifact `artifacts/ragas_50q.json`|
| 2 | Trần Gia Thành | 2A202602626 | Phụ trách Phase A (RAGAS): hoàn thiện Tasks 1–4 trong `src/phase_a_ragas.py` — đánh giá 50 câu hỏi bằng 4 chỉ số RAGAS, chọn bottom 10, phân tích ma trận `worst_metric` và các nhóm yếu theo điểm trung bình; lập báo cáo phân cụm lỗi tại `doc/reports/failure_clusters.md`. | Commits `f6a0cd7`, `cc16d08`; báo cáo `doc/reports/failure_clusters.md` |
| 3 | Bùi Tiến Cường | 2A202602539 | Phụ trách Phase B (LLM-as-Judge): hiện thực hóa các hàm đánh giá cặp và kiểm định độ tin cậy (`pairwise_judge`, `swap_and_average`, `cohen_kappa`, `bias_report`) tại `src/phase_b_judge.py`; vận hành thực nghiệm trực tuyến tạo `artifacts/judge_results.json`; biên soạn báo cáo phân tích thiên lệch và hiệu chuẩn tại `doc/reports/bias_report.md` | Commits `9ff7407`, `7311762`; artifact `artifacts/judge_results.json`; báo cáo `doc/reports/bias_report.md` |
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

### BuiTienCuong-2A202602539

- Phần được giao và phần thực tế đã làm: Đảm nhận toàn bộ quy trình nghiên cứu, hiện thực hóa mã nguồn và phân tích thực nghiệm cho **Phase B (LLM-as-Judge)**. Cụ thể, đã xây dựng bốn hàm cốt lõi trong `src/phase_b_judge.py`: (1) `pairwise_judge` (Task 5) thực hiện đánh giá so sánh cặp câu trả lời A/B có neo theo văn bản tham chiếu (`reference`) và trả về cấu trúc JSON định lượng; (2) `swap_and_average` (Task 6) thiết lập cơ chế thẩm định hai chiều `(A, B)` và `(B, A)` nhằm phát hiện và triệt tiêu thiên lệch vị trí (*position bias*), chỉ công nhận kết quả thắng cuộc khi hai lượt đánh giá đạt đồng thuận; (3) `cohen_kappa` (Task 7) tính toán hệ số đồng thuận thống kê $\kappa$ giữa bộ giám khảo LLM và nhãn chuẩn của chuyên gia con người; và (4) `bias_report` (Task 8) định lượng tỷ lệ bất nhất vị trí (`position_bias_rate`) cùng thiên lệch độ dài (`verbosity_bias`). Đồng thời, trực tiếp thực thi thực nghiệm trực tuyến tạo tập bằng chứng `artifacts/judge_results.json` và biên soạn báo cáo học thuật tại `doc/reports/bias_report.md`.
- Bằng chứng: Mã nguồn hoàn chỉnh tại `src/phase_b_judge.py` và dữ liệu thực nghiệm `artifacts/judge_results.json` (commit `9ff7407` — `"done Phase B"`); báo cáo phân tích chuyên sâu tại `doc/reports/bias_report.md` (commit `7311762` — `"docs: fill Phase B bias_report.md from live judge_results.json"`).
- Cách kiểm tra: (1) Kiểm thử đơn vị ngoại tuyến (offline mock unit tests) thông qua lệnh `python -m pytest tests/test_phase_b.py tests/test_support.py -q`, đạt kết quả `38 passed` (trong đó `8/8` bài kiểm thử thuộc `test_phase_b.py` đạt tuyệt đối); (2) Chạy thực nghiệm trực tuyến với mô hình `gpt-6-luna` qua lệnh `python scripts/run_experiments.py --phase b --live` (20 lượt gọi API gồm 10 lượt so sánh cặp trên các câu hỏi ID `1, 5, 12, 21, 41` và 10 lượt chấm điểm nhị phân hiệu chuẩn trên đúng `model_answer` gốc), ghi nhận `position_bias_rate = 0.0`, `verbosity_bias = 0.4` và hệ số đồng thuận $\kappa = 0.80$ ($p_o = 0.90, p_e = 0.50$); (3) Xác thực hợp đồng dữ liệu và lược đồ JSON bằng `python scripts/check_lab.py`, đạt trạng thái `PASS` cho cả ba hạng mục `phase_b_judge.py`, `Phase B artifact` và `doc/reports/bias_report.md`.
- Điều đã học: Nắm vững sự khác biệt bản chất phương pháp luận giữa đánh giá so sánh tương đối (*pairwise comparison* A/B/tie nhằm xếp hạng hai phiên bản hệ thống) và đánh giá hiệu chuẩn nhị phân tuyệt đối (*binary calibration* 0/1 đối chiếu một câu trả lời cố định với `reference`). Hiểu rõ cách vận dụng kỹ thuật hoán đổi thứ tự (*swap-and-average*) để kiểm soát thiên lệch vị trí của LLM, cũng như cách phân biệt giữa tương quan thống kê về độ dài câu trả lời (`verbosity_bias = 0.4`) với nguyên nhân nội dung thực chất (câu trả lời dài hơn giành phần thắng nhờ bao quát đầy đủ các điều kiện chính sách như nghỉ có lương hoặc đúng phiên bản v2024).
- Giới hạn/cách xử lý: (1) Mô hình `gpt-6-luna` trên hạ tầng thực nghiệm không hỗ trợ tham số `temperature=0` (trả về lỗi HTTP 400 `unsupported_value`), do đó đã thiết kế tầng kiểm soát tương thích ngay trong `src/phase_b_judge.py` để tự động lược bỏ `temperature=0` đối với dòng mô hình `luna` đồng thời giám sát chặt chẽ hạn mức chi phí API dưới ngưỡng `$0.10` (chi phí thực tế chỉ tiêu tốn `~$0.01376` cho 20 lời gọi); (2) Cỡ mẫu thực nghiệm còn nhỏ ($n = 5$ cặp so sánh và $n = 10$ mẫu hiệu chuẩn) và xuất hiện một trường hợp lệch nhãn tại `question_id = 46` do LLM Judge áp dụng tiêu chí điều kiện phụ (*"phải được trưởng phòng phê duyệt"*) khắt khe hơn người đánh giá — vấn đề này đã được phân tích minh bạch trong `doc/reports/bias_report.md` kèm khuyến nghị kết hợp cơ chế *Human-in-the-loop*.
- Nguồn/AI hỗ trợ nếu có: Sử dụng công cụ trợ lý lập trình AI (Antigravity) để hỗ trợ rà soát hợp đồng giao diện (`src/report_contracts.py`, `doc/schemas/phase_b.schema.json`), thiết lập cơ chế kiểm soát ngân sách API và định dạng bảng biểu Markdown; toàn bộ logic thuật toán, kết quả gọi API trực tuyến và lập luận đối chiếu từng câu trả lời đều được kiểm chứng độc lập thông qua `pytest` và `scripts/check_lab.py`.

### TranGiaThanh-2A202602626

- Phần được giao và phần thực tế đã làm: Phase A, hoàn thiện Tasks 1–4 trong `src/phase_a_ragas.py` (nhóm 50 câu, nối evaluator m4, chọn bottom 10, phân tích ma trận worst_metric và nhóm yếu theo mean); điền `doc/reports/failure_clusters.md` từ kết quả RAGAS và đối chiếu các câu tiêu biểu với answer, contexts, reference.
- Bằng chứng: commit `f6a0cd7` cho `src/phase_a_ragas.py`, commit `cc16d08` cho `doc/reports/failure_clusters.md`; dữ liệu phân tích ở `artifacts/ragas_50q.json`.
- Cách kiểm tra: đối chiếu `artifacts/ragas_50q.json` với nguồn: 50 per_question, đủ bốn metric/câu, 20 factual/20 multi_hop/10 adversarial, 10 bottom rows theo thứ tự và matrix có tổng cột 20/20/10.
- Điều đã học: số câu 20/20/10 là kích thước nhóm, không phải mức chất lượng; nhóm yếu nhất phải chọn theo mean thấp nhất. Metric thấp nhất chỉ định hướng chẩn đoán, còn nguyên nhân cần đọc answer, contexts và reference; model generation và evaluator phải ghi tách vai trò.
- Giới hạn/cách xử lý: nhóm adversarial có 10 câu và mean 0.7211 chỉ thấp hơn multi_hop 0.7283 khoảng 0.0072; báo cáo phân tích từng ID thay vì coi chênh lệch nhỏ là kết luận chắc chắn. Hash bytes của hai file nguồn hiện tại khác metadata do xuống dòng CRLF trên Windows; sau khi chuẩn hóa về LF, cả hai hash khớp artifact.
- Nguồn/AI hỗ trợ nếu có: Codex hỗ trợ triển khai Tasks 1–4, điền báo cáo và rà soát số liệu; kiểm tra lại bằng mã nguồn, `ragas_50q.json`, `answers_50q.json` và các trường hợp bottom 10.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
