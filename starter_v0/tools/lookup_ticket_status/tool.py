from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from tools._shared import ROOT, err


TICKET_ID_PATTERN = re.compile(r"^(?:INC|CHG|REQ)-\d{4}$", re.IGNORECASE)
TICKET_STATUS_PATH = ROOT / "helpdesk_data" / "ticket_status.json"


def lookup_ticket_status(ticket_id: str = "") -> dict[str, Any]:
    """Return a read-only, sanitized status record for a known mock ticket."""
    if not isinstance(ticket_id, str):
        return {"tool": "lookup_ticket_status", "error": "invalid_ticket_id_type"}

    normalized_ticket_id = ticket_id.strip().upper()
    if not TICKET_ID_PATTERN.fullmatch(normalized_ticket_id):
        return {
            "tool": "lookup_ticket_status",
            "error": "invalid_ticket_id",
            "message": "Provide a ticket ID in the form INC-1234, CHG-1234, or REQ-1234.",
        }

    try:
        snapshot = json.loads(Path(TICKET_STATUS_PATH).read_text(encoding="utf-8"))
        for ticket in snapshot.get("tickets", []):
            if str(ticket.get("ticket_id", "")).upper() == normalized_ticket_id:
                return {
                    "tool": "lookup_ticket_status",
                    "ticket": {
                        "ticket_id": normalized_ticket_id,
                        "status": ticket.get("status"),
                        "priority": ticket.get("priority"),
                        "service": ticket.get("service"),
                        "updated_at": ticket.get("updated_at"),
                        "public_update": ticket.get("public_update"),
                    },
                    "freshness": snapshot.get("snapshot_at"),
                    "trust_boundary": "Read-only mock status data. It contains no requester identity, asset, credentials, or ticket body.",
                }
        return {"tool": "lookup_ticket_status", "error": "ticket_not_found", "ticket_id": normalized_ticket_id}
    except Exception as exc:
        return err("lookup_ticket_status", exc)
