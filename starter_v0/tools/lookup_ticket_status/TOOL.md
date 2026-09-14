---
name: lookup_ticket_status
track: bonus
kind: local_read
provider: fictional_static_ticket_store
requires_env: []
inputs: [ticket_id]
outputs: [ticket, status, ticket_id]
side_effect: false
---
# lookup_ticket_status

Looks up the status of a fictional ticket by its ID. This is read-only: it
does not create, update, or expose ticket attachments. Accept only an ID in the
form `INC-<digits>`, `REQ-<digits>`, or `LAB-<digits>`; ask the user to provide
one if it is absent. Returned records are mock data for this lab.
