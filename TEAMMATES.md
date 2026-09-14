# TEAMMATES — K4-Day04-2A202602801

- **Nhóm:** kuteboyz
- **Repository nộp bài chung:** https://github.com/DucVinhBui/K4-Day04-2A202602801
- **Branch nộp bài:** `main`

## Thành viên

| Họ và tên | MSSV | GitHub username | Vai trò |
| --- | --- | --- | --- |
| Bùi Đức Vinh | 2A202602801 | [DucVinhBui](https://github.com/DucVinhBui) | **Nhóm trưởng** · C — Eval & Red-Team: tác giả 10 case `eval_group.json` (G01→G10), kiểm thử 12 adversarial attack, vòng cải tiến prompt v1→v4 và tổng hợp evidence |
| `<Họ và tên đầy đủ>` | `<MSSV>` | [TuTune04](https://github.com/TuTune04) | A+B — Prompt Architect & Tool Schema: xây `system_prompt.md` qua v1/v2/v3.1, chuẩn hoá enum và description trong `tools.yaml`, cập nhật `search_device_info` |
| Nguyễn Quang Duy | `<MSSV>` | [nguyenquangduy2005](https://github.com/nguyenquangduy2005) | E — Security & Bonus Tool: rà soát data leakage của external search, xây bonus tool `lookup_ticket_status` kèm smoke test và `E_SECURITY_BONUS.md` |
| Đỗ Phúc Hưng | 2A202602762 | [huwungG](https://github.com/huwungG) | D — UI & Report Coordinator: cấu hình provider/`.env`, chạy baseline eval, tổng hợp `artifacts/REPORT.md` |

## Bằng chứng đóng góp trên branch nộp bài

Mỗi thành viên có ít nhất một commit nội dung (không tính merge commit) trong
lịch sử `main`.

| Thành viên | Git identity dùng để commit | Commit | Nội dung |
| --- | --- | --- | --- |
| Bùi Đức Vinh | `VinhBuii <dbui9708@uni.sydney.edu.au>` | `9ca626a` | `system_prompt.md` — sửa rule `clarify`/`response_type` |
| | | `5bd7bc6` | `TEAMMATES.md` — bản đầu |
| | | `d8fe114` | `eval_group.json` (10 case), `C_EVAL_REDTEAM.md`, `version_log.csv` v0→v4, 14 run trong `evidence/`, prompt v3/v4 và `tools.yaml` |
| TuTune04 | `TuTune04 <baygiolamaygio04@gmail.com>` | `01df29b` | `system_prompt.md` v1 + `tools.yaml` |
| | | `8118669` | `system_prompt.md` v2, `tools.yaml`, `search_device_info` |
| | | `943e6eb` | `system_prompt.md` v3.1 + `tools.yaml` |
| Nguyễn Quang Duy | `Nguyen Quang Duy <quangduy230905@gmail.com>` | `28952c0` | Bonus tool `lookup_ticket_status` (tool, `TOOL.md`, registry, schema), `eval_security_bonus.json`, `smoke_ticket_status.py`, `E_SECURITY_BONUS.md` |
| Đỗ Phúc Hưng | `huwung <13dophuchung05@gmail.com>` | `44093b3` | `artifacts/REPORT.md` phần A, `reflections/2A202602762-do-phuc-hung.md`, dọn `.env.example` |
| | | `24433bf` | `TEAMMATES.md` |

Kiểm tra lại bằng lệnh:

```bash
git log main --no-merges --format="%h | %an <%ae> | %s"
```

### Ghi chú về Git identity

Hai thành viên dùng hai identity khác nhau giữa GitHub account và Git config
local. Đây là cùng một người, không phải hai thành viên:

- **Bùi Đức Vinh** — GitHub `DucVinhBui`, commit dưới tên `VinhBuii`. Tên
  `DucVinhBui` chỉ xuất hiện ở merge commit của pull request.
- **Đỗ Phúc Hưng** — GitHub `huwungG`, commit dưới tên `huwung`.

### Ghi chú về merge commit `d73ada8`

`d73ada8 "update v2"` do `huwung` tạo là **merge commit** (hai parent:
`44093b3` và `a09bb8b`), không phải commit nội dung. Diff hiển thị của nó bao
gồm cả bonus tool `lookup_ticket_status`, nhưng tác giả thật của phần đó là
**Nguyễn Quang Duy** ở commit `28952c0`.
