from dataclasses import dataclass
import sqlite3
import random
import string
from typing import List, Optional


@dataclass
class Pilot:
    pilot_id: str
    first_name: str
    last_name: str

    @classmethod
    def generate_pilot_id(cls, length: int = 6) -> str:
        """Generate a random pilot ID with letters and digits"""
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choice(chars) for _ in range(length - 1))

    @classmethod
    def create_table(cls, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pilots (
                pilot_id TEXT PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL
            )
        """
        )

    @classmethod
    def drop_table(cls, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS pilots")

    def save(self, conn: sqlite3.Connection) -> None:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE pilots 
            SET first_name = ?, last_name = ?
            WHERE pilot_id = ?
        """,
            (self.first_name, self.last_name, self.pilot_id),
        )

        if cursor.rowcount == 0:
            cursor.execute(
                """
                INSERT INTO pilots (pilot_id, first_name, last_name)
                VALUES (?, ?, ?)
            """,
                (self.pilot_id, self.first_name, self.last_name),
            )

    @classmethod
    def create(
        cls, conn: sqlite3.Connection, first_name: str, last_name: str
    ) -> "Pilot":
        pilot_id = cls.generate_pilot_id()
        pilot = cls(pilot_id, first_name, last_name)
        pilot.save(conn)
        return pilot

    @classmethod
    def get_by_id(cls, conn: sqlite3.Connection, pilot_id: str) -> Optional["Pilot"]:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pilot_id, first_name, last_name FROM pilots WHERE pilot_id = ?",
            (pilot_id,),
        )
        row = cursor.fetchone()
        return cls(*row) if row else None

    @classmethod
    def get_all(cls, conn: sqlite3.Connection) -> List["Pilot"]:
        cursor = conn.cursor()
        cursor.execute("SELECT pilot_id, first_name, last_name FROM pilots")
        return [cls(*row) for row in cursor.fetchall()]

    def delete(self, conn: sqlite3.Connection) -> None:
        conn.execute("DELETE FROM pilots WHERE pilot_id = ?", (self.pilot_id,))

    @classmethod
    def delete_by_id(cls, conn: sqlite3.Connection, pilot_id: str) -> None:
        conn.execute("DELETE FROM pilots WHERE pilot_id = ?", (pilot_id,))
