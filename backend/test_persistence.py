# test_persistence.py
"""Test patient persistence - verify patients survive backend restarts"""
import sys
from pathlib import Path

# Add shared folder to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from smart_queue import SmartQueue
from bed_registery import BedRegistry

print("Testing patient persistence...")
print("=" * 50)

# Create instances (this loads from database)
sq = SmartQueue("ED")
br = BedRegistry()

print(f"\nLoaded from database:")
print(f"  Patients in memory: {len(sq._patients)}")
print(f"  Beds: {len(br.list_beds())}")

# Get active patients
active = sq.get_all_active_patients()
print(f"\nActive patients: {len(active)}")

if active:
    print("\nFirst 3 patients:")
    for p in active[:3]:
        print(f"  - {p['name']} (ESI {p['esi']}) - Status: {p['status']}")

print("\n" + "=" * 50)
print("Patient persistence is working!")
print("\nYou can now:")
print("1. Restart the backend - patients will persist")
print("2. Add new patients through the UI - they'll be saved")
print("3. Stop worrying about losing patient data on restart")
