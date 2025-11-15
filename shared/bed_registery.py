# beds.py
from typing import Dict, List, Optional, Iterable
from ..smart_core.bed import Bed

class BedRegistry:
    """
    Public service API for bed management.
    Uses an in-memory SQLite store and a process-level mutex for safety.
    """
    def __init__(self):
        self.store = SQLiteBedStore()
        self._lock = threading.Lock()

    # --- CRUD-ish ---
    def add_bed(self, bed_type: str, section: str, features: Iterable[str] = ()) -> str:
        with self._lock:
            return self.store.add_bed(Bed(bed_type=bed_type, section=section, features=set(features)))

    def upsert_bed(self, bed: Bed) -> str:
        with self._lock:
            return self.store.upsert_bed(bed)

    def list_beds(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            return [b.to_dict() for b in self.store.list_beds(status=status)]

    def get(self, bed_id: str) -> Optional[Bed]:
        with self._lock:
            return self.store.get_bed(bed_id)

    # --- Status changes ---
    def free_bed(self, bed_id: str) -> None:
        with self._lock:
            self.store.free_bed(bed_id)

    def hold_bed(self, bed_id: str, patient_id: Optional[str] = None) -> None:
        with self._lock:
            self.store.hold_bed(bed_id, patient_id)

    def occupy_bed(self, bed_id: str, patient_id: str) -> None:
        with self._lock:
            # Ensure patient not already occupying another bed
            existing = self.store.get_bed_by_patient(patient_id)
            if existing and existing.id != bed_id:
                self.store.free_bed(existing.id)
            self.store.occupy_bed(bed_id, patient_id)

    # --- Matching & assignment ---
    def assign_best_available(
        self,
        patient_id: str,
        needed_bed_type: Optional[str] = None,
        needed_section: Optional[str] = None,
        required_features: Optional[Iterable[str]] = None,
    ) -> Optional[str]:
        """
        Assigns the first OPEN bed that matches the patient's constraints.
        Returns bed_id or None.
        """
        with self._lock:
            match = self.store.find_open_bed(needed_bed_type, needed_section, required_features)
            if not match:
                return None
            # free any current bed first (single-occupancy invariant)
            current = self.store.get_bed_by_patient(patient_id)
            if current:
                self.store.free_bed(current.id)
            self.store.occupy_bed(match.id, patient_id)
            return match.id

    def release_patient(self, patient_id: str) -> Optional[str]:
        """
        Free the bed currently occupied by patient_id (if any).
        Returns freed bed_id or None.
        """
        with self._lock:
            b = self.store.get_bed_by_patient(patient_id)
            if not b:
                return None
            self.store.free_bed(b.id)
            return b.id

    def move_patient_to_bed(self, patient_id: str, to_bed_id: str) -> Tuple[Optional[str], str]:
        """
        Force a move to a specific OPEN bed (manual override).
        Returns (from_bed_id, to_bed_id).
        """
        with self._lock:
            return self.store.move_patient_atomic(to_bed_id, patient_id)

    def transfer_patient_best_match(
        self,
        patient_id: str,
        needed_bed_type: Optional[str] = None,
        needed_section: Optional[str] = None,
        required_features: Optional[Iterable[str]] = None,
    ) -> Optional[Tuple[Optional[str], str]]:
        """
        Transfer patient to the best available OPEN bed that matches constraints.
        Frees the old bed in the same critical section.
        Returns (from_bed_id, to_bed_id) or None if no match.
        """
        with self._lock:
            match = self.store.find_open_bed(needed_bed_type, needed_section, required_features)
            if not match:
                return None
            current = self.store.get_bed_by_patient(patient_id)
            from_id = current.id if current else None
            if from_id:
                self.store.free_bed(from_id)
            self.store.occupy_bed(match.id, patient_id)
            return (from_id, match.id)

    def swap_patients_between_beds(self, bed_id_a: str, bed_id_b: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Swap patients between two OCCUPIED beds.
        Returns (patient_a, patient_b).
        """
        with self._lock:
            a = self.store.get_bed(bed_id_a)
            b = self.store.get_bed(bed_id_b)
            if not a or not b:
                raise ValueError("One or both beds not found")
            if a.status != "OCCUPIED" or b.status != "OCCUPIED":
                raise ValueError("Both beds must be OCCUPIED to swap")
            pa, pb = a.patient_id, b.patient_id
            # swap
            self.store.occupy_bed(bed_id_a, pb)
            self.store.occupy_bed(bed_id_b, pa)
            return (pa, pb)

    # -----------------------------
    # Hooks to call from your API
    # -----------------------------
    def on_patient_added(
        self,
        patient_id: str,
        needed_bed_type: Optional[str] = None,
        needed_section: Optional[str] = None,
        required_features: Optional[Iterable[str]] = None,
        auto_assign: bool = True,
    ) -> Optional[str]:
        """
        Call when a new patient enters the system.
        Optionally try immediate assignment to an OPEN bed.
        """
        if not auto_assign:
            return None
        return self.assign_best_available(patient_id, needed_bed_type, needed_section, required_features)

    def on_patient_removed(self, patient_id: str) -> Optional[str]:
        """
        Call when a patient is discharged/removed; frees their bed if occupied.
        """
        return self.release_patient(patient_id)

    def on_patient_requirements_updated(
        self,
        patient_id: str,
        needed_bed_type: Optional[str] = None,
        needed_section: Optional[str] = None,
        required_features: Optional[Iterable[str]] = None,
        auto_transfer: bool = False,
    ) -> Optional[Tuple[Optional[str], str]]:
        """
        Call when bed requirements change.
        If auto_transfer=True, try to move them to a matching OPEN bed now.
        """
        if not auto_transfer:
            return None
        return self.transfer_patient_best_match(patient_id, needed_bed_type, needed_section, required_features)