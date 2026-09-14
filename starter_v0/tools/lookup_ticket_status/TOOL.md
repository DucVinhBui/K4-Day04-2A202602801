---
name: lookup_ticket_status
track: bonus
kind: local_status
provider: mock_json
requires_env: []
inputs: [ticket_id]
outputs: [ticket, freshness, trust_boundary]
side_effect: false
---
# lookup_ticket_status

Returns the status of a known mock incident, change, or request ticket from
`helpdesk_data/ticket_status.json`. This is a read-only bonus capability for
checking a ticket after a user supplies its exact public ticket ID.

The tool never searches by person, asset, hostname, or free-text ticket body,
and returns only a sanitized operational update. Invalid and unknown ticket IDs
return deterministic errors.
