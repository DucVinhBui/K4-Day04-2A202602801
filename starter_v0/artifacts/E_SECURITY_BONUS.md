# Phần E — Security review và bonus tool

## Tavily / external data boundary

`search_device_info` chỉ nhận `manufacturer`, public `model`, `query_type` và
`max_results`. Hàm chặn asset/employee ID, serial, hostname, IP, location,
assigned user, diagnostics, credential và ticket marker trước khi đọc API key
hoặc tạo HTTP request. Request Tavily được tạo từ chuỗi public-only; web result
được trả về như untrusted evidence và loại các dòng mang instruction-like text.

Smoke check không gọi mạng:

```powershell
python -c "from tools import TOOL_FUNCTIONS as T; r=T['search_device_info']('Lenovo','ThinkPad T14 Gen 4 LT-204','drivers',2); assert r['error']=='restricted_internal_data'; print('Tavily privacy guard: PASS')"
```

## Ticket hygiene

`starter_v0/tickets/` không chứa ticket sinh thử tại thời điểm kiểm tra. Thư
mục này đã bị `.gitignore` loại khỏi submission. Không tạo ticket khi smoke
test: `create_ticket(..., confirmed=False)` trả `needs_confirmation` và không
ghi file. Không đưa generated ticket, password, token, MFA/OTP hoặc dữ liệu
thật vào evidence.

## Bonus: `lookup_ticket_status`

Tool mới đọc fixture `helpdesk_data/ticket_status.json`, nhận đúng một public
ticket ID (`INC-1234`, `CHG-1234` hoặc `REQ-1234`) và chỉ trả trạng thái vận
hành đã được sanitize. Đây là tool read-only: không tạo/sửa ticket, không tìm
theo employee/asset/free-text, và không trả ticket body hay dữ liệu requester.

Chạy smoke test:

```powershell
python scripts/smoke_ticket_status.py
```

Team/member eval cases nằm tại `data/eval_security_bonus.json`; khi hợp nhất
team eval chính, giữ case `E01` hoặc một case tương đương để chứng minh routing
và case `E02` để chứng minh boundary không suy đoán ticket ID.
