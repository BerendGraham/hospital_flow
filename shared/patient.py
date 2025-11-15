# patient.py
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict
from enum import Enum
import uuid

UTC = timezone.utc


class PatientStatus(str, Enum):
    """ER workflow stages"""
    REGISTERED = "REGISTERED"
    AWAITING_TRIAGE = "AWAITING_TRIAGE"
    TRIAGED = "TRIAGED"
    AWAITING_BED = "AWAITING_BED"
    IN_BED = "IN_BED"
    AWAITING_DISPOSITION = "AWAITING_DISPOSITION"
    DISCHARGED = "DISCHARGED"
    ADMITTED = "ADMITTED"
    LEFT_WITHOUT_BEING_SEEN = "LWBS"


@dataclass
class Patient:
    """
    Represents a patient in the ER flow.
    - esi: Emergency Severity Index (ESI) 1..5 (1 = most urgent)
    - status: Current stage in ER workflow
    """
    # Required fields
    name: str
    esi: int  # 1..5
    chief_complaint: str
    age: int
    gender: str  # "M" | "F" | "Other"

    # Workflow tracking
    department: str = "ED"
    status: str = PatientStatus.AWAITING_TRIAGE.value

    # Assignments
    bed_id: Optional[str] = None
    assigned_nurse_id: Optional[str] = None  # For logging only
    assigned_physician_id: Optional[str] = None  # For logging only

    # Notes
    notes: str = ""
    triage_notes: str = ""

    # Identifiers & timestamps
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    arrival_ts: datetime = field(default_factory=lambda: datetime.now(UTC))
    timestamps: Dict[str, datetime] = field(default_factory=dict)

    def __post_init__(self):
        """Record initial status timestamp"""
        if not self.timestamps:
            self.timestamps[self.status] = self.arrival_ts

    def time_in_current_status(self) -> timedelta:
        """Calculate how long patient has been in current status"""
        status_start = self.timestamps.get(self.status)
        if status_start:
            return datetime.now(UTC) - status_start
        return timedelta(0)

    def total_er_time(self) -> timedelta:
        """Total time since arrival"""
        return datetime.now(UTC) - self.arrival_ts

    def is_delayed(self) -> bool:
        """Check if patient exceeds ESI wait time threshold"""
        # ESI wait time thresholds in minutes
        thresholds = {
            1: 0,    # Immediate
            2: 10,   # 10 minutes
            3: 30,   # 30 minutes
            4: 60,   # 60 minutes
            5: 120   # 120 minutes
        }
        max_wait = timedelta(minutes=thresholds.get(self.esi, 30))
        return self.time_in_current_status() > max_wait

    def update_status(self, new_status: str) -> None:
        """Update patient status and record timestamp"""
        self.status = new_status
        self.timestamps[new_status] = datetime.now(UTC)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        d = asdict(self)
        d["arrival_ts"] = self.arrival_ts.isoformat()
        # Serialize timestamps dict
        d["timestamps"] = {
            status: ts.isoformat()
            for status, ts in self.timestamps.items()
        }
        # Add computed fields
        d["time_in_current_status_minutes"] = int(self.time_in_current_status().total_seconds() / 60)
        d["total_er_time_minutes"] = int(self.total_er_time().total_seconds() / 60)
        d["is_delayed"] = self.is_delayed()
        return d
