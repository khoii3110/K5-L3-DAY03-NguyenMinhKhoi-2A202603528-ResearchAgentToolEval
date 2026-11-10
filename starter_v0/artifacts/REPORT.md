# Day 03 Lab v2 Report — Research Agent

## Team
- Team / Members: Nguyễn Minh Khôi (2A202603528), Võ Công Minh, Nguyễn Đắc Tuấn Nghĩa (2A202603442), Nguyễn Ngọc Hiếu (2A202603502).
- Provider/model: OpenRouter / `openai/gpt-4o-mini`.

---

# PHẦN A — Giới thiệu agent

## A1. Khả năng
Research Agent tìm tin trên web và mạng xã hội, xem bài đăng theo tài khoản, đọc URL và paper arXiv, tra cứu chính sách nội bộ, loại bỏ URL trùng lặp và định dạng digest. Giao tiếp Telegram có guardrail yêu cầu xác nhận rõ ràng trước khi gửi.

**Giao diện & Trải nghiệm:** Chạy trực tiếp qua Streamlit UI cục bộ tại `http://localhost:8501` (khởi chạy bằng lệnh `python -m streamlit run app.py`).

## A2. Tools
Các tool được khai báo trong `artifacts/tools.yaml` và đăng ký trong `tools/__init__.py`.

| Tool | Chức năng | Phân loại |
|---|---|---|
| `clarify` | Hỏi lại khi thiếu thông tin hoặc cần xác nhận. | Core tool |
| `timeline` | Lấy bài đăng theo tài khoản Twitter. | Core tool |
| `social_search` | Tìm bài đăng Twitter theo từ khóa (`Latest`/`Top`). | Core tool |
| `lookup` | Tìm kiếm web với Tavily, hỗ trợ lọc tin tức theo thời gian. | Core tool |
| `fetch` | Đọc nội dung trang web từ URL cụ thể bằng Firecrawl. | Core tool |
| `format` | Định dạng dữ liệu thu thập thành bản tin digest. | Core tool |
| `send` | Gửi tin nhắn Telegram sau khi có xác nhận (`confirmed=true`). | Bonus tool |
| `policy` | Tra cứu tài liệu và quy định nội bộ công ty. | Bonus tool |
| `papers` | Tìm kiếm bài báo khoa học trên arXiv. | Bonus tool |
| `paper_text` | Trích xuất toàn văn nội dung bài báo arXiv từ PDF. | Bonus tool |
| `deduplicate_sources` | Lọc bỏ URL trùng lặp (chuẩn hóa domain, xóa UTM/tracking query). | Tool mới nhóm tự phát triển |

## A3. Câu hỏi thử
1. Tin tức AI hôm nay có gì nổi bật?
2. Mọi người đang bàn gì về GPT-5 trên Twitter?
3. Tóm tắt 5 tweet mới nhất của Elon Musk.
4. Tìm paper mới về Retrieval-Augmented Generation trên arXiv và tóm tắt ngắn gọn.
5. Loại bỏ các URL trùng trong danh sách nguồn: `[{"url": "https://example.com/news?utm_source=chat"}, {"url": "https://example.com/news"}]`.

---

# PHẦN B — Bằng chứng thực nghiệm

## B1. Version Evidence
Đã hoàn thành đánh giá baseline `v0` trên toàn bộ 20 test cases chuẩn hóa của `data/eval_base.json`:

| Version | Thay đổi | Kết quả thực tế | Run file |
|---|---|---|---|
| v0 | Baseline (Prompt và Tool schema khởi điểm) | 14/20 pass (70% accuracy, 80% routing, 70% args, 100% multi-turn) | `runs/v0_B_base_openrouter_20261110T151647352421.json` |

## B2. Phân tích lỗi Baseline v0

| Case | Lỗi thực tế | Nguyên nhân & Hướng khắc phục |
|---|---|---|
| `R03_web_news_routing` | `wrong_tool` (sai tham số query) | Truyền `query="AI news"` thay vì `query="AI", topic="news"`. Cần mô tả rõ convention tham số trong `tools.yaml`. |
| `R08_out_of_scope` | `out_of_scope` (gọi nhầm tool) | Câu hỏi ngoài phạm vi nghiên cứu nhưng agent vẫn gọi tool. Cần quy định biên giới từ chối trong prompt. |
| `R10_missing_handle` | `missing_info` (đoán mò) | Người dùng không đưa tài khoản, agent tự đoán `sama`. Cần ép rule gọi `clarify` khi thiếu đối tượng. |
| `R11_missing_url` | `missing_info` (đoán mò) | Thiếu link nhưng agent vẫn cố gọi `fetch`. Cần gọi `clarify` để yêu cầu link. |
| `R12_confirm_before_send` | `wrong_boundary` (hành động vội) | Gọi `send` trước khi người dùng xác nhận. Cần chặn hành động gửi và gọi `clarify` xin phép trước. |
| `R13_parallel_web_and_tweets` | `wrong_tool` (sai tham số query) | Truyền nhầm `query="AI news"` thay vì tách biệt từ khóa và topic. |

## B3. Team Eval
Bộ đề kiểm thử độc lập do nhóm tự phát triển gồm đủ 10 cases (5 single-turn, 5 multi-turn) trong `data/eval_group.json`. Kết quả chạy đánh giá thực tế đạt **7/10 pass (70.0%)**, **tool routing accuracy đạt 90.0%** (`runs/v0_B_group_openrouter_20261110T222620690855.json`):

| Case | Loại kiểm thử | Kỳ vọng | Kết quả baseline v0 |
|---|---|---|---|
| `group_dedup_single` | Bỏ trùng URL danh sách nguồn có sẵn (single-turn) | `deduplicate_sources` | PASS |
| `group_dedup_missing_items` | Hỏi lại khi thiếu danh sách nguồn (single-turn) | `clarify` | PASS |
| `group_arxiv_paper_search` | Tìm bài báo khoa học trên arXiv (single-turn) | `papers` | PASS |
| `group_company_policy_search` | Tra cứu chính sách công ty (single-turn) | `policy` | FAIL (arg query dài) |
| `group_out_of_scope_math` | Từ chối câu hỏi giải toán ngoài phạm vi (single-turn) | Không gọi tool | FAIL (gọi lookup do prompt v0) |
| `group_dedup_multi` | Dùng danh sách nguồn ở lượt trước để bỏ trùng (multi-turn) | `deduplicate_sources` | PASS |
| `group_clarify_then_send` | Hỏi xác nhận ở lượt 1, xác nhận xong mới gửi Telegram (multi-turn) | `send` (`confirmed=true`) | PASS |
| `group_missing_url_then_fetch` | Hỏi URL ở lượt 1, có URL ở lượt 2 mới đọc bài (multi-turn) | `fetch` | PASS |
| `group_correction_search_timeframe` | Đính chính khoảng thời gian tìm kiếm từ ngày sang tháng (multi-turn) | `lookup` (`timeframe=month`) | FAIL (arg query thừa từ) |
| `group_switch_search_to_timeline` | Đổi ý từ tìm kiếm chung sang xem tweet tài khoản chính chủ (multi-turn) | `timeline` | PASS |

## B4. Live Chat Evidence
Đã triển khai ứng dụng Streamlit (`app.py`) và thực hiện tương tác trực tiếp với model OpenRouter thật, lưu tại `starter_v0/transcripts/`:

| Transcript ID | Yêu cầu người dùng | Tool được gọi | Kết quả thực thi |
|---|---|---|---|
| `v3_openrouter_ui_20261110T224946326435.transcript.json` | "Tìm tin tức mới nhất về OpenAI trong tuần này" (tương tác trực tiếp trên giao diện Streamlit) | `lookup` | Trả về tổng hợp tin tức nổi bật tuần này của OpenAI. |
| `v0_openrouter_ui_20261110T224705052469.transcript.json` | "Tìm 2 bài báo khoa học mới nhất về RAG trên arXiv và tóm tắt ngắn gọn" | `papers` -> `format` | Trích xuất thành công 2 bài báo arXiv và định dạng thành digest các phần. |
| `v0_openrouter_ui_20261110T224721535793.transcript.json` | "Tìm tin tức công nghệ nổi bật về OpenAI trong tuần này" | `lookup` | Thu thập dữ liệu web thời gian thực thành công. |
| `v0_openrouter_ui_20261110T224734173076.transcript.json` | "Loại bỏ các URL trùng lặp trong danh sách nguồn có gắn UTM params" | `deduplicate_sources` | Lọc sạch các link trùng lặp theo đúng chuẩn URL. |

## B5. Bonus & Unit Tests
- **Unit test suite:** Toàn bộ **104 unit tests passed** (`python -m pytest`), bao gồm:
  - 34 test cases độc lập cho tool mới `deduplicate_sources` (`tests/test_deduplicate_sources.py`).
  - Toàn bộ các bài test contract và example tool (`tests/test_tool_contract.py`, `tests/test_tools_examples.py`).
- **Tool mới tự phát triển:** `deduplicate_sources` hoạt động ổn định, đã có tài liệu `TOOL.md` và tích hợp hoàn chỉnh vào hệ thống.
- **Guardrail an toàn:** Tool `send` được trang bị cơ chế chặn (`needs_confirmation`) nếu chưa có cờ `confirmed=True`.
- **Giao diện người dùng:** Ứng dụng Streamlit `app.py` đã hoàn thành đầy đủ các tính năng chat, gợi ý câu hỏi và hiển thị chi tiết các vòng gọi tool.

## B6. Bài học kinh nghiệm & Đúc kết
- **Prompt Guardrail:** Cần triệt tiêu hoàn toàn hướng dẫn đoán mò cố ý của starter; bắt buộc agent phải dừng lại gọi `clarify` khi thiếu tham số bắt buộc hoặc khi thực hiện hành động gửi tin nhắn.
- **Độ chính xác tham số (Arg Convention):** Cần quy định rõ ràng trong `tools.yaml` về định dạng đối số (tách biệt `query` từ khóa với `topic` hoặc `timeframe`) để tránh việc agent gộp toàn bộ câu lệnh vào query.
- **Kiểm soát phạm vi (Boundary):** Đối với các câu hỏi ngoài phạm vi năng lực nghiên cứu (như giải toán), mô tả tool và prompt cần hướng dẫn agent trả lời trực tiếp hoặc từ chối lịch sự, tránh lãng phí chi phí gọi API tìm kiếm.
