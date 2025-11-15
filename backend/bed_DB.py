# beds_db.py
"""
Database layer for hospital beds.

This module owns the SQLite database and the 'beds' table.
The actual .db file will be created automatically the first time
you import and use SQLiteBedStore.
"""

import json
import sqlite3
from typing import Iterable, List, Optional, Set

from bed import Bed  # assumes bed.py is in the same folder

# Change this to ":memory:" if you truly want it in-memory only
DB_PATH = "hospital_beds.db"


class SQLiteBedStore:
    """
    Thin wrapper around a SQLite 'beds' table.

    You DON'T use this directly in the frontend.
    BedRegistry will use this class to read/write beds, and
    FastAPI endpoints will call BedRegistry.
    """

    def __init__(self, db_path: str = DB_PATH):
        # check_same_thread=False so multiple FastAPI threads can share this connection
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    # ------------- schema -------------

    def _init_schema(self) -> None:
        """
        Create the 'beds' table if it does not exist.
        """
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS beds (
                id TEXT PRIMARY KEY,
                bed_type TEXT NOT NULL,
                section TEXT NOT NULL,
                features TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('OPEN','HELD','OCCUPIED')),
                patient_id TEXT
            )
            """
        )
        self.conn.commit()

    # ------------- helpers -------------

    @staticmethod
    def _row_to_bed(row: sqlite3.Row) -> Bed:
        """
        Convert a DB row into a Bed dataclass.
        """
        features: Set[str] = set()
        raw = row["features"]
        if raw:
            try:
                features = set(json.loads(raw))
            except json.JSONDecodeError:
                features = set()

        return Bed(
            id=row["id"],
            bed_type=row["bed_type"],
            section=row["section"],
            features=features,
            status=row["status"],
            patient_id=row["patient_id"],
        )

    # ------------- CRUD operations -------------

    def insert_bed(self, bed: Bed) -> None:
        """
        Insert a new bed row into the DB.
        """
        self.conn.execute(
            """
            INSERT INTO beds (id, bed_type, section, features, status, patient_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                bed.id,
                bed.bed_type,
                bed.section,
                json.dumps(sorted(list(bed.features))),
                bed.status,
                bed.patient_id,
            ),
        )
        self.conn.commit()

    def update_bed(self, bed: Bed) -> None:
        """
        Update an existing bed row.
        """
        self.conn.execute(
            """
            UPDATE beds
            SET bed_type = ?, section = ?, features = ?, status = ?, patient_id = ?
            WHERE id = ?
            """,
            (
                bed.bed_type,
                bed.section,
                json.dumps(sorted(list(bed.features))),
                bed.status,
                bed.patient_id,
                bed.id,
            ),
        )
        self.conn.commit()

    def get_bed(self, bed_id: str) -> Optional[Bed]:
        cur = self.conn.execute("SELECT * FROM beds WHERE id = ?", (bed_id,))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_bed(row)

    def get_bed_by_patient(self, patient_id: str) -> Optional[Bed]:
        cur = self.conn.execute("SELECT * FROM beds WHERE patient_id = ?", (patient_id,))
        row = cur.fetchone()
        if not row:
            return None
        return self._row_to_bed(row)

    def list_beds(
        self,
        status: Optional[str] = None,
        bed_type: Optional[str] = None,
        section: Optional[str] = None,
    ) -> List[Bed]:
        """
        Get a list of beds filtered by optional fields.
        """
        query = "SELECT * FROM beds WHERE 1=1"
        params: List[str] = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if bed_type:
            query += " AND bed_type = ?"
            params.append(bed_type)
        if section:
            query += " AND section = ?"
            params.append(section)

        cur = self.conn.execute(query, params)
        rows = cur.fetchall()
        return [self._row_to_bed(r) for r in rows]

    def find_open_bed(
        self,
        needed_bed_type: Optional[str],
        needed_section: Optional[str],
        required_features: Optional[Iterable[str]],
    ) -> Optional[Bed]:
        """
        Find an OPEN bed that matches bed_type, section, and required features.
        Very simple "best match" for hackathon purposes: returns the first match.
        """
        required_features = set(required_features or [])

        query = "SELECT * FROM beds WHERE status = 'OPEN'"
        params: List[str] = []

        if needed_bed_type:
            query += " AND bed_type = ?"
            params.append(needed_bed_type)

        if needed_section:
            query += " AND section = ?"
            params.append(needed_section)

        cur = self.conn.execute(query, params)
        candidates = [self._row_to_bed(r) for r in cur.fetchall()]

        def matches_features(b: Bed) -> bool:
            return required_features.issubset(b.features)

        candidates = [b for b in candidates if matches_features(b)]

        if not candidates:
            return None

        # You could sort by section or some scoring rule here.
        return candidates[0]
