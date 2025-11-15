# add_sample_data.py
"""
Add sample patients and beds to the ER Flow Dashboard for testing
This script manually populates the database with demo data.
For automatic demo data on startup, use DEMO_MODE in main.py
"""
from demo_data import create_demo_data

print("Adding sample data to ER Flow Dashboard...")
print("=" * 50)

# Use shared demo data creation function
create_demo_data()

print("\nYou can now:")
print("1. Start the backend: python main.py")
print("2. Open frontend/index.html in your browser")
print("3. Test the full workflow!")
print("\nNote: If DEMO_MODE is enabled in main.py, data will reset on backend startup.")
