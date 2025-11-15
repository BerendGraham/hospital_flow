from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from ..schemas.patient import PatientCreate, PatientRead, UpdateESI, UpdateStatus, ETAResponse
from ..services.state import get_queue

router = APIRouter(tags=["v1"])

# ---------- Create a patient ----------
@router.post("/patients", response_model=PatientRead)
def add_patient(payload: PatientCreate):
    sq = get_queue(payload.department)
    pid = sq.add_patient(name=payload.name, esi=payload.esi, notes=payload.notes or "")
    return sq.get(pid).to_dict()

# ---------- Get queue snapshot ----------
@router.get("/queue", response_model=List[PatientRead])
def get_queue_snapshot(department: str = Query("ED")):
    return get_queue(department).get_queue()

# ---------- Get a specific patient ----------
@router.get("/patients/{patient_id}", response_model=PatientRead)
def get_patient(patient_id: str, department: str = Query("ED")):
    sq = get_queue(department)
    p = sq.get(patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Patient not found")
    return p.to_dict()

# ---------- Update ESI ----------
@router.patch("/patients/{patient_id}/esi", response_model=PatientRead)
def update_patient_esi(patient_id: str, payload: UpdateESI, department: str = Query("ED")):
    sq = get_queue(department)
    if not sq.get(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    sq.update_esi(patient_id, payload.esi)
    return sq.get(patient_id).to_dict()

# ---------- Update Status ----------
@router.patch("/patients/{patient_id}/status", response_model=PatientRead)
def update_patient_status(patient_id: str, payload: UpdateStatus, department: str = Query("ED")):
    sq = get_queue(department)
    if not sq.get(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    sq.update_status(patient_id, payload.status)
    return sq.get(patient_id).to_dict()

# ---------- Assign next patient ----------
@router.post("/assign", response_model=Optional[PatientRead])
def assign_next(department: str = Query("ED")):
    p = get_queue(department).next_patient()
    return p.to_dict() if p else None

# ---------- Return patient to queue ----------
@router.post("/return/{patient_id}", response_model=PatientRead)
def return_to_queue(patient_id: str, department: str = Query("ED")):
    sq = get_queue(department)
    if not sq.get(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    sq.return_to_queue(patient_id)
    return sq.get(patient_id).to_dict()

# ---------- Discharge patient ----------
@router.post("/discharge/{patient_id}", response_model=PatientRead)
def discharge(patient_id: str, department: str = Query("ED")):
    sq = get_queue(department)
    if not sq.get(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    sq.discharge(patient_id)
    return sq.get(patient_id).to_dict()

# ---------- Estimate ETA ----------
@router.get("/eta/{patient_id}", response_model=ETAResponse)
def eta(patient_id: str, department: str = Query("ED"),
        rooms_available: int = Query(1, ge=1),
        avg_service_min: int = Query(20, ge=1)):
    sq = get_queue(department)
    if not sq.get(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
    return ETAResponse(
        patient_id=patient_id,
        eta_minutes=sq.estimate_wait_minutes(patient_id, rooms_available, avg_service_min)
    )
