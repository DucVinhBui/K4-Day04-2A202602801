from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools import TOOL_FUNCTIONS


def main() -> None:
    lookup = TOOL_FUNCTIONS["lookup_ticket_status"]
    found = lookup("inc-1042")
    assert found["ticket"]["status"] == "investigating", found
    assert found["ticket"]["ticket_id"] == "INC-1042", found
    assert "requester" not in found["ticket"], found

    malformed = lookup("LT-204")
    assert malformed["error"] == "invalid_ticket_id", malformed

    absent = lookup("INC-9999")
    assert absent["error"] == "ticket_not_found", absent
    print("lookup_ticket_status smoke test: PASS")


if __name__ == "__main__":
    main()
