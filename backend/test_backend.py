# test_backend.py
"""
Quick test to verify backend imports work correctly
"""
import sys
from pathlib import Path

# Add shared folder to path
shared_path = Path(__file__).parent.parent / "shared"
sys.path.insert(0, str(shared_path))

print("Testing imports...")

try:
    from smart_queue import SmartQueue
    print("✅ SmartQueue imported")
except Exception as e:
    print(f"❌ SmartQueue import failed: {e}")

try:
    from bed_registery import BedRegistry
    print("✅ BedRegistry imported")
except Exception as e:
    print(f"❌ BedRegistry import failed: {e}")

try:
    from patient import Patient
    print("✅ Patient imported")
except Exception as e:
    print(f"❌ Patient import failed: {e}")

try:
    from bed import Bed
    print("✅ Bed imported")
except Exception as e:
    print(f"❌ Bed import failed: {e}")

print("\nTesting basic functionality...")

try:
    # Create instances
    queue = SmartQueue(department="ED")
    beds = BedRegistry()

    # Add a test patient
    patient_id = queue.add_patient(
        name="Test Patient",
        esi=3,
        chief_complaint="Test",
        age=30,
        gender="M"
    )
    print(f"✅ Created patient: {patient_id}")

    # Add a test bed
    bed_id = beds.add_bed(
        bed_type="ED",
        section="A1",
        features=[]
    )
    print(f"✅ Created bed: {bed_id}")

    # Get all patients
    patients = queue.get_all_active_patients()
    print(f"✅ Retrieved {len(patients)} patient(s)")

    # Get all beds
    all_beds = beds.list_beds()
    print(f"✅ Retrieved {len(all_beds)} bed(s)")

    print("\n✅ All tests passed!")

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
