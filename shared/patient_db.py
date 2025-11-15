# patient_db.py
"""
Database layer for patients.

This module manages the SQLite database for the 'patients' table.
Works alongside bed_db.py using the same hospital_flow.db database.
"""

import json
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from patient import Patient, PatientStatus

# Use same database as beds
DB_PATH = "hospital_flow.db"
UTC = timezone.utc


class SQLitePatientStore:
    """
    Thin wrapper around a SQLite 'patients' table.

    Provides persistence for Patient objects, similar to SQLiteBedStore for Bed objects.
    """

    def __init__(self, db_path: str = DB_PATH):
        # check_same_thread=False so multiple FastAPI threads can share this connection
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    # ------------- schema -------------

    def _init_schema(self) -> None:
        """
        Create the 'patients' table if it does not exist.
        """
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                esi INTEGER NOT NULL CHECK(esi BETWEEN 1 AND 5),
                chief_complaint TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                department TEXT NOT NULL,
                status TEXT NOT NULL,
                bed_id TEXT,
                assigned_nurse_id TEXT,
                assigned_physician_id TEXT,
                notes TEXT,
                triage_notes TEXT,
                arrival_ts TEXT NOT NULL,
                timestamps TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    # ------------- helpers -------------

    @staticmethod
    def _row_to_patient(row: sqlite3.Row) -> Patient:
        """
        Convert a DB row into a Patient dataclass.
        """
        # Parse timestamps dict from JSON
        timestamps_dict = {}
        raw_timestamps = row["timestamps"]
        if raw_timestamps:
            try:
                timestamps_json = json.loads(raw_timestamps)
                timestamps_dict = {
                    status: datetime.fromisoformat(ts)
                    for status, ts in timestamps_json.items()
                }
            except (json.JSONDecodeError, ValueError):
                timestamps_dict = {}

        # Parse arrival timestamp
        arrival_ts = datetime.fromisoformat(row["arrival_ts"])

        return Patient(
            id=row["id"],
            name=row["name"],
            esi=row["esi"],
            chief_complaint=row["chief_complaint"],
            age=row["age"],
            gender=row["gender"],
            department=row["department"],
            status=row["status"],
            bed_id=row["bed_id"],
            assigned_nurse_id=row["assigned_nurse_id"],
            assigned_physician_id=row["assigned_physician_id"],
            notes=row["notes"] or "",
            triage_notes=row["triage_notes"] or "",
            arrival_ts=arrival_ts,
            timestamps=timestamps_dict,
        )

    @staticmethod
    def _patient_to_values(patient: Patient) -> tuple:
        """
        Convert Patient dataclass to tuple for DB insertion/update.
        """
        # Serialize timestamps dict to JSON
        timestamps_json = json.dumps({
            status: ts.isoformat()
            for status, ts in patient.timestamps.items()
        })

        return (
            patient.id,
            patient.name,
            patient.esi,
            patient.chief_complaint,
            patient.age,
            patient.gender,
            patient.department,
            patient.status,
            patient.bed_id,
            patient.assigned_nurse_id,
            patient.assigned_physician_id,
            patient.notes,
            patient.triage_notes,
            patient.arrival_ts.isoformat(),
            timestamps_json,
        )

    # ------------- CRUD operations -------------

    def insert_patient(self, patient: Patient) -> None:
        """
        Insert a new patient row into the DB.
        """
        values = self._patient_to_values(patient)
        self.conn.execute(
            """
            INSERT INTO patients (
                id, name, esi, chief_complaint, age, gender, department, status,
                bed_id, assigned_nurse_id, assigned_physician_id, notes, triage_notes,
                arrival_ts, timestamps
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            values,
        )
        self.conn.commit()

    def update_patient(self, patient: Patient) -> None:
        """
        Update an existing patient row.
        """
        values = self._patient_to_values(patient)
        self.conn.execute(
            """
            UPDATE patients
            SET name = ?, esi = ?, chief_complaint = ?, age = ?, gender = ?,
                department = ?, status = ?, bed_id = ?, assigned_nurse_id = ?,
                assigned_physician_id = ?, notes = ?, triage_notes = ?,
                arrival_ts = ?, timestamps = ?
            WHERE id = ?
            """,
            values[1:] + (values[0],),  # All fields except id, then id at the end
        )
        self.conn.commit()

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """
        Get a single patient by ID.
        """
        cur = self.conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_patient(row)

    def list_patients(
        self,
        department: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Patient]:
        """
        Get a list of patients filtered by optional fields.
        """
        query = "SELECT * FROM patients WHERE 1=1"
        params: List[str] = []

        if department:
            query += " AND department = ?"
            params.append(department)
        if status:
            query += " AND status = ?"
            params.append(status)

        cur = self.conn.execute(query, params)
        rows = cur.fetchall()
        return [self._row_to_patient(r) for r in rows]

    def list_active_patients(self, department: Optional[str] = None) -> List[Patient]:
        """
        Get all active patients (not DISCHARGED, ADMITTED, or LWBS).
        """
        inactive_statuses = (
            PatientStatus.DISCHARGED.value,
            PatientStatus.ADMITTED.value,
            PatientStatus.LEFT_WITHOUT_BEING_SEEN.value,
        )

        query = "SELECT * FROM patients WHERE status NOT IN (?, ?, ?)"
        params = list(inactive_statuses)

        if department:
            query += " AND department = ?"
            params.append(department)

        cur = self.conn.execute(query, params)
        rows = cur.fetchall()
        return [self._row_to_patient(r) for r in rows]

    def delete_patient(self, patient_id: str) -> None:
        """
        Delete a patient from the database (use sparingly - prefer status updates).
        """
        self.conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        self.conn.commit()
