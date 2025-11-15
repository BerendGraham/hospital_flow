# main.py
"""
ER Flow Dashboard - FastAPI Backend with Socket.IO
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import socketio
import sys
from pathlib import Path

# Add shared folder to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from smart_queue import SmartQueue
from bed_registery import BedRegistry

# ============================================================================
# Initialize FastAPI and Socket.IO
# ============================================================================

app = FastAPI(
    title="ER Flow Dashboard API",
    description="Real-time ER patient flow tracking",
    version="1.0.0"
)

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO server for real-time updates
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)
socket_app = socketio.ASGIApp(sio, app)

# ============================================================================
# Global State (In-Memory for now)
# ============================================================================

smart_queue = SmartQueue(department="ED")
bed_registry = BedRegistry()

# ============================================================================
# Pydantic Models (Request/Response schemas)
# ============================================================================

class PatientCreate(BaseModel):
    name: str
    esi: int  # 1-5
    chief_complaint: str
    age: int
    gender: str
    notes: str = ""

class PatientStatusUpdate(BaseModel):
    new_status: str

class BedAssignment(BaseModel):
    bed_id: str

class BedCreate(BaseModel):
    bed_type: str
    section: str
    features: List[str] = []

# ============================================================================
# REST API Endpoints - Patients
# ============================================================================

@app.get("/")
def root():
    return {
        "service": "ER Flow Dashboard API",
        "status": "running",
        "patients_in_queue": len(smart_queue._patients),
        "total_beds": len(bed_registry.store.list_beds())
    }

@app.get("/api/patients")
def get_all_patients():
    """Get all active patients"""
    return smart_queue.get_all_active_patients()

@app.get("/api/patients/delayed")
def get_delayed_patients():
    """Get patients exceeding ESI wait thresholds"""
    return smart_queue.get_delayed_patients()

@app.get("/api/patients/status/{status}")
def get_patients_by_status(status: str):
    """Get patients by status (e.g., AWAITING_TRIAGE, IN_BED)"""
    return smart_queue.get_patients_by_status(status)

@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: str):
    """Get single patient details"""
    patient = smart_queue.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient.to_dict()

@app.post("/api/patients")
async def create_patient(patient: PatientCreate):
    """Register a new patient"""
    patient_id = smart_queue.add_patient(
        name=patient.name,
        esi=patient.esi,
        chief_complaint=patient.chief_complaint,
        age=patient.age,
        gender=patient.gender,
        notes=patient.notes
    )

    patient_data = smart_queue.get(patient_id).to_dict()

    # Broadcast to all connected clients
    await sio.emit('patient:created', patient_data)

    return patient_data

@app.patch("/api/patients/{patient_id}/status")
async def update_patient_status(patient_id: str, data: PatientStatusUpdate):
    """Update patient status"""
    patient = smart_queue.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    smart_queue.update_status(patient_id, data.new_status)
    patient_data = patient.to_dict()

    # Broadcast update
    await sio.emit('patient:updated', patient_data)

    return patient_data

@app.patch("/api/patients/{patient_id}/bed")
async def assign_bed_to_patient(patient_id: str, data: BedAssignment):
    """Assign bed to patient"""
    patient = smart_queue.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    bed = bed_registry.get(data.bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    # Assign bed (SmartQueue updates patient, BedRegistry updates bed)
    smart_queue.assign_bed(patient_id, data.bed_id)
    bed_registry.occupy_bed(data.bed_id, patient_id)

    patient_data = patient.to_dict()
    bed_data = bed_registry.get(data.bed_id).to_dict()

    # Broadcast both updates
    await sio.emit('patient:updated', patient_data)
    await sio.emit('bed:updated', bed_data)

    return patient_data

# ============================================================================
# REST API Endpoints - Beds
# ============================================================================

@app.get("/api/beds")
def get_all_beds(status: Optional[str] = None):
    """Get all beds, optionally filter by status"""
    return bed_registry.list_beds(status=status)

@app.get("/api/beds/{bed_id}")
def get_bed(bed_id: str):
    """Get single bed details"""
    bed = bed_registry.get(bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")
    return bed.to_dict()

@app.post("/api/beds")
async def create_bed(bed: BedCreate):
    """Add a new bed to inventory"""
    bed_id = bed_registry.add_bed(
        bed_type=bed.bed_type,
        section=bed.section,
        features=bed.features
    )

    bed_data = bed_registry.get(bed_id).to_dict()

    # Broadcast new bed
    await sio.emit('bed:created', bed_data)

    return bed_data

@app.patch("/api/beds/{bed_id}/free")
async def free_bed(bed_id: str):
    """Mark bed as available (free it)"""
    bed = bed_registry.get(bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="Bed not found")

    bed_registry.free_bed(bed_id)
    bed_data = bed_registry.get(bed_id).to_dict()

    # Broadcast update
    await sio.emit('bed:updated', bed_data)

    return bed_data

# ============================================================================
# Socket.IO Events
# ============================================================================

@sio.event
async def connect(sid, environ):
    """Client connected - send full state snapshot"""
    print(f"[OK] Client connected: {sid}")

    await sio.emit('state:snapshot', {
        'patients': smart_queue.get_all_active_patients(),
        'beds': bed_registry.list_beds()
    }, to=sid)

@sio.event
def disconnect(sid):
    """Client disconnected"""
    print(f"[DISCONNECT] Client disconnected: {sid}")

@sio.event
async def update_patient_status_ws(sid, data):
    """Handle status update from client via WebSocket"""
    patient_id = data.get('patient_id')
    new_status = data.get('new_status')

    if not patient_id or not new_status:
        await sio.emit('error', {'message': 'Missing fields'}, to=sid)
        return

    patient = smart_queue.get(patient_id)
    if not patient:
        await sio.emit('error', {'message': 'Patient not found'}, to=sid)
        return

    smart_queue.update_status(patient_id, new_status)
    await sio.emit('patient:updated', patient.to_dict())

# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("Starting ER Flow Dashboard Backend...")
    print("API Docs: http://localhost:8000/docs")
    print("WebSocket: ws://localhost:8000/socket.io/")
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
