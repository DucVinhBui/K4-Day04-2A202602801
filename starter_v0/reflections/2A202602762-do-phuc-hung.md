# Self-reflection — Đỗ Phúc Hưng

> Reflection cá nhân cho bài Lab Day 04, team **kuteboyz**.
> Điền theo mẫu ở `starter_v0/artifacts/REPORT.md` mục C2.

## Họ tên — MSSV

Đỗ Phúc Hưng — 2A202602762

- **Vai trò/phần việc được nhận:**
  Cấu hình provider/model và chạy evaluation cho base eval. Trong repo,
  nhánh làm việc là `contrib/huwungG`. Phần việc chính liên quan tới:
  - Khai báo key và load `.env` cho provider.
  - Chạy `run_eval.py` nhiều lần với `--provider openrouter` để thu
    baseline metric và debug lỗi provider.
  - Đối chiếu `runs/*.json` với prompt/tool artifacts để tìm điểm cần
    cải thiện trong `system_prompt.md` và `tools.yaml`.

- **Những gì tôi đã thay đổi trong repo chung:**
  - Cập nhật `starter_v0/.env` đặt `OPENROUTER_API_KEY` đúng định dạng
    OpenRouter (`sk-or-v1-...`); vô hiệu hóa các key không dùng
    (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`).
  - Chạy `python run_eval.py --provider openrouter --version v0 --suite
    base --eval-cases data/eval_base.json` lặp lại nhiều lần từ thư mục
    `starter_v0`. Mỗi lần chạy ghi một file mới vào
    `starter_v0/runs/v0_B_base_openrouter_<timestamp>.json`.
  - Không sửa trực tiếp `system_prompt.md` hay `tools.yaml` ở vòng này;
    vòng lặp version sẽ được đồng độu khác đảm nhiệm sau khi debug
    xong auth.

- **File hoặc artifact liên quan:**
  - `starter_v0/.env` — khai báo key provider.
  - `starter_v0/runs/v0_B_base_openrouter_20260914T200623440518.json`
    — run evidence chính dùng làm baseline (29/30 PASS, artifact
    `v0+pef8d0c1952b8+t2779dba71c07`).
  - 4 run sớm hơn (`...190151380604.json`, `...190406739682.json`,
    `...191404535019.json`, `...191455730179.json`) đều fail vì
    `AuthenticationError: 401 - Missing Authentication header`.
  - `starter_v0/scripts/preflight_provider.py` — đã tham khảo để hiểu
    cơ chế preflight.

- **Commit hash hoặc pull request:**
  > _TODO: điền commit hash và link PR sau khi đẩy `contrib/huwungG`
  > lên fork chung và mở pull request vào branch nộp bài. Nhánh đã tồn
  > tại ở remote (`git branch` cho thấy `* contrib/huwungG`)._

- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
  Chọn **OpenRouter với model `openai/gpt-4o-mini`** thay vì gọi trực
  tiếp OpenAI native làm provider mặc định. Lý do:
  1. OpenRouter trỏ thẳng tới `openai/gpt-4o-mini` qua cùng OpenAI
     schema, nên không cần đổi `agent.py`/`providers/`.
  2. Có sẵn fallback sang nhiều model khác (Anthropic, Gemini, ...) chỉ
     bằng cách đổi tên model, không phải đổi code.
  3. Starter README khuyến nghị OpenRouter làm lựa chọn đầu tiên nên
     hạ tầng logging và artifact version (`versioning.py`) đã hỗ trợ
     sẵn.

- **Khó khăn tôi gặp và cách tôi xử lý:**
  - **Auth fail 100% khi mới chạy eval lần đầu.** `run_eval.py` in
    30 case `provider_error` với nội dung
    `AuthenticationError: 401 - Missing Authentication header`. Không
    phải routing hay argument — `provider_error_cases: 30` nghĩa là
    eval không đo được gì về prompt.
  - **Nguyên nhân thật.** `OPENROUTER_API_KEY` trong `.env` ban đầu
    được dán từ project OpenAI, mang prefix `sk-proj-`. OpenRouter
    báo "Missing Authentication header" thay vì "Invalid key" vì nó
    không nhận ra prefix, nên biểu hiện dễ nhầm với key rỗng.
  - **Cách xử lý.** Tôi đã đọc
    `runs/v0_B_base_openrouter_20260914T191455730179.json` trường
    `failures` để xác nhận là lỗi OpenRouter 401, không phải của
    OpenAI provider. Sau đó làm key mới đúng format `sk-or-v1-...`,
    chạy lại eval và nhận `passed_cases: 29`, `provider_error_cases: 0`.
  - **Bài học debug.** Terminal lúc đầu `cd ..` ra thư mục cha nên
    Python báo `No module named 'dotenv'`. Phải luôn chạy diagnostic
    từ đúng thư mục `starter_v0` (nơi có `.venv` đầy đủ).

- **Điều tôi học được từ phần việc này:**
  - Phân biệt được 4 loại metric fail của eval: `provider_error`
    (cơ sở hạ tầng), `wrong_tool` (routing), `wrong_arg_value`
    (schema), `missing_info`/`wrong_boundary` (chính sách). Mỗi loại
    cần một cách debug khác nhau.
  - `provider_error_cases == 0` là điều kiện tiên quyết để một run
    được tính là evidence. Một run đẹp nhưng fail auth thì không có
    giá trị đo.
  - Tool routing accuracy 100% ở v0 cho thấy phần lớn rule trong
    `system_prompt.md` đã đúng; vấn đề còn lại (H11) là biên — model
    dùng default thay vì truyền arg explicit, một dạng lỗi đặc thù
    của strict grader.

- **Nếu làm lại, tôi sẽ cải thiện điều gì:**
  1. **Chạy `scripts/preflight_provider.py` trước mỗi eval.** Nếu
     preflight fail thì không nên chạy 30 case để rồi nhận 30/30
     `provider_error`. Hiện tại hai bước này chưa được nối với nhau.
  2. **Pin một dòng smoke test vào CI.** Một case đơn (`H01`) chạy
     trước, nếu nó không về PASS thì stop sớm — đỡ tốn thời gian
     chờ 30 case fail cùng một lỗi.
  3. **Tách phần "đổi key" ra khỏi `.env` thật.** Dùng shell export
     hoặc secret manager để tránh nhầm key OpenAI vào biến
     `OPENROUTER_API_KEY` như đã xảy ra.
  4. **Ghi chú lại từng lần chạy vào `version_log.csv`** kể cả khi
     fail, để khi rà lại biết được baseline 0/30 → 29/30 đến từ
     thay đổi nào.
