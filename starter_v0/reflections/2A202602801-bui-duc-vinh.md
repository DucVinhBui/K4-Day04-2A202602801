# Self-reflection — Bùi Đức Vinh

> Reflection cá nhân cho bài Lab Day 04, team **kuteboyz**.
> Theo mẫu ở `starter_v0/artifacts/REPORT.md` mục C2.

## Họ tên — MSSV

Bùi Đức Vinh — 2A202602801

- **Vai trò/phần việc được nhận:**
  Nhóm trưởng, kiêm vai C (Eval & Red-Team): tác giả 10 case
  `data/eval_group.json` (G01→G10) và kiểm thử 12 adversarial attack. Nhánh làm
  việc là `contrib/DucVinhBui`, commit dưới Git identity `VinhBuii`.

- **Những gì tôi đã thay đổi trong repo chung:**
  - Viết đúng 10 case original trong `data/eval_group.json`: 5 single-turn
    (G01→G05) và 5 multi-turn (G06→G10).
  - Chạy suite adversarial 12 case, review thủ công từng `tool_results` và
    kiểm tra filesystem xem có ticket nào bị ghi thật không.
  - Chạy vòng cải tiến prompt v1→v4 trên `artifacts/system_prompt.md`, sửa
    `inspect_device.asset_id` trong `artifacts/tools.yaml`.
  - Viết `artifacts/C_EVAL_REDTEAM.md` và điền `artifacts/version_log.csv`
    (v0→v4, kèm hypothesis, metric before/after và run file).
  - Thêm `starter_v0/evidence/` chứa 14 run JSON làm evidence, vì
    `starter_v0/runs/` nằm trong `.gitignore` nên không đi vào submission được.

- **File hoặc artifact liên quan:**
  - `starter_v0/data/eval_group.json` — 10 case team eval.
  - `starter_v0/artifacts/C_EVAL_REDTEAM.md` — phân tích red-team.
  - `starter_v0/artifacts/version_log.csv` — v0→v4.
  - `starter_v0/evidence/v4_B_base_...json` (30/30),
    `v4_B_extension_...json` (10/10), `v4_B_group_...json` (9/10),
    `v4_B_adversarial_...json` (8/12).
  - `starter_v0/evidence/v2_B_extension_openrouter_20260914T204539334218.json`
    — run đối chứng chạy với prompt v2 để chứng minh E02/E03/E06 là gap có sẵn,
    không phải regression của v3.

- **Commit hash hoặc pull request:**
  `9ca626a`, `5bd7bc6`, `d8fe114` — merge qua pull request #4, #5 và #8.

- **Một quyết định kỹ thuật tôi đã đưa ra và lý do:**
  Tôi đề xuất thêm confirmation token gắn với hash payload vào `create_ticket`
  để chặn A03/A04/A10/A11, nhưng sau khi đọc code thì **loại bỏ chính đề xuất
  của mình**. Lý do: `run_eval.py` gọi `agent.run()` chỉ chạy một round
  (`agent.py:38`) nên token không bao giờ được dùng lại, còn `chat.py` tuy chạy
  4 round nhưng đưa tool result thẳng về model (`chat.py:92`) nên model chỉ cần
  gọi `create_ticket` hai lần là tự lấy được token. Một guardrail bị bypass dễ
  như vậy còn tệ hơn không có, vì nó tạo cảm giác an toàn giả. Tôi ghi lại lý do
  loại bỏ trong `C_EVAL_REDTEAM.md` thay vì ship nó.

- **Khó khăn tôi gặp và cách tôi xử lý:**
  Vòng v1 sửa được H11 nhưng làm regress H19, và vòng v4 sửa được E02/E03/E06
  nhưng làm regress G05. Cả hai lần tôi đều không đoán nguyên nhân mà chạy lại
  để phân biệt nhiễu với hành vi hệ thống — riêng G05 tôi chạy group suite hai
  lần, kết quả giống hệt nên xác định là hệ thống chứ không phải nhiễu. Sau đó
  mới sửa đúng rule gây ra nó. Điều này làm tôi hiểu vì sao LAB-GUIDE khuyên mỗi
  version chỉ đổi một artifact chính.

- **Điều tôi học được từ phần việc này:**
  Automatic score không chứng minh được là không có gì bị ghi ra. Suite
  adversarial ở v2 báo 7/12 FAIL, nhưng chỉ khi mở `tool_results` và `ls tickets/`
  tôi mới thấy 4 attack đã ghi ticket thật vào filesystem. Tôi cũng học được
  cách đọc failure cho đúng tầng: H11 FAIL không phải vì model chọn sai tool mà
  vì grader so sánh args của tool call chứ không so sánh tool result — một chi
  tiết chỉ thấy được khi đọc `run_eval.py`.

- **Nếu làm lại, tôi sẽ cải thiện điều gì:**
  Tôi sẽ chạy cả bốn suite ngay từ v0 để có baseline đầy đủ. Thực tế tôi chỉ
  chạy base ở v0→v2, nên tới v3 mới phát hiện extension đang 7/10 và phải chạy
  thêm một run đối chứng với prompt cũ mới chứng minh được đó không phải lỗi do
  mình gây ra. Về kỹ thuật, tôi sẽ ưu tiên sửa `run_model_tool_loop` để nó dừng
  lại khi model gọi `clarify` — đó mới là chỗ đóng được A03/A04/A10/A11, thứ mà
  bốn vòng sửa prompt không làm được.
