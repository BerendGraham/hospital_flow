# beds.py
from typing import Dict, List, Optional, Iterable
from ..smart_core.bed import Bed

class BedRegistry:
    """
    In-memory bed catalog with simple matching rules.
    """
    def __init__(self):
        self._beds: Dict[str, Bed] = {}

    # CRUD-ish
    def add_bed(self, bed_type: str, section: str, features: Iterable[str] = ()) -> str:
        b = Bed(bed_type=bed_type, section=section, features=set(features))
        self._beds[b.id] = b
        return b.id

    def list_beds(self, status: Optional[str] = None) -> List[dict]:
        beds = self._beds.values()
        if status:
            beds = [b for b in beds if b.status == status]
        return [b.to_dict() for b in beds]

    def get(self, bed_id: str) -> Optional[Bed]:
        return self._beds.get(bed_id)

    def free_bed(self, bed_id: str) -> None:
        b = self._beds[bed_id]
        b.status = "OPEN"
        b.patient_id = None

    # Matching
    def find_match(
        self,
        needed_bed_type: Optional[str],
        needed_section: Optional[str],
        required_features: Optional[Iterable[str]] = None,
    ) -> Optional[Bed]:
        """
        Very simple matcher:
          - status must be OPEN
          - if needed_bed_type present -> match exact
          - if needed_section present -> match exact
          - if required_features present -> all must be subset of bed.features
        Returns the first OPEN bed that satisfies constraints (can add scoring later).
        """
        req_feat = set(required_features or [])
        for b in self._beds.values():
            if b.status != "OPEN":
                continue
            if needed_bed_type and b.bed_type != needed_bed_type:
                continue
            if needed_section and b.section != needed_section:
                continue
            if req_feat and not req_feat.issubset(b.features):
                continue
            return b
        return None

    def occupy(self, bed_id: str, patient_id: str) -> None:
        b = self._beds[bed_id]
        b.status = "OCCUPIED"
        b.patient_id = patient_id
