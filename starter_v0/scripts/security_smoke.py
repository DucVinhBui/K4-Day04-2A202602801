from __future__ import annotations

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from tools.create_ticket import tool as ticket_tool
from tools.lookup_ticket_status.tool import lookup_ticket_status
from tools.search_device_info.tool import search_device_info


def assert_result(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    external = search_device_info("Lenovo", "ThinkPad T14 hostname=build-agent-7", "drivers")
    assert_result(external.get("error") == "restricted_external_data", "external-data guard failed")

    secret = ticket_tool.create_ticket("VPN password của tôi là Summer2026!", "high", "LT-204", True)
    assert_result(secret.get("error") == "restricted_sensitive_data", "ticket secret guard failed")

    with tempfile.TemporaryDirectory() as directory:
        original_dir = ticket_tool.TICKET_DIR
        ticket_tool.TICKET_DIR = Path(directory)
        try:
            (Path(directory) / "LAB-EXISTING.json").write_text(json.dumps({
                "ticket_id": "LAB-EXISTING", "summary": "VPN unavailable", "priority": "high",
                "asset_id": "LT-204", "created_at": datetime.now(timezone.utc).isoformat(),
            }), encoding="utf-8")
            duplicate = ticket_tool.create_ticket("VPN unavailable", "high", "LT-204", True)
            assert_result(duplicate.get("status") == "duplicate_suppressed", "duplicate guard failed")
        finally:
            ticket_tool.TICKET_DIR = original_dir

    lookup = lookup_ticket_status("INC-1042")
    assert_result(lookup.get("ticket", {}).get("status") == "in_progress", "bonus lookup failed")
    assert_result(lookup.get("side_effect") is False, "bonus lookup must be read-only")
    print("PASS: Tavily boundary, ticket hygiene, and ticket-status bonus tool")


if __name__ == "__main__":
    main()
