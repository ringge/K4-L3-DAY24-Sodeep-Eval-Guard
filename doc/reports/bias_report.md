# Đánh giá LLM Judge Phase B

Nhóm: Sodeep

Người phụ trách: Bùi Tiến Cường - 2A202602539

Nguồn: `artifacts/judge_results.json`; run timestamp: `2026-10-12T05:16:36.812714+00:00`.
Models generation/judge: `metadata.models.generation = ["gpt-6-luna"]` và `metadata.models.judge = ["gpt-6-luna"]`.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ `artifacts/answers_50q.json:answer`; B từ `fixtures/human_labels_10q.json:model_answer`; reference từ `fixtures/test_set_50q.json:ground_truth`.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

| ID | Candidate A (`answers_50q.json`) | Candidate B (`human_labels_10q.json`) | `winner_pass1` | `winner_pass2` (quy về A/B gốc) | `final_winner` | `position_consistent` | `scores_pass1` (A / B) | `scores_pass2` (A / B) | `reasoning_pass1` | `reasoning_pass2` (lượt đảo B/A) |
|---:|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc khi kết hôn. (49 ký tự) | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. (58 ký tự) | B | B | B | `true` | 0.8 / 0.9 | 0.7 / 0.9 | B chính xác và đầy đủ hơn vì nêu rõ 3 ngày nghỉ có lương; cả hai đều thiếu thông tin không trừ vào phép năm. | A chính xác và đầy đủ hơn vì nêu rõ 3 ngày nghỉ có lương; cả hai đều thiếu thông tin không trừ vào phép năm. A vẫn súc tích. |
| 5 | Tổng Giám đốc (CEO) phê duyệt. (30 ký tự) | Cần Giám đốc phòng ban phê duyệt. (33 ký tự) | A | A | A | `true` | 1.0 / 0.0 | 1.0 / 0.0 | A đúng theo chính sách: đơn hàng trên 50 triệu đồng cần CEO phê duyệt. B nêu sai người phê duyệt. | B đúng theo chính sách: đơn hàng trên 50 triệu VNĐ cần CEO phê duyệt; A nêu sai người phê duyệt. |
| 12 | Tối thiểu 1 tháng lương. (24 ký tự) | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. (50 ký tự) | A | A | A | `true` | 1.0 / 0.75 | 0.97 / 0.93 | A trả lời chính xác mức tối thiểu và phù hợp với điều kiện từ 6 tháng trở lên. B nêu mức thưởng nhưng thiếu điều kiện này, khiến câu trả lời kém đầy đủ. | Cả hai đều nêu đúng mức tối thiểu là 1 tháng lương. B trả lời trực tiếp và súc tích hơn; điều kiện từ 6 tháng trở lên đã có trong câu hỏi. |
| 21 | Nhân viên 9 năm thâm niên được **18 ngày phép năm có lương** theo quy định cộng thêm 1 ngày cho mỗi 3 năm làm việc liên tục (15 + 3). **Không tìm thấy** thông tin về khoảng lương. (180 ký tự) | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. (82 ký tự) | B | B | B | `true` | 0.7 / 1.0 | 0.6 / 1.0 | B nêu đúng 18 ngày phép và khoảng lương Senior 20–35 triệu đồng/tháng, đầy đủ và súc tích. A đúng về số ngày phép nhưng thiếu thông tin lương. | A nêu chính xác cả 18 ngày phép và khoảng lương Senior 20–35 triệu VNĐ/tháng. B nêu đúng số ngày phép nhưng bỏ sót khoảng lương nên chưa đầy đủ. |
| 41 | Nhân viên chính thức được hưởng 15 ngày phép năm có lương. (58 ký tự) | Nhân viên được nghỉ 12 ngày phép năm. (37 ký tự) | A | A | A | `true` | 0.85 / 0.1 | 0.8 / 0.1 | A đúng mức phép cơ bản theo chính sách v2024 hiện hành, còn B dùng mức 12 ngày của chính sách đã bị thay thế. A chưa nêu thêm 1 ngày mỗi 3 năm thâm niên nên chưa đầy đủ. | B ưu tiên đúng chính sách v2024 với mức cơ bản 15 ngày; tuy nhiên chưa nêu phần tăng thêm 1 ngày mỗi 3 năm thâm niên và giới hạn đối tượng là nhân viên chính thức chưa được nêu trong đáp án tham chiếu. A dùng mức 12 ngày của chính sách v2023 đã bị thay thế. |

Position bias count/rate: `position_bias_count = 0` / `5`, `position_bias_rate = 0.0` (0.0%).
Verbosity win rate: `verbosity_bias = 0.4` (40.0%); decisive cases: `total_decisive = 5` (`a_wins_a_longer = 1`, `b_wins_b_longer = 1`).
Nhận định tự động từ runner (`interpretation`): `"Position bias thấp — judge ổn định."`

### Phân tích chi tiết Position Bias và Verbosity Bias
- **Về tính nhất quán vị trí (Position Consistency):** Cả 5/5 cặp (`question_id`: 1, 5, 12, 21, 41) đều có `position_consistent = true` (`winner_pass1 == winner_pass2` sau khi quy đổi về không gian A/B gốc). Không có trường hợp nào bị lật kết quả khi đảo thứ tự hiển thị `(A, B)` sang `(B, A)`. Tuy nhiên, ở **câu 12**, dù cả hai lượt đều chọn Candidate A (`"Tối thiểu 1 tháng lương."`), lập luận ở lượt 1 của Judge có phần thiếu nhất quán nội tại (nói B thiếu điều kiện 6 tháng dù bản thân A ngắn hơn và cũng không lặp lại điều kiện đó), trong khi lượt 2 giải thích hợp lý hơn rằng A trả lời trực tiếp và súc tích hơn vì điều kiện 6 tháng đã nằm trong câu hỏi.
- **Về Verbosity Win Rate (`0.4` — 2/5 câu thắng dài hơn):**
  - Hai trường hợp câu trả lời dài hơn giành chiến thắng là **câu 1** (B thắng, 58 ký tự > A 49 ký tự) và **câu 41** (A thắng, 58 ký tự > B 37 ký tự). Đọc nội dung thực tế cho thấy ở **câu 1**, B thắng vì bổ sung đúng thuộc tính chính sách quan trọng là `"có lương"`; ở **câu 41**, A thắng vì nêu đúng chính sách v2024 (`15 ngày phép năm`) trong khi B trả lời sai theo chính sách cũ v2023 (`12 ngày`).
  - Ở 3/5 câu còn lại (**câu 5, 12, 21**), câu trả lời **ngắn hơn** lại giành chiến thắng. Đặc biệt ở **câu 21**, Candidate A dài gấp đôi (180 ký tự) nhưng thiếu thông tin khung lương Senior, trong khi Candidate B ngắn gọn (82 ký tự) nhưng trả lời đủ cả 2 vế (18 ngày phép + lương 20–35 triệu) nên thắng tuyệt đối (`1.0` điểm ở cả 2 lượt).
  - Như vậy, tỷ lệ `verbosity_bias = 0.4` phản ánh Judge chấm dựa trên **độ chính xác và độ đầy đủ thông tin đối chiếu với `reference`** chứ không thiên vị câu dài hơn.

## Calibration đúng model_answer

Helper `judge_binary` đánh giá đúng `question` và `model_answer` đang có trong `fixtures/human_labels_10q.json`; không lấy answer mới của pipeline. Prompt chỉ nhận `question`, `answer`, `reference`. Không gửi `human_label`, `human_note` hoặc phân bố nhãn human vào prompt.

| Thứ tự | `question_id` | Câu hỏi | `model_answer` gốc (`human_labels_10q.json`) | `judge_label` | `human_label` | `agree` | `reasoning` của Binary Judge |
|---:|---:|---|---|:---:|:---:|:---:|---|
| 1 | 1 | Nhân viên được nghỉ bao nhiêu ngày khi kết hôn? | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | 1 | `true` | Trả lời đúng nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn; việc không trừ vào phép năm không cần thiết để trả lời câu hỏi về số ngày nghỉ. |
| 2 | 5 | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | Cần Giám đốc phòng ban phê duyệt. | 0 | 0 | `true` | Thiết bị trị giá 55 triệu vượt ngưỡng 50 triệu nên cần Tổng Giám đốc (CEO) phê duyệt, không phải Giám đốc phòng ban. |
| 3 | 12 | Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là bao nhiêu? | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | 1 | `true` | Đáp án nêu đúng mức thưởng Tết tối thiểu là 1 tháng lương cho đối tượng được hỏi. |
| 4 | 21 | Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào? | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | 1 | `true` | Nêu đúng 18 ngày phép và khoảng lương Senior 20–35 triệu đồng/tháng theo chính sách v2024. |
| 5 | 23 | Nhân viên được tài trợ khóa học 25 triệu, nghỉ việc sau 8 tháng. Phải hoàn trả bao nhiêu? | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | 1 | `true` | Nghỉ sau 8 tháng, chưa đủ cam kết 1 năm nên phải hoàn trả 100% chi phí, tức 25 triệu. |
| 6 | 29 | Nhân viên tạm ứng 8 triệu, chưa thanh toán sau 30 ngày. Ai phê duyệt và phí phạt là bao nhiêu? | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | 0 | `true` | Thiếu Kế toán trưởng trong các cấp phê duyệt cần thiết; phí phạt theo reference là 80.000 VNĐ, không phải 2% của cả tháng trên 8 triệu. |
| 7 | 33 | Nhân viên Manager có thâm niên 12 năm: tổng phụ cấp hàng tháng và số ngày phép năm? | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | 1 | `true` | Phụ cấp Manager tổng cộng 1.500.000 VNĐ/tháng và phép năm là 19 ngày, đúng theo reference. |
| 8 | 41 | Nhân viên được nghỉ bao nhiêu ngày phép năm? | Nhân viên được nghỉ 12 ngày phép năm. | 0 | 0 | `true` | Câu trả lời dùng mức 12 ngày của chính sách v2023 đã bị thay thế; chính sách hiện hành v2024 quy định 15 ngày cơ bản, cộng thêm 1 ngày mỗi 3 năm thâm niên. |
| 9 | 46 | Nhân viên thử việc có được nghỉ phép năm không? | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 0 | 1 | `false` | Đúng là nhân viên thử việc không được nghỉ phép năm, nhưng câu trả lời thiếu điều kiện nghỉ không lương phải được trưởng phòng phê duyệt. |
| 10 | 50 | Nhân viên Manager có thể dùng VPN cá nhân (NordVPN) khi WFH không? | Được, miễn là đảm bảo kết nối an toàn. | 0 | 0 | `true` | Sai: chính sách cấm VPN cá nhân như NordVPN trong mạng công ty và yêu cầu dùng VPN WireGuard của công ty. |

Cohen’s κ: `0.8`.
Observed/chance agreement và diễn giải:
- Mảng nhãn thực tế: `judge_labels = [1, 0, 1, 1, 1, 0, 1, 0, 0, 0]` (5 nhãn `1`, 5 nhãn `0`); `human_labels = [1, 0, 1, 1, 1, 0, 1, 0, 1, 0]` (6 nhãn `1`, 4 nhãn `0`).
- **Observed agreement ($p_o$):** Đồng thuận trên 9/10 câu $\Rightarrow p_o = 9 / 10 = 0.90$.
- **Chance agreement ($p_e$):**
  $$p_e = P(\text{judge}=1)\cdot P(\text{human}=1) + P(\text{judge}=0)\cdot P(\text{human}=0) = (0.5 \times 0.6) + (0.5 \times 0.4) = 0.30 + 0.20 = 0.50$$
- **Hệ số Cohen's $\kappa$:**
  $$\kappa = \frac{p_o - p_e}{1 - p_e} = \frac{0.90 - 0.50}{1 - 0.50} = \frac{0.40}{0.50} = 0.80$$
- **Diễn giải theo thang Landis-Koch:** $\kappa = 0.80$ nằm ở ranh giới giữa mức **Substantial agreement** ($0.6 - 0.8$) và **Almost perfect agreement** ($0.8 - 1.0$), vượt ngưỡng mục tiêu $> 0.6$ của bài lab, cho thấy LLM Judge có độ đồng thuận cao với người đánh giá trên tập câu hỏi chính sách này.

## Giới hạn và cách dùng judge

- **Phân tích trường hợp bất đồng duy nhất (`question_id = 46`):**
  - Câu hỏi: *"Nhân viên thử việc có được nghỉ phép năm không?"*
  - `ground_truth`: *"KHÔNG. Nhân viên trong thời gian thử việc không được hưởng phép năm. Nếu cần nghỉ, phải xin nghỉ không lương và được trưởng phòng phê duyệt."*
  - `model_answer`: *"Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần."*
  - **Nguyên nhân lệch nhãn:** Người đánh giá (`human_label = 1`) chấp nhận câu trả lời vì đã trả lời đúng trực tiếp câu hỏi Có/Không và nêu được hướng xin nghỉ không lương. Trong khi đó, `BINARY_SYSTEM_PROMPT` yêu cầu nghiêm ngặt *"không bỏ qua phủ định hoặc điều kiện quan trọng"*, nên `gpt-6-luna` (`judge_label = 0`) trừ điểm vì thiếu điều kiện *"phải được trưởng phòng phê duyệt"* có trong `ground_truth`. Điều này cho thấy LLM Judge bám rất sát từng mệnh đề điều kiện trong `reference`, đôi khi khắt khe hơn con người đối với các thông tin bổ trợ không nằm trực tiếp trong câu hỏi.
- **Giới hạn của thực nghiệm:**
  - **Cỡ mẫu nhỏ:** Tập Pairwise chỉ gồm 5 cặp câu hỏi (10 lượt gọi API) và tập Calibration nhị phân chỉ gồm 10 câu hỏi. Với $n = 10$, chỉ cần thay đổi nhãn của 1 câu sẽ làm $\kappa$ biến động khoảng $\pm 0.20$. Do đó, $\kappa = 0.80$ và `position_bias_rate = 0.0` là tín hiệu tích cực nhưng chưa đủ để khẳng định Judge hoàn toàn không có thiên lệch trên quy mô lớn.
  - **Cùng họ mô hình (`gpt-6-luna`):** Cả `generation_model` (sinh Candidate A) và `judge_model` đều dùng `gpt-6-luna`, có nguy cơ tồn tại *self-enhancement bias* (mô hình ưa thích văn phong của chính nó).
- **Khuyến nghị sử dụng LLM-as-Judge trong thực tế:**
  1. **Không coi LLM Judge là đáp án tuyệt đối:** Luôn kết hợp `swap_and_average` (chấm 2 chiều A/B và B/A, gán `"tie"` khi bất đồng) để triệt tiêu thiên lệch vị trí trước khi đưa vào báo cáo.
  2. **Tách biệt mục đích sử dụng:** Dùng Pairwise A/B/tie khi so sánh hai phiên bản pipeline (ví dụ nâng cấp chunking/prompt), và dùng Binary 0/1 có đối chiếu `reference` khi đo tỷ lệ pass/fail tuyệt đối.
  3. **Kiểm định định kỳ với Human-in-the-loop:** Lấy mẫu ngẫu nhiên các câu có bất đồng giữa 2 lượt đảo vị trí hoặc các câu bị Judge đánh rớt do điều kiện phụ (như câu 46) để con người rà soát và tinh chỉnh rubric trong prompt chấm điểm.
