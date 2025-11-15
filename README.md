# ER Patient Flow Dashboard

Real-time emergency room patient tracking system that eliminates communication silos between ER staff.

## Overview

This dashboard provides a centralized view of all ER patients with ESI-based priority queuing, automatic bed assignment, and real-time status tracking.

### Core Features

- **Single dashboard** showing all patients and their current status
- **One-click status transitions** through the ER workflow
- **Real-time updates** via WebSocket (Socket.IO)
- **ESI-based priority** (Emergency Severity Index 1-5)
- **Automatic bed assignment** with feature matching
- **Delay alerts** when patients exceed wait thresholds
- **Bed availability tracking** with SQLite persistence

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Add Sample Data (Optional)

```bash
cd backend
python add_sample_data.py
```

### 3. Start Backend

```bash
cd backend
python main.py
```

Backend runs at `http://localhost:8000`

### 4. Open Frontend

Open `frontend/index.html` in your browser, or:

```bash
cd frontend
python -m http.server 8080
```

Visit `http://localhost:8080`

## Project Structure

```
hospital_flow/
├── shared/              # Business logic (Python)
│   ├── patient.py      # Patient data model
│   ├── bed.py          # Bed data model
│   ├── smart_queue.py  # ESI-based priority queue
│   ├── bed_registery.py # Bed management
│   └── bed_db.py       # SQLite persistence
│
├── backend/            # FastAPI web server
│   ├── main.py         # API + Socket.IO server
│   ├── requirements.txt
│   └── add_sample_data.py
│
└── frontend/           # Vanilla JavaScript UI
    ├── index.html
    ├── app.js
    └── styles.css
```

## Workflow

```
Patient Arrives
    ↓
REGISTERED → AWAITING_TRIAGE → TRIAGED → AWAITING_BED → IN_BED
    ↓
AWAITING_DISPOSITION → DISCHARGED / ADMITTED
```

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Socket.IO** - Real-time bidirectional communication
- **SQLite** - Persistent bed storage
- **Pydantic** - Data validation

### Frontend
- **Vanilla JavaScript** - No framework dependencies
- **HTML5 + CSS3** - Modern, responsive design
- **Fetch API** - RESTful communication

### Shared Core
- **SmartQueue** - Thread-safe ESI-based priority queue
- **BedRegistry** - Intelligent bed matching and assignment
- **SQLite** - Simple, portable database

## ESI (Emergency Severity Index)

| Level | Description | Target Time |
|-------|-------------|-------------|
| 1 | Resuscitation | Immediate |
| 2 | Emergent | 10 minutes |
| 3 | Urgent | 30 minutes |
| 4 | Less urgent | 60 minutes |
| 5 | Non-urgent | 120 minutes |

## API Documentation

Interactive API docs available at: `http://localhost:8000/docs`

### Key Endpoints

**Patients:**
- `GET /queue` - Get all active patients
- `POST /patients` - Register new patient
- `PATCH /patients/{id}/status` - Update patient status
- `GET /eta/{id}` - Calculate wait time estimate
- `POST /discharge/{id}` - Discharge patient

**Beds:**
- `GET /beds` - Get all beds
- `POST /beds/assign_best` - Auto-assign best matching bed

**WebSocket Events:**
- `state:snapshot` - Full state on connect
- `patient:created` - New patient added
- `patient:updated` - Patient changed
- `bed:updated` - Bed status changed

## Features in Detail

### Smart Queue
- Automatic ESI-based prioritization
- Stable sorting (FIFO within same ESI)
- Real-time delay detection
- Complete timestamp tracking

### Bed Registry
- Thread-safe concurrent access
- Feature-based matching (isolation, cardiac monitor, etc.)
- Automatic assignment algorithms
- SQLite persistence (survives restarts)

### Patient Tracking
- Full workflow stage history
- Time-in-status calculations
- Automatic bed assignment on status change
- Audit trail for compliance

## Development

### Run Tests

```bash
cd backend
python test_backend.py
```

### Add More Beds

```bash
curl -X POST http://localhost:8000/api/beds \
  -H "Content-Type: application/json" \
  -d '{"bed_type": "ED", "section": "A1", "features": ["cardiac_monitor"]}'
```

### Add Patient via API

```bash
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Patient",
    "esi": 3,
    "chief_complaint": "Chest pain",
    "age": 55,
    "gender": "M"
  }'
```

## Configuration

### Backend Port
Edit `backend/main.py`:
```python
uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)
```

### Database Location
Edit `shared/bed_db.py`:
```python
DB_PATH = "hospital_flow.db"  # Change path as needed
```

### Frontend API URL
Edit `frontend/app.js`:
```javascript
const API_BASE = "http://localhost:8000";
```

## Future Enhancements

- [ ] User authentication and roles
- [ ] Historical analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Integration with EMR systems
- [ ] Multi-hospital support
- [ ] Predictive wait time modeling
- [ ] SMS/push notifications for staff

## License

MIT

## Contributors

Built for ER workflow optimization.
