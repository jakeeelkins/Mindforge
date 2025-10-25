from dataclasses import dataclass

@dataclass
class Alert:
    id: int | None
    sku: str
    location: str
    severity_band: str   # info|warning|critical
    status: str          # open|acked|resolved
    message: str
    first_seen: str
    last_sent: str | None
    next_escalation: str | None
    step_idx: int = 0
