# smart_queue.py
from datetime import datetime, timezone
import heapq
import itertools
from typing import Dict, List, Optional, Tuple

from patient import Patient, PatientStatus  # assumes patient.py is in the same folder

UTC = timezone.utc
_counter = itertools.count()  # ensures stable ordering for ties

class SmartQueue:
    """
    Priority queue for Patients using deterministic, rule-based ordering:
      1) Lower ESI first (1 is highest priority)
      2) Earlier arrival first (i.e., longer wait first)
      3) Stable order via a monotonic counter

    Tracks all active patients (not just waiting for triage) for dashboard display.
    """
    def __init__(self, department: str = "ED"):
        self.department = department
        self._heap: List[Tuple[int, datetime, int, str]] = []  # (esi, arrival_ts, counter, patient_id)
        self._patients: Dict[str, Patient] = {}

    # ------------ internal helpers ------------
    def _key(self, p: Patient) -> Tuple[int, datetime, int, str]:
        # Lower ESI first, then earlier arrival, then stable counter, then id
        return (p.esi, p.arrival_ts, next(_counter), p.id)

    def _rebuild_heap(self) -> None:
        """Rebuild heap with patients awaiting triage"""
        self._heap.clear()
        for p in self._patients.values():
            if p.status == PatientStatus.AWAITING_TRIAGE.value and p.department == self.department:
                heapq.heappush(self._heap, self._key(p))

    # ------------ public API ------------
    def add_patient(self, name: str, esi: int, chief_complaint: str, age: int, gender: str, notes: str = "") -> str:
        """Register a new patient in the ER"""
        p = Patient(
            name=name,
            esi=esi,
            chief_complaint=chief_complaint,
            age=age,
            gender=gender,
            department=self.department,
            notes=notes
        )
        self._patients[p.id] = p
        # Add to heap since default status is AWAITING_TRIAGE
        heapq.heappush(self._heap, self._key(p))
        return p.id

    def get(self, patient_id: str) -> Optional[Patient]:
        return self._patients.get(patient_id)

    def update_esi(self, patient_id: str, new_esi: int) -> None:
        p = self._patients[patient_id]
        p.esi = new_esi
        p.last_assessed_ts = datetime.now(UTC)
        self._rebuild_heap()

    def update_status(self, patient_id: str, new_status: str) -> None:
        """Update patient status and record timestamp"""
        p = self._patients[patient_id]
        p.update_status(new_status)
        # Only AWAITING_TRIAGE patients live in the heap
        self._rebuild_heap()

    def assign_bed(self, patient_id: str, bed_id: str) -> None:
        """Assign a bed to a patient and update status to IN_BED"""
        p = self._patients[patient_id]
        p.bed_id = bed_id
        p.update_status(PatientStatus.IN_BED.value)
        self._rebuild_heap()

    def assign_nurse(self, patient_id: str, nurse_id: str) -> None:
        """Assign a nurse to a patient"""
        p = self._patients[patient_id]
        p.assigned_nurse_id = nurse_id

    def assign_physician(self, patient_id: str, physician_id: str) -> None:
        """Assign a physician to a patient"""
        p = self._patients[patient_id]
        p.assigned_physician_id = physician_id

    def next_awaiting_triage(self) -> Optional[Patient]:
        """Get the highest-priority patient awaiting triage without changing status"""
        while self._heap:
            _, _, _, pid = heapq.heappop(self._heap)
            p = self._patients.get(pid)
            if not p:
                continue
            if p.status == PatientStatus.AWAITING_TRIAGE.value and p.department == self.department:
                # Don't change status, just return the patient
                # Re-add to heap since we're just peeking
                heapq.heappush(self._heap, self._key(p))
                return p
        return None

    def get_all_active_patients(self) -> List[dict]:
        """Get all patients except DISCHARGED, ADMITTED, or LWBS - sorted by ESI then arrival"""
        inactive_statuses = {
            PatientStatus.DISCHARGED.value,
            PatientStatus.ADMITTED.value,
            PatientStatus.LEFT_WITHOUT_BEING_SEEN.value
        }
        active = [
            p for p in self._patients.values()
            if p.status not in inactive_statuses and p.department == self.department
        ]
        active.sort(key=lambda p: (p.esi, p.arrival_ts))
        return [p.to_dict() for p in active]

    def get_patients_by_status(self, status: str) -> List[dict]:
        """Get all patients with a specific status"""
        patients = [
            p for p in self._patients.values()
            if p.status == status and p.department == self.department
        ]
        patients.sort(key=lambda p: (p.esi, p.arrival_ts))
        return [p.to_dict() for p in patients]

    def get_delayed_patients(self) -> List[dict]:
        """Get patients exceeding ESI wait time thresholds"""
        delayed = [
            p for p in self._patients.values()
            if p.is_delayed() and p.department == self.department
        ]
        delayed.sort(key=lambda p: (p.esi, p.arrival_ts))
        return [p.to_dict() for p in delayed]

    def get_queue(self) -> List[dict]:
        """Legacy method - returns patients awaiting triage"""
        return self.get_patients_by_status(PatientStatus.AWAITING_TRIAGE.value)

    def estimate_wait_minutes(self, patient_id: str, rooms_available: int, avg_service_min: int) -> int:
        """
        Very rough ETA:
        - Build the triage queue (patients AWAITING_TRIAGE in this department),
          sorted by ESI then arrival.
        - Calculate how many people are ahead of this patient.
        - ETA ~= (people_ahead / rooms_available) * avg_service_min
        """
        rooms_available = max(1, int(rooms_available))
        avg_service_min = max(1, int(avg_service_min))

        queue = [
            p for p in self._patients.values()
            if p.status == PatientStatus.AWAITING_TRIAGE.value and p.department == self.department
        ]
        queue.sort(key=lambda p: (p.esi, p.arrival_ts))

        for index, p in enumerate(queue):
            if p.id == patient_id:
                people_ahead = index
                eta = int((people_ahead * avg_service_min) / rooms_available)
                return max(0, eta)

        # If they aren't in the waiting queue, ETA is 0 for now
        return 0

