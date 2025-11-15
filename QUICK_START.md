# Quick Start Guide

## Getting the Dashboard Running

### Step 1: Start Backend Server

Open a terminal in the `backend` folder:

```bash
cd backend
python main.py
```

You should see:
```
Starting ER Flow Dashboard Backend...
API Docs: http://localhost:8000/docs
WebSocket: ws://localhost:8000/socket.io/
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal window open** - the backend must stay running.

### Step 2: Add Sample Data (Optional but Recommended)

Open a **second terminal** in the `backend` folder:

```bash
cd backend
python add_sample_data.py
```

This creates:
- 7 sample patients with various ESI levels (persisted to database)
- Additional beds (persisted to database)

**Note**: Both patient and bed data are now persisted to SQLite and will survive backend restarts!

### Step 3: Open Frontend

**Option A: Direct File Open** (Simplest)
1. Open File Explorer
2. Navigate to: `C:\Users\beren\Desktop\hospital_flow\frontend\`
3. **Double-click `index.html`**
4. The dashboard will open in your default browser

**Option B: Local Server** (Better for development)
Open a **third terminal** in the `frontend` folder:

```bash
cd frontend
python -m http.server 8080
```

Then open your browser to: `http://localhost:8080`

## What You Should See

The dashboard shows:

### Patient Queue Section
- List of all active patients sorted by ESI priority (1-5)
- Patient details: name, chief complaint, ESI level
- Current status (REGISTERED, AWAITING_TRIAGE, etc.)
- Wait times with delay indicators
- Actions: Save status, Assign bed, Get ETA, Discharge

### Bed Overview Section
- All beds with their status (AVAILABLE/OCCUPIED)
- Bed type, section, features
- Current patient assignment

## Testing the Workflow

### 1. Register a New Patient
- Fill out the form at the top
- Select ESI level (1 = most urgent, 5 = least urgent)
- Click "Add to queue"

### 2. Update Patient Status
- Find patient in the queue table
- Use the dropdown to change status
- Click "Save status"

### 3. Assign a Bed
- Click "Assign bed" button on any patient
- System automatically finds best available bed
- Patient moves to IN_BED status

### 4. Get ETA
- Click "Get ETA" on any patient
- Shows estimated wait time in minutes

### 5. Discharge Patient
- Click "Discharge" button
- Confirm the action
- Patient marked as DISCHARGED
- Their bed automatically freed

## Troubleshooting

### Problem: Backend shows 0 patients
**Solution**: Run `python add_sample_data.py` to add sample patients

### Problem: Frontend shows "No active patients"
**Solution**:
1. Make sure backend is running on port 8000
2. Run add_sample_data.py to add patients
3. Refresh the frontend page

### Problem: Can't connect to backend
**Solution**:
1. Verify backend is running: `http://localhost:8000` should show API status
2. Check for firewall/antivirus blocking port 8000

### Problem: Bed assignment fails
**Solution**: Check that beds exist by visiting `http://localhost:8000/beds`

## Important Notes

- **All data is persistent**: Both patients and beds are stored in SQLite database (`hospital_flow.db`) and survive backend restarts.
- **Database location**: `backend/hospital_flow.db` contains all your data.
- **Multiple terminals**: You need to keep the backend terminal running while using the dashboard.

## Next Steps

1. Test the complete workflow with sample data
2. Try registering your own patients
3. Experiment with different ESI levels to see priority ordering
4. Check the delay indicators (patients exceeding wait thresholds)
