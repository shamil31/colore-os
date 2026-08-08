"""Vendor-neutral capability vocabulary.

ADR-002 decision 3: Growth AI asks the gateway for a *capability* and never
names a platform. Adding a channel is registering a connector, not editing the
code that decides what to do.

Connectors may also declare vendor-specific capability names — `altegio.get_staff`
and friends already exist and callers that genuinely need one platform (the
import scripts) should keep using them. The neutral names below are for callers
that must not care, which is every caller in the decision layer.

The values are the wire format: they are stored in the trace, returned over
HTTP and read in logs. Do not rename one without a migration.
"""

MESSAGE_SEND = "message.send"
"""Deliver a message to a person or a channel."""

WORKFLOW_TRIGGER = "workflow.trigger"
"""Start an external automation workflow."""

EVENT_VERIFY = "event.verify"
"""Answer a platform's webhook verification handshake."""

CLIENTS_READ = "clients.read"
"""Read client records from the system of record."""

RECORDS_READ = "records.read"
"""Read appointment or visit records from the system of record."""


NEUTRAL_CAPABILITIES = frozenset(
    {
        MESSAGE_SEND,
        WORKFLOW_TRIGGER,
        EVENT_VERIFY,
        CLIENTS_READ,
        RECORDS_READ,
    }
)
