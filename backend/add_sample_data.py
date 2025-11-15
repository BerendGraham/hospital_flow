# add_sample_data.py
"""
Add sample patients and beds to the ER Flow Dashboard for testing
"""
import sys
from pathlib import Path

# Add shared folder to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from smart_queue import SmartQueue
from bed_registery import BedRegistry

print("Adding sample data to ER Flow Dashboard...")
print("=" * 50)

# Create instances
queue = SmartQueue(department="ED")
beds = BedRegistry()

# Add sample beds
print("\nAdding beds...")
bed_data = [
    {"bed_type": "ED", "section": "A1", "features": ["cardiac_monitor"]},
    {"bed_type": "ED", "section": "A2", "features": []},
    {"bed_type": "ED", "section": "A3", "features": ["isolation"]},
    {"bed_type": "ED", "section": "B1", "features": ["cardiac_monitor"]},
    {"bed_type": "ED", "section": "B2", "features": []},
    {"bed_type": "ICU", "section": "ICU-1", "features": ["ventilator", "cardiac_monitor"]},
    {"bed_type": "ICU", "section": "ICU-2", "features": ["ventilator"]},
]

for b in bed_data:
    bed_id = beds.add_bed(
        bed_type=b["bed_type"],
        section=b["section"],
        features=b["features"]
    )
    print(f"  Created bed: {b['section']} ({b['bed_type']}) - ID: {bed_id[:8]}...")

# Add sample patients
print("\nAdding patients...")
patient_data = [
    {"name": "John Smith", "esi": 2, "chief_complaint": "Chest pain", "age": 65, "gender": "M"},
    {"name": "Mary Johnson", "esi": 1, "chief_complaint": "Severe trauma", "age": 42, "gender": "F"},
    {"name": "Robert Brown", "esi": 3, "chief_complaint": "Abdominal pain", "age": 55, "gender": "M"},
    {"name": "Patricia Davis", "esi": 4, "chief_complaint": "Ankle sprain", "age": 28, "gender": "F"},
    {"name": "Michael Wilson", "esi": 2, "chief_complaint": "Difficulty breathing", "age": 70, "gender": "M"},
    {"name": "Linda Martinez", "esi": 3, "chief_complaint": "Headache", "age": 35, "gender": "F"},
    {"name": "James Anderson", "esi": 5, "chief_complaint": "Minor cut", "age": 22, "gender": "M"},
]

for p in patient_data:
    patient_id = queue.add_patient(
        name=p["name"],
        esi=p["esi"],
        chief_complaint=p["chief_complaint"],
        age=p["age"],
        gender=p["gender"]
    )
    print(f"  Created patient: {p['name']} (ESI {p['esi']}) - ID: {patient_id[:8]}...")

print("\n" + "=" * 50)
print("Sample data added successfully!")
print(f"Total patients: {len(queue._patients)}")
print(f"Total beds: {len(beds.list_beds())}")
print("\nYou can now:")
print("1. Start the backend: python main.py")
print("2. Open frontend/index.html in your browser")
print("3. Test the full workflow!")
