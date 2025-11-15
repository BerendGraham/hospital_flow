# bed.py
from dataclasses import dataclass, field, asdict
from typing import Optional, Set
from uuid import uuid4

@dataclass
class Bed:
    """
    A physical care location that can be assigned to a patient.
    bed_type: logical capability (e.g., 'ED', 'ICU', 'OR', 'PEDS', 'ISOLATION', 'POSTOP')
    section: physical wing/zone, e.g., 'A3', 'ED-North', 'OR-2'
    features: optional set like {'negative_pressure', 'cardiac_monitor'}
    status: 'OPEN' | 'HELD' | 'OCCUPIED'
    """
    bed_type: str
    section: str
    features: Set[str] = field(default_factory=set)
    status: str = "OPEN"
    id: str = field(default_factory=lambda: str(uuid4()))
    patient_id: Optional[str] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["features"] = sorted(list(self.features))
        return d
