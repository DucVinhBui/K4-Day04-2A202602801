from __future__ import annotations

import json
import re
from typing import Any

from tools._shared import ROOT, err


TICKET_STATUS_FILE = ROOT / "helpdesk_data" / "ticket_status.json"
TICKET_ID_PATTERN = re.compile(r"^(?:INC|REQ|LAB)-\d{3,8}$", re.IGNORECASE)


def lookup_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    """Read a fictional ticket status without creating or changing a ticket."""
    if not isinstance(ticket_id, str):
        return {"tool": "lookup_ticket_status", "error": "invalid_ticket_id_type"}
    normalized_id = ticket_id.strip().upper()
    if not TICKET_ID_PATTERN.fullmatch(normalized_id):
        return {
            "tool": "lookup_ticket_status",
            "error": "invalid_ticket_id",
            "message": "Provide a ticket ID such as INC-1042, REQ-220, or LAB-12345678.",
        }
    try:
        records = json.loads(TICKET_STATUS_FILE.read_text(encoding="utf-8"))
        for record in records.get("tickets", []):
            if str(record.get("ticket_id", "")).upper() == normalized_id:
                return {
                    "tool": "lookup_ticket_status",
                    "ticket": record,
                    "source": "fictional_static_ticket_store",
                    "side_effect": False,
                }
        return {"tool": "lookup_ticket_status", "status": "not_found", "ticket_id": normalized_id}
    except Exception as exc:
        return err("lookup_ticket_status", exc)
