# smart_queue.py
from datetime import datetime, timezone
import heapq
import itertools
from typing import Dict, List, Optional, Tuple

from patient import Patient  # assumes patient.py is in the same folder

UTC = timezone.utc
_counter = itertools.count()  # ensures stable ordering for ties

class SmartQueue:
    """
    Priority queue for Patients using deterministic, rule-based ordering:
      1) Lower ESI first (1 is highest priority)
      2) Earlier arrival first (i.e., longer wait first)
      3) Stable order via a monotonic counter
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
        self._heap.clear()
        for p in self._patients.values():
            if p.status == "WAITING" and p.department == self.department:
                heapq.heappush(self._heap, self._key(p))

    # ------------ public API ------------
    def add_patient(self, name: str, esi: int, notes: str = "") -> str:
        p = Patient(name=name, esi=esi, department=self.department, notes=notes)
        self._patients[p.id] = p
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
        p = self._patients[patient_id]
        p.status = new_status
        p.last_assessed_ts = datetime.now(UTC)
        # Only WAITING patients live in the heap
        self._rebuild_heap()

    def next_patient(self, mark_treating: bool = True) -> Optional[Patient]:
        # Pop the highest-priority WAITING patient for this department
        while self._heap:
            _, _, _, pid = heapq.heappop(self._heap)
            p = self._patients.get(pid)
            if not p:
                continue
            if p.status == "WAITING" and p.department == self.department:
                if mark_treating:
                    p.status = "TREATING"
                    p.last_assessed_ts = datetime.now(UTC)
                return p
        return None

    def return_to_queue(self, patient_id: str) -> None:
        # e.g., after imaging/hold, put them back into WAITING
        p = self._patients[patient_id]
        p.status = "WAITING"
        p.last_assessed_ts = datetime.now(UTC)
        heapq.heappush(self._heap, self._key(p))

    def discharge(self, patient_id: str) -> None:
        p = self._patients[patient_id]
        p.status = "DISCHARGED"
        p.last_assessed_ts = datetime.now(UTC)
        # discharged patients are not in the heap

    def get_queue(self) -> List[dict]:
        # Produce a sorted snapshot for display
        waiting = [
            p for p in self._patients.values()
            if p.status == "WAITING" and p.department == self.department
        ]
        waiting.sort(key=lambda p: (p.esi, p.arrival_ts))
        return [p.to_dict() for p in waiting]
