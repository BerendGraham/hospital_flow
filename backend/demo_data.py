# demo_data.py
"""
Demo data creation for ER Flow Dashboard
Provides sample patients and beds across multiple departments
LARGE DATASET for impressive hackathon demo
"""
import sys
from pathlib import Path

# Add shared folder to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

from smart_queue import SmartQueue
from bed_registery import BedRegistry


def create_demo_data():
    """Create demo beds and patients for hackathon demo"""

    print("Creating LARGE demo dataset...")
    print("=" * 60)

    # Create instances
    queue = SmartQueue(department="ED")
    beds = BedRegistry()

    # ============================================================================
    # Add sample beds across departments (EXPANDED)
    # ============================================================================
    print("\nAdding beds...")
    bed_data = [
        # Emergency Department (15 beds)
        {"bed_type": "ED", "section": "ED-A1", "features": ["cardiac_monitor"]},
        {"bed_type": "ED", "section": "ED-A2", "features": []},
        {"bed_type": "ED", "section": "ED-A3", "features": ["isolation"]},
        {"bed_type": "ED", "section": "ED-A4", "features": ["cardiac_monitor"]},
        {"bed_type": "ED", "section": "ED-B1", "features": ["cardiac_monitor"]},
        {"bed_type": "ED", "section": "ED-B2", "features": []},
        {"bed_type": "ED", "section": "ED-B3", "features": []},
        {"bed_type": "ED", "section": "ED-B4", "features": ["isolation"]},
        {"bed_type": "ED", "section": "ED-C1", "features": ["trauma_bay"]},
        {"bed_type": "ED", "section": "ED-C2", "features": ["trauma_bay"]},
        {"bed_type": "ED", "section": "ED-D1", "features": []},
        {"bed_type": "ED", "section": "ED-D2", "features": ["cardiac_monitor"]},
        {"bed_type": "ED", "section": "ED-D3", "features": []},
        {"bed_type": "ED", "section": "ED-D4", "features": []},
        {"bed_type": "ED", "section": "ED-E1", "features": ["pediatric"]},

        # ICU (8 beds)
        {"bed_type": "ICU", "section": "ICU-1", "features": ["ventilator", "cardiac_monitor"]},
        {"bed_type": "ICU", "section": "ICU-2", "features": ["ventilator", "cardiac_monitor"]},
        {"bed_type": "ICU", "section": "ICU-3", "features": ["ventilator"]},
        {"bed_type": "ICU", "section": "ICU-4", "features": ["ventilator", "cardiac_monitor"]},
        {"bed_type": "ICU", "section": "ICU-5", "features": ["ventilator"]},
        {"bed_type": "ICU", "section": "ICU-6", "features": ["ventilator", "cardiac_monitor"]},
        {"bed_type": "ICU", "section": "ICU-7", "features": ["ventilator"]},
        {"bed_type": "ICU", "section": "ICU-8", "features": ["ventilator", "cardiac_monitor"]},

        # Med-Surg (12 beds)
        {"bed_type": "MED_SURG", "section": "MS-201", "features": []},
        {"bed_type": "MED_SURG", "section": "MS-202", "features": []},
        {"bed_type": "MED_SURG", "section": "MS-203", "features": ["telemetry"]},
        {"bed_type": "MED_SURG", "section": "MS-204", "features": []},
        {"bed_type": "MED_SURG", "section": "MS-205", "features": ["telemetry"]},
        {"bed_type": "MED_SURG", "section": "MS-206", "features": []},
        {"bed_type": "MED_SURG", "section": "MS-301", "features": []},
        {"bed_type": "MED_SURG", "section": "MS-302", "features": ["telemetry"]},
        {"bed_type": "MED_SURG", "section": "MS-303", "features": []},
        {"bed_type": "MED_SURG", "section": "MS-304", "features": []},
        {"bed_type": "MED_SURG", "section": "MS-305", "features": ["telemetry"]},
        {"bed_type": "MED_SURG", "section": "MS-306", "features": []},

        # Step-Down (6 beds)
        {"bed_type": "STEP_DOWN", "section": "SD-101", "features": ["telemetry", "cardiac_monitor"]},
        {"bed_type": "STEP_DOWN", "section": "SD-102", "features": ["telemetry"]},
        {"bed_type": "STEP_DOWN", "section": "SD-103", "features": ["telemetry", "cardiac_monitor"]},
        {"bed_type": "STEP_DOWN", "section": "SD-104", "features": ["telemetry"]},
        {"bed_type": "STEP_DOWN", "section": "SD-105", "features": ["telemetry", "cardiac_monitor"]},
        {"bed_type": "STEP_DOWN", "section": "SD-106", "features": ["telemetry"]},

        # Pediatrics (6 beds)
        {"bed_type": "PEDS", "section": "PEDS-1", "features": ["pediatric"]},
        {"bed_type": "PEDS", "section": "PEDS-2", "features": ["pediatric"]},
        {"bed_type": "PEDS", "section": "PEDS-3", "features": ["pediatric", "isolation"]},
        {"bed_type": "PEDS", "section": "PEDS-4", "features": ["pediatric"]},
        {"bed_type": "PEDS", "section": "PEDS-5", "features": ["pediatric"]},
        {"bed_type": "PEDS", "section": "PEDS-6", "features": ["pediatric", "cardiac_monitor"]},

        # Labor & Delivery (4 beds)
        {"bed_type": "LD", "section": "LD-1", "features": ["fetal_monitor"]},
        {"bed_type": "LD", "section": "LD-2", "features": ["fetal_monitor"]},
        {"bed_type": "LD", "section": "LD-3", "features": ["fetal_monitor"]},
        {"bed_type": "LD", "section": "LD-4", "features": ["fetal_monitor"]},

        # Psych (4 beds)
        {"bed_type": "PSYCH", "section": "PSYCH-A", "features": ["secure"]},
        {"bed_type": "PSYCH", "section": "PSYCH-B", "features": ["secure"]},
        {"bed_type": "PSYCH", "section": "PSYCH-C", "features": ["secure"]},
        {"bed_type": "PSYCH", "section": "PSYCH-D", "features": ["secure"]},

        # Operating Room (4 beds)
        {"bed_type": "OR", "section": "OR-1", "features": ["surgical"]},
        {"bed_type": "OR", "section": "OR-2", "features": ["surgical"]},
        {"bed_type": "OR", "section": "OR-3", "features": ["surgical"]},
        {"bed_type": "OR", "section": "OR-4", "features": ["surgical"]},

        # PACU (6 beds)
        {"bed_type": "PACU", "section": "PACU-1", "features": ["post_op"]},
        {"bed_type": "PACU", "section": "PACU-2", "features": ["post_op"]},
        {"bed_type": "PACU", "section": "PACU-3", "features": ["post_op"]},
        {"bed_type": "PACU", "section": "PACU-4", "features": ["post_op"]},
        {"bed_type": "PACU", "section": "PACU-5", "features": ["post_op"]},
        {"bed_type": "PACU", "section": "PACU-6", "features": ["post_op"]},

        # Observation (4 beds)
        {"bed_type": "OBS", "section": "OBS-1", "features": []},
        {"bed_type": "OBS", "section": "OBS-2", "features": []},
        {"bed_type": "OBS", "section": "OBS-3", "features": []},
        {"bed_type": "OBS", "section": "OBS-4", "features": []},
    ]

    for b in bed_data:
        bed_id = beds.add_bed(
            bed_type=b["bed_type"],
            section=b["section"],
            features=b["features"]
        )
        print(f"  Created bed: {b['section']:10s} ({b['bed_type']:10s}) - ID: {bed_id[:8]}...")

    # ============================================================================
    # Add sample patients across departments (EXPANDED - 30+ patients)
    # ============================================================================
    print(f"\nAdding {30}+ patients...")
    patient_data = [
        # ED patients (15 patients - mix of severities)
        {"name": "John Smith", "esi": 2, "chief_complaint": "Chest pain", "age": 65, "gender": "M", "department": "ED"},
        {"name": "Mary Johnson", "esi": 1, "chief_complaint": "Severe trauma from MVA", "age": 42, "gender": "F", "department": "ED"},
        {"name": "Robert Brown", "esi": 3, "chief_complaint": "Abdominal pain", "age": 55, "gender": "M", "department": "ED"},
        {"name": "Patricia Davis", "esi": 4, "chief_complaint": "Ankle sprain", "age": 28, "gender": "F", "department": "ED"},
        {"name": "Michael Wilson", "esi": 2, "chief_complaint": "Difficulty breathing", "age": 70, "gender": "M", "department": "ED"},
        {"name": "Jennifer Garcia", "esi": 3, "chief_complaint": "Severe headache", "age": 38, "gender": "F", "department": "ED"},
        {"name": "David Lee", "esi": 2, "chief_complaint": "Stroke symptoms", "age": 68, "gender": "M", "department": "ED"},
        {"name": "Lisa Rodriguez", "esi": 4, "chief_complaint": "Nausea and vomiting", "age": 45, "gender": "F", "department": "ED"},
        {"name": "James Taylor", "esi": 5, "chief_complaint": "Minor laceration", "age": 22, "gender": "M", "department": "ED"},
        {"name": "Barbara Moore", "esi": 3, "chief_complaint": "Back pain", "age": 52, "gender": "F", "department": "ED"},
        {"name": "William Jackson", "esi": 1, "chief_complaint": "Cardiac arrest", "age": 75, "gender": "M", "department": "ED"},
        {"name": "Susan White", "esi": 4, "chief_complaint": "UTI symptoms", "age": 63, "gender": "F", "department": "ED"},
        {"name": "Christopher Harris", "esi": 3, "chief_complaint": "Pneumonia", "age": 58, "gender": "M", "department": "ED"},
        {"name": "Nancy Martin", "esi": 5, "chief_complaint": "Cold symptoms", "age": 35, "gender": "F", "department": "ED"},
        {"name": "Daniel Thompson", "esi": 2, "chief_complaint": "Severe allergic reaction", "age": 41, "gender": "M", "department": "ED"},

        # ICU patients (4 patients - critical)
        {"name": "Linda Martinez", "esi": 1, "chief_complaint": "Septic shock", "age": 58, "gender": "F", "department": "ICU"},
        {"name": "Richard Anderson", "esi": 1, "chief_complaint": "Respiratory failure", "age": 72, "gender": "M", "department": "ICU"},
        {"name": "Karen Thomas", "esi": 1, "chief_complaint": "Multi-organ failure", "age": 64, "gender": "F", "department": "ICU"},
        {"name": "Mark Davis", "esi": 1, "chief_complaint": "Post-surgical complications", "age": 56, "gender": "M", "department": "ICU"},

        # Pediatric patients (5 patients)
        {"name": "Emily Chen", "esi": 3, "chief_complaint": "High fever", "age": 7, "gender": "F", "department": "PEDS"},
        {"name": "Noah Williams", "esi": 4, "chief_complaint": "Ear infection", "age": 5, "gender": "M", "department": "PEDS"},
        {"name": "Sophia Martinez", "esi": 2, "chief_complaint": "Asthma attack", "age": 9, "gender": "F", "department": "PEDS"},
        {"name": "Liam Johnson", "esi": 4, "chief_complaint": "Stomach flu", "age": 6, "gender": "M", "department": "PEDS"},
        {"name": "Olivia Brown", "esi": 3, "chief_complaint": "Dehydration", "age": 3, "gender": "F", "department": "PEDS"},

        # Med-Surg patients (4 patients)
        {"name": "James Anderson", "esi": 5, "chief_complaint": "Post-op recovery", "age": 45, "gender": "M", "department": "MED_SURG"},
        {"name": "Dorothy Wilson", "esi": 4, "chief_complaint": "Diabetes management", "age": 67, "gender": "F", "department": "MED_SURG"},
        {"name": "George Clark", "esi": 3, "chief_complaint": "Cellulitis", "age": 54, "gender": "M", "department": "MED_SURG"},
        {"name": "Ruth Lewis", "esi": 4, "chief_complaint": "Hypertension", "age": 71, "gender": "F", "department": "MED_SURG"},

        # L&D patients (3 patients)
        {"name": "Sarah Thompson", "esi": 2, "chief_complaint": "Active labor", "age": 32, "gender": "F", "department": "LD"},
        {"name": "Jessica Walker", "esi": 3, "chief_complaint": "Preeclampsia monitoring", "age": 28, "gender": "F", "department": "LD"},
        {"name": "Amanda Hall", "esi": 2, "chief_complaint": "Premature labor", "age": 25, "gender": "F", "department": "LD"},

        # PSYCH patients (2 patients)
        {"name": "Timothy Allen", "esi": 3, "chief_complaint": "Suicidal ideation", "age": 34, "gender": "M", "department": "PSYCH"},
        {"name": "Michelle Young", "esi": 3, "chief_complaint": "Psychotic episode", "age": 29, "gender": "F", "department": "PSYCH"},

        # Step-Down patients (2 patients)
        {"name": "Paul King", "esi": 3, "chief_complaint": "Post-MI monitoring", "age": 61, "gender": "M", "department": "STEP_DOWN"},
        {"name": "Betty Wright", "esi": 3, "chief_complaint": "CHF exacerbation", "age": 78, "gender": "F", "department": "STEP_DOWN"},
    ]

    for p in patient_data:
        # Create patient in appropriate queue
        dept_queue = SmartQueue(department=p.get("department", "ED"))
        patient_id = dept_queue.add_patient(
            name=p["name"],
            esi=p["esi"],
            chief_complaint=p["chief_complaint"],
            age=p["age"],
            gender=p["gender"]
        )
        print(f"  Created: {p['name']:20s} (ESI {p['esi']}, {p.get('department', 'ED'):10s}) - ID: {patient_id[:8]}...")

    print("\n" + "=" * 60)
    print("LARGE DEMO DATASET CREATED!")
    print(f"Total beds: {len(beds.list_beds())} across all departments")
    print(f"Total patients: {len(patient_data)} across all departments")
    print("=" * 60)

    return queue, beds


if __name__ == "__main__":
    create_demo_data()
    print("\nDemo data ready!")
