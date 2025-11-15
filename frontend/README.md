# ER Flow Dashboard - Frontend

Real-time ER patient flow tracking dashboard built with vanilla JavaScript.

## Features

### Patient Management
- **Register new patients** with ESI level, chief complaint, demographics
- **View live queue** sorted by ESI priority (1-5)
- **Update patient status** through workflow stages
- **Track wait times** with visual delay indicators
- **Calculate ETA** for each patient

### Bed Management
- **View bed availability** in real-time
- **Auto-assign beds** to patients (matches by type, section, features)
- **Track bed occupancy**
- **Free beds** on patient discharge

### Real-Time Updates
- Automatic polling every 10 seconds for patients
- Automatic polling every 30 seconds for beds
- Socket.IO ready (for instant updates when connected)

## How to Run

### Option 1: Direct File Open
Simply open `index.html` in your web browser.

### Option 2: Local Server (Recommended)
```bash
# Python 3
python -m http.server 8080

# Python 2
python -m SimpleHTTPServer 8080

# Node.js
npx http-server -p 8080
```

Then visit: `http://localhost:8080`

## Configuration

Edit `app.js` to change the backend URL:

```javascript
const API_BASE = "http://localhost:8000"; // Change if backend runs elsewhere
```

## User Guide

### 1. Register a Patient
1. Fill out the "Register New Patient" form
2. Select ESI level (1 = most urgent, 5 = least urgent)
3. Enter chief complaint and demographics
4. Click "Add to queue"

### 2. Manage Patient Status
1. Find patient in the live queue table
2. Use the status dropdown to update their stage:
   - REGISTERED → Patient just arrived
   - AWAITING_TRIAGE → Waiting to be seen by triage nurse
   - TRIAGED → Triage complete, waiting for bed
   - AWAITING_BED → Ready for bed assignment
   - IN_BED → Currently receiving treatment
   - AWAITING_DISPOSITION → Care complete, awaiting decision
   - DISCHARGED → Released from ER
   - ADMITTED → Moving to inpatient unit
3. Click "Save status" to update

### 3. Assign a Bed
1. Click "Assign bed" on any patient
2. System automatically finds best available bed
3. Patient moves to IN_BED status
4. Bed marked as OCCUPIED

### 4. Check ETA
1. Click "Get ETA" for any patient
2. System calculates estimated wait time based on:
   - Patients ahead in queue
   - ESI priority
   - Average service time

### 5. Discharge Patient
1. Click "Discharge" button
2. Confirm the action
3. Patient marked as DISCHARGED
4. Their bed automatically freed

## ESI Color Coding

- **ESI 1** (Red) - Resuscitation, immediate
- **ESI 2** (Orange) - Emergent, 10 minutes
- **ESI 3** (Yellow) - Urgent, 30 minutes
- **ESI 4** (Green) - Less urgent, 60 minutes
- **ESI 5** (Blue) - Non-urgent, 120 minutes

## Delay Indicators

Patients exceeding their ESI wait threshold are highlighted in red.

## Technical Details

- **No build step required** - Pure vanilla JavaScript
- **No dependencies** - Just HTML, CSS, JavaScript
- **Modern browser required** - Uses ES6+ features
- **Responsive design** - Works on desktop and tablets

## File Structure

```
frontend/
├── index.html      # Main dashboard
├── app.js          # Application logic
├── styles.css      # Styling
└── README.md       # This file
```

## API Integration

The frontend expects these backend endpoints:

- `GET /queue?department=ED` - Get all active patients
- `POST /patients` - Create new patient
- `PATCH /patients/{id}/status` - Update status
- `GET /eta/{id}` - Get estimated wait time
- `POST /discharge/{id}` - Discharge patient
- `GET /beds` - Get all beds
- `POST /beds/assign_best` - Auto-assign bed

## Customization

### Change Polling Intervals
Edit the bottom of `app.js`:
```javascript
setInterval(loadQueue, 10_000);  // Change 10000 to desired ms
setInterval(loadBeds, 30_000);   // Change 30000 to desired ms
```

### Add More Departments
Edit the department dropdowns in `index.html` and add corresponding backend support.

### Modify ESI Thresholds
Wait time thresholds are calculated by the backend. Delay indicators update automatically.
