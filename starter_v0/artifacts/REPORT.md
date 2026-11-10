# Day 03 Lab v2 Report — Research Agent

## Team
- Team / Members: Nguyễn Minh Khôi (2A202603528), Võ Công Minh, Nguyễn Đắc Tuấn Nghĩa (2A202603442), Nguyễn Ngọc Hiếu (2A202603502).
- Provider/model baseline: OpenRouter / `openai/gpt-4o-mini`.

# PHẦN A — Giới thiệu agent

## A1. Khả năng
Research Agent tìm tin trên web và mạng xã hội, xem bài đăng theo tài khoản, đọc URL và paper arXiv, tra cứu policy nội bộ, loại URL trùng và định dạng digest. Gửi Telegram cần xác nhận rõ ràng trước khi thực hiện.

**Link dùng thử:** chưa có URL deploy công khai trong repo; có mã `app.py`.

## A2. Tools
Các tool được khai báo trong `artifacts/tools.yaml` và đăng ký trong `tools/__init__.py`.

| Tool | Chức năng | Trạng thái |
|---|---|---|
| `clarify` | Hỏi lại khi thiếu thông tin hoặc cần xác nhận. | Có |
| `timeline` | Lấy bài đăng theo tài khoản. | Có |
| `social_search` | Tìm bài đăng theo từ khóa (`Latest`/`Top`). | Có |
| `lookup` | Tìm kiếm web, gồm tin tức theo khoảng thời gian. | Có |
| `fetch` | Đọc URL được cung cấp. | Có |
| `format` | Định dạng kết quả thành digest. | Có |
| `send` | Gửi Telegram sau xác nhận (`confirmed=true`). | Có (bonus) |
| `policy` | Tìm trong policy nội bộ. | Có (bonus) |
| `papers` | Tìm paper trên arXiv. | Có (bonus) |
| `paper_text` | Trích xuất nội dung paper arXiv. | Có (bonus) |
| `deduplicate_sources` | Loại URL trùng, giữ nguồn đầu tiên. | Tool mới nhóm thêm |

## A3. Câu hỏi thử
1. Tin tức AI hôm nay có gì nổi bật?
2. Mọi người đang bàn gì về GPT-5 trên Twitter?
3. Tóm tắt 5 tweet mới nhất của Elon Musk.
4. Tìm paper mới về RAG và tóm tắt một paper.
5. Loại URL trùng trong danh sách nguồn này: [dán danh sách].

# PHẦN B — Bằng chứng

## B1. Version Evidence
Hiện có run baseline v0; chưa có run v1–v3 hoặc version log đã điền.

| Version | Thay đổi | Kết quả | Run |
|---|---|---|---|
| v0 | Baseline | 15/20 pass; accuracy 0.75, routing 0.80, arguments 0.75, multi-turn 1.00; 0 provider errors. | `runs/v0_B_base_openrouter_20261110T102236137498.json` |
| v1–v3 | Chưa có bằng chứng | Chưa đo | Chưa có |

## B2. Lỗi baseline và hướng sửa

| Case | Lỗi / tool thực tế | Hướng sửa |
|---|---|---|
| `R08_out_of_scope` | Ngoài phạm vi nhưng gọi `send`. | Quy định phạm vi; không gọi tool cho yêu cầu ngoài phạm vi. |
| `R10_missing_handle` | Đoán `sama`, gọi `timeline` thay vì hỏi. | Thiếu tài khoản thì gọi `clarify`. |
| `R11_missing_url` | Gọi `fetch` khi chưa có URL. | Thiếu link thì hỏi người dùng. |
| `R12_confirm_before_send` | Gọi `send` trước khi xác nhận. | Hỏi xác nhận trước; chỉ gửi khi được đồng ý. |
| `R13_parallel_web_and_tweets` | Gọi `lookup` + `social_search`, arguments sai. | Làm rõ cách gán query/topic/timeframe và kiểm tra lại bằng eval. |

Nguồn: run v0 và `analysis/base_runs.csv`; không suy đoán arguments sai của R13 khi log tóm tắt không ghi rõ.

## B3. Team Eval
`data/eval_group.json` có đủ 10 case (5 single-turn, 5 multi-turn) do nhóm tự xây dựng để kiểm thử các tình huống chuyên biệt.

| Case | Kiểm tra | Kỳ vọng | Kết quả |
|---|---|---|---|
| `group_dedup_single` | Deduplicate danh sách đã cho (single-turn). | `deduplicate_sources` | Chưa đo |
| `group_dedup_missing_items` | Hỏi khi thiếu danh sách nguồn (single-turn). | `clarify` | Chưa đo |
| `group_arxiv_paper_search` | Tìm bài báo khoa học trên arXiv (single-turn). | `papers` | Chưa đo |
| `group_company_policy_search` | Tra cứu chính sách công ty (single-turn). | `policy` | Chưa đo |
| `group_out_of_scope_math` | Từ chối câu hỏi giải toán ngoài phạm vi (single-turn). | Không gọi tool | Chưa đo |
| `group_dedup_multi` | Dùng danh sách ở lượt trước để bỏ trùng (multi-turn). | `deduplicate_sources` | Chưa đo |
| `group_clarify_then_send` | Xác nhận ở lượt sau rồi mới gửi Telegram (multi-turn). | `send` (`confirmed=true`) | Chưa đo |
| `group_missing_url_then_fetch` | Cung cấp URL ở lượt sau rồi mới đọc (multi-turn). | `fetch` | Chưa đo |
| `group_correction_search_timeframe` | Sửa khoảng thời gian tìm kiếm từ hôm nay sang tháng (multi-turn). | `lookup` (`timeframe=month`) | Chưa đo |
| `group_switch_search_to_timeline` | Đổi từ tìm kiếm sang xem bài đăng tài khoản chính chủ (multi-turn). | `timeline` | Chưa đo |

## B4. Live Chat
Chưa có transcript live trong repo; transcript mẫu không được tính là bằng chứng.

## B5. Bonus và tests
Các tool bonus `send`, `policy`, `papers`, `paper_text` đều có implementation và đăng ký trong repo; hiện chưa có transcript/run riêng chứng minh đã chạy live. `app.py` có trong repo nhưng chưa có URL deploy.

`tests/test_deduplicate_sources.py` kiểm tra chuẩn hóa/URL trùng, URL lỗi, bảo toàn dữ liệu và dispatch/format. Chưa có output pytest lưu, nên chưa xác nhận số test pass hay bug phát hiện được.

| Bonus | Bằng chứng | Guardrail |
|---|---|---|
| Telegram | `tools/send/`, `artifacts/tools.yaml` | Chỉ gửi sau xác nhận. |
| arXiv/policy | `tools/papers/`, `tools/paper_text/`, `tools/policy/` | Kiểm tra nguồn và trích dẫn; dùng policy cho câu hỏi nội bộ. |
| UI | `app.py` | Chưa có URL public. |
| Unit tests | `tests/test_deduplicate_sources.py` | Cần lưu output chạy pytest. |

## B6. Reflection
- Prompt nên yêu cầu hỏi lại khi thiếu dữ kiện, giới hạn phạm vi và xác nhận trước hành động có side effect.
- `tools.yaml` nên nói rõ cách chọn tool và quy ước arguments.
- Boundary gửi/publish và câu hỏi ngoài phạm vi cần review cẩn thận, không chỉ dựa vào điểm tự động.
- Tiếp theo: hoàn thiện prompt, chạy v1–v3 và group eval, bổ sung 7 eval case, lưu transcript và kết quả pytest.

## B7. Local Model Challenge
Chưa có bằng chứng chạy Ollama/local model; chưa thể đánh giá độ chính xác hoặc các kiểu lỗi.
