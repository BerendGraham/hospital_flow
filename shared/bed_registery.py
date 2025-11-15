# bed_registery.py
"""
High-level bed management service.

This module defines BedRegistry, which is the API the rest of your
backend should use to work with beds. It delegates all persistence
to SQLiteBedStore in beds_db.py, so every change is mirrored to the
SQLite database (hospital_beds.db by default).
"""

import threading
from typing import Any, Dict, Iterable, List, Optional, Tuple

from bed import Bed              # <-- adjust to your real import path if needed
from beds_DB import SQLiteBedStore  # <-- adjust to your real import path if needed


class BedRegistry:
    """
    Public service API for bed management.

    Key ideas:
    - The actual data is stored in SQLite via SQLiteBedStore.
    - BedRegistry adds concurrency safety and higher-level operations
      like "assign the best available bed to this patient".
    """

    def __init__(self, store: Optional[SQLiteBedStore] = None) -> None:
        # You can inject a custom store for tests; otherwise use the default.
        self.store = store or SQLiteBedStore()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Basic CRUD-like operations
    # ------------------------------------------------------------------
    def add_bed(
        self,
        bed_type: str,
        section: str,
        features: Iterable[str] = (),
    ) -> str:
        """
        Create a new Bed, persist it, and return the bed's id.
        """
        bed = Bed(bed_type=bed_type, section=section, features=set(features))
        with self._lock:
            self.store.insert_bed(bed)
        return bed.id

    def upsert_bed(self, bed: Bed) -> str:
        """
        Insert or update a Bed object.
        If the id already exists, we overwrite that row.
        """
        with self._lock:
            existing = self.store.get_bed(bed.id)
            if existing:
                self.store.update_bed(bed)
            else:
                self.store.insert_bed(bed)
        return bed.id

    def list_beds(
        self,
        status: Optional[str] = None,
        bed_type: Optional[str] = None,
        section: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return beds as a list of plain dicts, ready to JSON-serialize.
        """
        with self._lock:
            beds = self.store.list_beds(
                status=status,
                bed_type=bed_type,
                section=section,
            )
        return [b.to_dict() for b in beds]

    def get(self, bed_id: str) -> Optional[Bed]:
        """
        Return the Bed object for a given id, or None.
        """
        with self._lock:
            return self.store.get_bed(bed_id)

    # ------------------------------------------------------------------
    # Status changes
    # ------------------------------------------------------------------
    def free_bed(self, bed_id: str) -> None:
        """
        Mark a bed as OPEN and clear any patient.
        """
        with self._lock:
            bed = self.store.get_bed(bed_id)
            if not bed:
                return
            bed.status = "OPEN"
            bed.patient_id = None
            self.store.update_bed(bed)

    def hold_bed(
        self,
        bed_id: str,
        patient_id: Optional[str] = None,
    ) -> None:
        """
        Mark a bed as HELD, optionally tying it to a patient.
        """
        with self._lock:
            bed = self.store.get_bed(bed_id)
            if not bed:
                return
            bed.status = "HELD"
            bed.patient_id = patient_id
            self.store.update_bed(bed)

    def occupy_bed(self, bed_id: str, patient_id: str) -> None:
        """
        Mark the bed as OCCUPIED by the given patient.

        If the patient already occupies another bed, that bed is freed
        first, so each patient can only have at most one bed.
        """
        with self._lock:
            # If patient already has a bed, free it
            current = self.store.get_bed_by_patient(patient_id)
            if current and current.id != bed_id:
                current.status = "OPEN"
                current.patient_id = None
                self.store.update_bed(current)

            bed = self.store.get_bed(bed_id)
            if not bed:
                return
            bed.status = "OCCUPIED"
            bed.patient_id = patient_id
            self.store.update_bed(bed)

    # ------------------------------------------------------------------
    # Matching & assignment
    # ------------------------------------------------------------------
    def assign_best_available(
        self,
        patient_id: str,
        needed_bed_type: Optional[str] = None,
        needed_section: Optional[str] = None,
        required_features: Optional[Iterable[str]] = None,
    ) -> Optional[str]:
        """
        Assign the first OPEN bed that matches the constraints.

        Returns the bed_id or None if no matching open bed is found.
        """
        with self._lock:
            match = self.store.find_open_bed(
                needed_bed_type=needed_bed_type,
                needed_section=needed_section,
                required_features=required_features,
            )
            if not match:
                return None

            # Free any current bed for this patient (single-occupancy invariant)
            current = self.store.get_bed_by_patient(patient_id)
            if current:
                current.status = "OPEN"
                current.patient_id = None
                self.store.update_bed(current)

            # Occupy the new bed
            match.status = "OCCUPIED"
            match.patient_id = patient_id
            self.store.update_bed(match)
            return match.id

    def release_patient(self, patient_id: str) -> Optional[str]:
        """
        Free whatever bed this patient is currently occupying.
        Returns the bed id that was freed, or None if they had no bed.
        """
        with self._lock:
            bed = self.store.get_bed_by_patient(patient_id)
            if not bed:
                return None
            bed.status = "OPEN"
            bed.patient_id = None
            self.store.update_bed(bed)
            return bed.id

    def transfer_patient_best_match(
        self,
        patient_id: str,
        needed_bed_type: Optional[str] = None,
        needed_section: Optional[str] = None,
        required_features: Optional[Iterable[str]] = None,
    ) -> Optional[Tuple[Optional[str], str]]:
        """
        Transfer a patient to a better-matching OPEN bed.

        Frees the old bed and occupies the new one atomically.
        Returns (from_bed_id, to_bed_id) or None if no match exists.
        """
        with self._lock:
            match = self.store.find_open_bed(
                needed_bed_type=needed_bed_type,
                needed_section=needed_section,
                required_features=required_features,
            )
            if not match:
                return None

            current = self.store.get_bed_by_patient(patient_id)
            from_id: Optional[str] = None
            if current:
                from_id = current.id
                current.status = "OPEN"
                current.patient_id = None
                self.store.update_bed(current)

            match.status = "OCCUPIED"
            match.patient_id = patient_id
            self.store.update_bed(match)

            return (from_id, match.id)

    def swap_patients_between_beds(
        self,
        bed_id_a: str,
        bed_id_b: str,
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Swap patients between two beds.

        Returns (patient_in_a, patient_in_b) after the swap.
        """
        with self._lock:
            a = self.store.get_bed(bed_id_a)
            b = self.store.get_bed(bed_id_b)
            if not a or not b:
                return (None, None)

            pa, pb = a.patient_id, b.patient_id
            a.patient_id, b.patient_id = pb, pa

            # Keep status consistent: a bed with a patient is OCCUPIED,
            # an empty bed is OPEN.
            a.status = "OCCUPIED" if a.patient_id else "OPEN"
            b.status = "OCCUPIED" if b.patient_id else "OPEN"

            self.store.update_bed(a)
            self.store.update_bed(b)
            return (pa, pb)

    # ------------------------------------------------------------------
    # Hooks to call from your API (optional helpers)
    # ------------------------------------------------------------------
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

        If auto_assign=True, immediately try to place them in a matching
        OPEN bed. Returns the assigned bed_id or None.
        """
        if not auto_assign:
            return None
        return self.assign_best_available(
            patient_id,
            needed_bed_type=needed_bed_type,
            needed_section=needed_section,
            required_features=required_features,
        )

    def on_patient_removed(self, patient_id: str) -> Optional[str]:
        """
        Call when a patient is discharged/removed; frees their bed if any.
        Returns the bed id that was freed, or None.
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
        Call when bed requirements (e.g., ICU vs ED section) change.

        If auto_transfer=True, try to move the patient immediately to a
        matching OPEN bed. Returns (from_bed_id, to_bed_id) or None.
        """
        if not auto_transfer:
            return None
        return self.transfer_patient_best_match(
            patient_id,
            needed_bed_type=needed_bed_type,
            needed_section=needed_section,
            required_features=required_features,
        )
