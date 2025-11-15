# ER Flow Dashboard - Setup Guide

## Quick Start

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs at: `http://localhost:8000`

### 2. Open the Frontend

```bash
cd frontend
# Open index.html in your browser
# Or use a simple server:
python -m http.server 8080
```

Frontend runs at: `http://localhost:8080`

## What's Included

### Backend (FastAPI + Socket.IO)
- **Patients API**: Create, update status, assign beds
- **Beds API**: View availability, assign to patients
- **Real-time updates**: Socket.IO broadcasts changes
- **ETA calculation**: Estimate wait times
- **Auto bed assignment**: Match patients to available beds

### Frontend (Vanilla JavaScript)
- **Patient registration form**
- **Live queue table** (ESI-based priority)
- **Bed overview board**
- **Status updates** via dropdown
- **One-click bed assignment**
- **ETA calculation**
- **Discharge workflow**

### Shared Core
- **SmartQueue**: ESI-based priority queue with delay detection
- **BedRegistry**: Thread-safe bed management with SQLite persistence
- **Patient model**: Full ER workflow tracking
- **Bed model**: Features, sections, occupancy

## API Endpoints

### Patients
- `GET /queue?department=ED` - Get all active patients
- `POST /patients` - Create new patient
- `PATCH /patients/{id}/status` - Update patient status
- `GET /eta/{id}` - Get estimated wait time
- `POST /discharge/{id}` - Discharge patient

### Beds
- `GET /beds` - Get all beds
- `POST /beds/assign_best` - Auto-assign best available bed

## Features

- ESI-based priority (1 = most urgent, 5 = least urgent)
- Real-time delay detection (patients exceeding ESI thresholds)
- Automatic bed matching by type, section, and features
- Complete audit trail (SQLite database)
- Thread-safe concurrent access
- Live updates (polling + Socket.IO ready)

## Next Steps

1. **Add sample data** - Create test patients and beds
2. **Test the workflow** - Register patient → Assign bed → Discharge
3. **Customize** - Adjust ESI thresholds, add more bed features

## Troubleshooting

**Backend won't start:**
- Check Python version (3.8+)
- Install dependencies: `pip install -r requirements.txt`

**Frontend can't connect:**
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`

**No beds available:**
- Create beds first using the bed API or directly in database
