from dataclasses import dataclass
import sqlite3
from typing import List, Optional
from enum import Enum


class AirportStatus(Enum):
    ALL_CLEAR = "all_clear"
    WARNING = "warning"
    CLOSED = "closed"


@dataclass
class Airport:
    code: str
    name: str
    address: str
    status: AirportStatus

    @classmethod
    def create_table(cls, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS airports (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                status TEXT NOT NULL
            )
        """
        )

    @classmethod
    def drop_table(cls, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS airports")

    def update(self, conn: sqlite3.Connection) -> None:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE airports 
            SET name = ?, address = ?, status = ?
            WHERE code = ?
        """,
            (self.name, self.address, self.status.value, self.code),
        )

        if cursor.rowcount == 0:
            raise KeyError(f"Airport with code {self.code} not found")

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        code: str,
        name: str,
        address: str,
        status: AirportStatus,
    ) -> "Airport":
        airport = cls(code, name, address, status)
        cursor = conn.cursor()
        if Airport.get_by_code(conn, code) is not None:
            raise ValueError("Airport with the same code already created")

        cursor.execute(
            """
            INSERT INTO airports (code, name, address, status)
            VALUES (?, ?, ?, ?)
        """,
            (code, name, address, status.value),
        )
        return airport

    @classmethod
    def get_by_code(cls, conn: sqlite3.Connection, code: str) -> Optional["Airport"]:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT code, name, address, status FROM airports WHERE code = ?", (code,)
        )
        row = cursor.fetchone()
        if row:
            return cls(
                code=row[0], name=row[1], address=row[2], status=AirportStatus(row[3])
            )
        return None

    @classmethod
    def get_all(cls, conn: sqlite3.Connection) -> List["Airport"]:
        cursor = conn.cursor()
        cursor.execute("SELECT code, name, address, status FROM airports")
        return [
            cls(code=row[0], name=row[1], address=row[2], status=AirportStatus(row[3]))
            for row in cursor.fetchall()
        ]

    def delete(self, conn: sqlite3.Connection) -> None:
        conn.execute("DELETE FROM airports WHERE code = ?", (self.code,))

    @classmethod
    def delete_by_code(cls, conn: sqlite3.Connection, code: str) -> None:
        conn.execute("DELETE FROM airports WHERE code = ?", (code,))
