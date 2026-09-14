# Phần E — Security, ticket hygiene và bonus tool

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

## Ticket rác và secret

`create_ticket` từ chối summary có password, token, API key, MFA/OTP hoặc
recovery code có kèm giá trị. Với payload giống hệt (summary, priority, asset)
trong 24 giờ, tool trả `duplicate_suppressed` thay vì ghi file mới. Confirmation
vẫn phải là Boolean `true`; prompt cần bảo đảm confirmation thuộc payload mới
nhất trong hội thoại.

## Bonus: `lookup_ticket_status`

Tool read-only tra cứu ticket giả lập theo ID `INC-*`, `REQ-*` hoặc `LAB-*`.
Nó có mock data, implementation, registry, schema, TOOL.md và smoke test:

```powershell
python scripts/security_smoke.py
```

Đề xuất thêm một case single-turn vào `data/eval_group.json` khi nhóm điền đủ
10 case: hỏi trạng thái `INC-1042`, kỳ vọng đúng một tool call
`lookup_ticket_status` với `ticket_id: INC-1042`.
