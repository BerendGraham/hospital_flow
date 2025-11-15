# patient.py
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import uuid

UTC = timezone.utc

@dataclass
class Patient:
    """
    Represents a patient to be placed in the queue.
    - esi: Emergency Severity Index (ESI) 1..5 (1 = most urgent)
    - status: "WAITING" | "TREATING" | "ON_HOLD" | "DISCHARGED"
    """
    name: str
    esi: int                       # 1..5
    department: str = "ED"
    status: str = "WAITING"
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    arrival_ts: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_assessed_ts: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        d = asdict(self)
        d["arrival_ts"] = self.arrival_ts.isoformat()
        d["last_assessed_ts"] = self.last_assessed_ts.isoformat()
        return d
