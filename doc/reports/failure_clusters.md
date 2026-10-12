# Phân tích lỗi Phase A

Nhóm: Sodeep

Người phụ trách: Trần Gia Thành - 2A202602626

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T05:17:33.438949+00:00.
Generation mode/fallback và điều kiện chạy: metadata ghi `run_kind=live`; `artifacts/answers_50q.json` có 50/50 bản ghi `generation_mode=llm`, `generation_model=gpt-6-luna`.
Models generation/evaluator: generation `gpt-6-luna`; evaluator `BAAI/bge-m3`, `gpt-6-luna` (theo `metadata.models`).

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9500 | 0.6597 | 0.8000 |
| answer_relevancy | 0.9180 | 0.7950 | 0.7928 |
| context_precision | 0.9750 | 0.7792 | 0.9000 |
| context_recall | 0.8250 | 0.6792 | 0.3917 |
| avg_score | 0.9170 | 0.7283 | 0.7211 |

Các điểm trong bảng được làm tròn 4 chữ số thập phân từ `per_distribution`.

## Bottom 10 và nguyên nhân

| Rank | ID | Question | Distribution | Avg score | Worst metric | Diagnosis | Suggested fix |
|---|---:|---|---|---:|---|---|---|
| 1 | 44 | Bao lâu phải đổi mật khẩu một lần? | adversarial | 0.2917 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 2 | 35 | Nhân viên Junior P1 có lương cơ bản 12 triệu vừa vào thử việc: nhận lương bao nhiêu và phụ cấp gì tháng đầu tiên? | multi_hop | 0.4759 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 3 | 50 | Nhân viên Manager có thể dùng VPN cá nhân (như NordVPN) khi WFH để tăng bảo mật thêm không? | adversarial | 0.5357 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 4 | 39 | So sánh yêu cầu mật khẩu giữa policy v1.0 và v2.0 về độ dài tối thiểu, thời hạn đổi và MFA. | multi_hop | 0.5358 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 5 | 25 | Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu? | multi_hop | 0.5402 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 6 | 42 | Thâm niên bao nhiêu năm thì được cộng thêm ngày phép? | adversarial | 0.5850 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 7 | 27 | Nhân viên có thâm niên 7 năm theo v2024 được nghỉ bao nhiêu ngày phép? Nếu bị trừ thêm 4 ngày ốm không có giấy y tế thì còn lại bao nhiêu? | multi_hop | 0.6203 | faithfulness | LLM hallucinating | Tighten system prompt, lower temperature |
| 8 | 37 | Nhân viên tự ý xóa malware khỏi máy và chia sẻ thông tin sự cố này trên Slack nội bộ. Vi phạm những chính sách nào cụ thể? | multi_hop | 0.6537 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 9 | 24 | Nhân viên tạm ứng 15 triệu, sau 20 ngày mới thanh toán. Bị phạt bao nhiêu? | multi_hop | 0.6667 | answer_relevancy | Answer doesn't match question | Improve prompt template |
| 10 | 40 | Nhân viên cấp Manager có thời hạn thử việc 90 ngày, đang trong tháng thứ 3, phát hiện vi phạm bảo mật. Họ nên và không nên làm gì theo chính sách? | multi_hop | 0.6788 | context_precision | Too many irrelevant chunks | Add reranking or metadata filter |

Các giá trị `diagnosis` và `suggested_fix` ở bảng được giữ nguyên từ `bottom_10`; điểm hiển thị làm tròn 4 chữ số. Đây là nhãn chẩn đoán theo metric thấp nhất, cần đối chiếu nội dung từng câu trước khi kết luận nguyên nhân.

- ID 44: answer là “Không tìm thấy.” dù contexts chứa cả chu kỳ cũ 90 ngày, chu kỳ hiện hành 120 ngày và thông báo v1.0 đã được thay thế. Reference yêu cầu 120 ngày. Đây là lỗi tạo câu trả lời hoặc chọn phiên bản từ bằng chứng đã truy xuất; không phải thiếu con số trong contexts.
- ID 35: answer tính đúng lương thử việc 10,2 triệu nhưng không nêu phụ cấp ăn trưa 1 triệu, không có phụ cấp điện thoại và tổng 11,2 triệu như reference. Contexts chỉ nói phụ cấp ăn trưa áp dụng từ ngày đầu, không có mức tiền; phần thiếu này phù hợp với `context_recall=0.25`.
- ID 39: answer có độ dài 8/12 ký tự và chu kỳ v2.0 120 ngày, nhưng nói không tìm thấy chu kỳ v1.0 và không nêu MFA bắt buộc. Reference có v1.0 đổi mỗi 90 ngày và v2.0 bắt buộc MFA; ba contexts hiện tại không chứa hai thông tin này. Đây là thiếu bằng chứng để so sánh đầy đủ hai phiên bản.
- ID 25 và 27: ID 25 trả 14 triệu thay vì 17 triệu dù contexts có trần lương Junior 20 triệu và tỷ lệ thử việc 85%; lỗi nằm ở suy luận/tính toán câu trả lời. ID 27 trả 13 ngày rồi còn 9, trong khi reference v2024 là 15 + 2 = 17 rồi còn 13; contexts trộn quy tắc thâm niên cũ 5 năm với quy tắc mới 3 năm và thiếu đoạn nêu 15 ngày cơ bản. Cần xử lý đồng thời chọn phiên bản và truy xuất đủ dữ kiện.
- ID 24: contexts đã có hạn 15 ngày, phí 2%/tháng và công thức pro-rata 30 ngày, nhưng answer vẫn nói không tính được. Reference tính 5 ngày quá hạn trên 15 triệu, khoảng 50.000 VNĐ. Đây là lỗi tổng hợp/tính toán từ dữ kiện đã có, phù hợp với `answer_relevancy=0` hơn là thiếu tài liệu.
- ID 40: answer nêu đúng kênh và hạn báo cáo 1 giờ, không tự xử lý, nhưng chưa nêu không xóa dấu vết và không chia sẻ rộng rãi như reference. Một context về lương thử việc 85% ít liên quan đến phần hành động bảo mật; `context_precision=0.5833` là metric thấp nhất của câu này.

## Matrix và nhóm yếu nhất

| Worst metric | factual | multi_hop | adversarial | Tổng |
|---|---:|---:|---:|---:|
| faithfulness | 2 | 8 | 2 | 12 |
| answer_relevancy | 12 | 2 | 0 | 14 |
| context_precision | 1 | 3 | 0 | 4 |
| context_recall | 5 | 7 | 8 | 20 |
| Tổng câu | 20 | 20 | 10 | 50 |

Mỗi câu được đếm đúng một lần theo metric thấp nhất; tổng cột là kích thước nhóm, không phải số câu thất bại.

Nhóm yếu theo mean thấp nhất: adversarial; mean: 0.7211.
Worst metric xuất hiện nhiều nhất: context_recall; số câu: 20/50.

Adversarial thấp hơn multi_hop khoảng 0.0072 điểm và factual khoảng 0.1959. Điểm `context_recall` của adversarial là 0.3917, thấp hơn multi_hop 0.6792 và factual 0.8250; 8/10 câu adversarial có `context_recall` là metric thấp nhất. Các trường hợp ID 44, 42 cho thấy đoạn cũ và hiện hành cùng xuất hiện; ID 50 có đoạn cấm VPN cá nhân nhưng thiếu yêu cầu dùng WireGuard trong reference. Đây là bằng chứng cụ thể để ưu tiên truy xuất đủ chính sách và thông tin phiên bản, không phải kết luận rằng 8 câu đó đều trả lời sai.

Đề xuất kiểm tra: bổ sung metadata phiên bản/hiệu lực khi truy xuất, mở rộng hoặc rerank các chunks cho câu hỏi nhiều dữ kiện và giữ cả hai phiên bản khi câu hỏi yêu cầu so sánh; sau đó yêu cầu câu trả lời bám từng dữ kiện và tính toán tường minh. Chạy lại cùng bộ 50 câu, đối chiếu mean, matrix và từng ID 44/35/39/25/27/24/50 trước và sau sửa. Chưa có lượt chạy sau sửa để khẳng định cải thiện.

## Bẫy adversarial và giới hạn

Trong bottom 10 có 3 câu adversarial (ID 44, 50, 42), 7 câu multi_hop và không có factual. ID 44 là bẫy phiên bản 90 ngày cũ so với 120 ngày hiện hành: answer bỏ lỡ đáp án dù có context đúng. ID 42 có quy tắc thâm niên cũ 5 năm và mới 3 năm; answer chọn 3 năm đúng reference dù `context_recall=0`. ID 50 là bẫy phủ định: câu hỏi gợi ý VPN cá nhân “tăng bảo mật”, nhưng answer vẫn từ chối đúng theo đoạn cấm; reference còn yêu cầu dùng WireGuard, chưa có trong contexts. Vì vậy điểm thấp hoặc `worst_metric` riêng lẻ không đủ để kết luận mô hình đã hoặc chưa xử lý đúng bẫy.

Giới hạn: chỉ có 50 câu (20 factual, 20 multi_hop, 10 adversarial); chênh lệch mean giữa adversarial và multi_hop nhỏ. Metadata ghi generation `gpt-6-luna`, evaluator `gpt-6-luna` và embedding `BAAI/bge-m3`; không có bằng chứng về model khác hay lượt chạy sau sửa. File answers ghi 50 lượt `llm` và 0 fallback. SHA-256 của answers và test set khớp `metadata.source_sha256` sau khi chuẩn hóa ký tự xuống dòng Windows CRLF về LF; hash trực tiếp trên bytes CRLF vẫn khác.
