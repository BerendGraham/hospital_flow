# ER Flow Dashboard - Backend

FastAPI + Socket.IO backend for real-time ER patient flow tracking.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python main.py
```

Server runs at: `http://localhost:8000`

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## REST Endpoints

### Patients
- `GET /api/patients` - Get all active patients
- `GET /api/patients/delayed` - Get delayed patients (exceeding ESI thresholds)
- `GET /api/patients/status/{status}` - Get patients by status
- `GET /api/patients/{id}` - Get specific patient
- `POST /api/patients` - Create new patient
- `PATCH /api/patients/{id}/status` - Update patient status
- `PATCH /api/patients/{id}/bed` - Assign bed to patient

### Beds
- `GET /api/beds` - Get all beds (optionally filter by status)
- `GET /api/beds/{id}` - Get specific bed
- `POST /api/beds` - Create new bed
- `PATCH /api/beds/{id}/free` - Free a bed

## Socket.IO Events

### Server → Client
- `state:snapshot` - Full state on connect (patients + beds)
- `patient:created` - New patient added
- `patient:updated` - Patient status/bed changed
- `bed:created` - New bed added
- `bed:updated` - Bed status changed

### Client → Server
- `patient:update_status` - Request status change
  ```json
  { "patient_id": "...", "new_status": "TRIAGED" }
  ```

## Example Usage

### Create a Patient
```bash
curl -X POST http://localhost:8000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "esi": 2,
    "chief_complaint": "Chest pain",
    "age": 55,
    "gender": "M"
  }'
```

### Create a Bed
```bash
curl -X POST http://localhost:8000/api/beds \
  -H "Content-Type: application/json" \
  -d '{
    "bed_type": "ED",
    "section": "A3",
    "features": ["cardiac_monitor"]
  }'
```

### Get All Patients
```bash
curl http://localhost:8000/api/patients
```

## Architecture

```
backend/main.py
    ↓ imports
shared/
    ├── smart_queue.py    (business logic)
    ├── bed_registery.py  (business logic)
    └── bed_db.py         (SQLite persistence)
```

All patient and bed management logic lives in `/shared`.
Backend is just the web API layer.
