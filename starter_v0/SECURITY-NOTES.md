# Phần E — Security, ticket hygiene và bonus tool

## Tóm tắt đóng góp

Phần E bổ sung ba lớp bảo vệ cho IT Helpdesk Agent:

1. Kiểm soát dữ liệu trước khi gọi Tavily, để dữ liệu nội bộ không rời khỏi
   hệ thống qua external search.
2. Kiểm soát action `create_ticket`, để không lưu secret và không tạo ticket
   trùng lặp.
3. Bổ sung capability còn thiếu là tra cứu trạng thái ticket bằng một tool
   read-only có mock data ổn định.

Các thay đổi được thực hiện trên branch `contrib/nguyenquangduy-security`.
Chúng không được push trực tiếp vào `main`; cần tạo Pull Request để nhóm trưởng
review và merge.

## Rà soát Tavily

`search_device_info` chỉ nhận manufacturer, public model, query type và số kết
quả. Trước khi kiểm tra API key hoặc thực hiện HTTP request, implementation chặn
asset/employee ID, hostname, serial, IP, email, location, diagnostic/ticket
content và credential-like field. Web result được xem là untrusted; dòng có dấu
hiệu instruction/prompt injection được tách ra khỏi `summary`/`title`.

Smoke check không tiêu quota Tavily:

```powershell
python -c "from tools import TOOL_FUNCTIONS as T; print(T['search_device_info']('Lenovo','ThinkPad T14 hostname=build-agent-7','drivers'))"
```

Kỳ vọng: `error: restricted_external_data`, không có HTTP request.

### Thay đổi implementation

File: `tools/search_device_info/tool.py`

- Giữ guardrail có sẵn cho internal asset/employee ID như `LT-204` và
  `EMP-1001`.
- Bổ sung `RESTRICTED_EXTERNAL_DATA` để chặn hostname, serial number, IP,
  email, location, assigned user, diagnostic log, ticket content và
  credential-like data.
- Kiểm tra này chạy **trước** khi đọc API key hoặc gửi HTTP request đến Tavily.
- Mở rộng marker prompt injection trong web result, gồm `prompt injection`,
  `follow these instructions` và `# instructions`, ngoài các marker role
  spoofing có sẵn.
- Xử lý `max_results` không hợp lệ hoặc Boolean rõ ràng hơn thay vì để lỗi ép
  kiểu phát sinh trong request path.

Ranh giới: chỉ manufacturer, public model name, query type và số lượng kết quả
được phép ra external provider. Kết quả web vẫn là untrusted evidence và không
thể xác nhận action hoặc thay đổi policy.

## Ticket rác và secret

`create_ticket` từ chối summary có password, token, API key, MFA/OTP hoặc
recovery code có kèm giá trị. Với payload giống hệt (summary, priority, asset)
trong 24 giờ, tool trả `duplicate_suppressed` thay vì ghi file mới. Confirmation
vẫn phải là Boolean `true`; prompt cần bảo đảm confirmation thuộc payload mới
nhất trong hội thoại.

### Thay đổi implementation

File: `tools/create_ticket/tool.py`

- Reject summary có password, token, API key, MFA code, OTP hoặc recovery code
  khi có kèm giá trị nhạy cảm.
- Giới hạn ticket summary còn 500 ký tự để giảm payload quá dài.
- Thêm idempotency/deduplication window 24 giờ. Nếu summary, priority và asset
  ID trùng ticket đã tạo gần đây, trả `duplicate_suppressed` cùng ticket ID cũ
  và không ghi file JSON mới.
- Vẫn yêu cầu `confirmed is True` thật sự; string `"true"`, số hoặc object vẫn
  không được tính là confirmation hợp lệ.

Giới hạn đã biết: implementation chỉ có thể kiểm tra kiểu Boolean. System
prompt và agent loop phải tiếp tục bảo đảm confirmation thuộc payload mới nhất,
không dựa vào pseudo-code, fake tool result hoặc confirmation cũ.

## Bonus: `lookup_ticket_status`

Tool read-only tra cứu ticket giả lập theo ID `INC-*`, `REQ-*` hoặc `LAB-*`.
Nó có mock data, implementation, registry, schema, TOOL.md và smoke test:

```powershell
python scripts/security_smoke.py
```

Đề xuất thêm một case single-turn vào `data/eval_group.json` khi nhóm điền đủ
10 case: hỏi trạng thái `INC-1042`, kỳ vọng đúng một tool call
`lookup_ticket_status` với `ticket_id: INC-1042`.

### Contract bonus tool

| Thành phần | Chi tiết |
|---|---|
| Tên | `lookup_ticket_status` |
| Mục tiêu | Tra cứu trạng thái ticket giả lập theo ID |
| Input | `ticket_id`: `INC-*`, `REQ-*` hoặc `LAB-*` |
| Output | `ticket` khi tìm thấy, hoặc `status: not_found` |
| Data source | `helpdesk_data/ticket_status.json` |
| Side effect | Không có (`false`) |
| Guardrail | Reject ID sai định dạng; không tạo/cập nhật ticket; không đọc attachment |

Các file thêm mới:

- `tools/lookup_ticket_status/tool.py`: implementation.
- `tools/lookup_ticket_status/TOOL.md`: contract/frontmatter.
- `tools/lookup_ticket_status/__init__.py`: package marker.
- `helpdesk_data/ticket_status.json`: mock ticket fixtures.

Tool đã được đăng ký ở `tools/__init__.py` và khai báo cho model ở
`artifacts/tools.yaml`.

## Smoke test và kết quả

File `scripts/security_smoke.py` tự thêm `starter_v0` vào Python path để chạy
được từ bất kỳ working directory nào. Test không gọi Tavily thật và không cần
API key; nó kiểm tra bốn điều kiện:

1. Payload có hostname bị chặn trước external request.
2. Password trong ticket summary bị từ chối.
3. Ticket trùng được suppress trong thư mục tạm, không động vào `tickets/` thật.
4. `lookup_ticket_status('INC-1042')` trả `in_progress` và `side_effect: false`.

Kết quả chạy thực tế ngày 2026-09-14:

```text
PASS: Tavily boundary, ticket hygiene, and ticket-status bonus tool
```

## Checklist để nộp

- [x] Implementation security cho Tavily.
- [x] Ticket secret và duplicate guardrail.
- [x] Bonus tool: implementation, mock data, registry, schema và TOOL.md.
- [x] Smoke test PASS.
- [ ] Một member được phân công thêm case ticket-status vào đúng bộ 10 group eval cases.
- [ ] Người phụ trách prompt thêm safety rules tương ứng vào `artifacts/system_prompt.md`.
- [ ] Ghi evidence này vào mục B5/B6 của `artifacts/REPORT.md`.
- [ ] Push branch `contrib/nguyenquangduy-security` sau khi được cấp collaborator permission và tạo PR.
