from dataclasses import dataclass
import sqlite3
import random
import string
from typing import List, Optional, Iterator
from contextlib import contextmanager

@dataclass
class Airport:
    code: str
    name: str
    address: str

    @classmethod
    def create_table(cls, conn: sqlite3.Connection) -> None:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS airports (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT NOT NULL
            )
        ''')

    @classmethod
    def drop_table(cls, conn: sqlite3.Connection) -> None:
        conn.execute('DROP TABLE IF EXISTS airports')

    def save(self, conn: sqlite3.Connection) -> None:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE airports 
            SET name = ?, address = ?
            WHERE code = ?
        ''', (self.name, self.address, self.code))
        
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO airports (code, name, address)
                VALUES (?, ?, ?)
            ''', (self.code, self.name, self.address))

    @classmethod
    def create(cls, conn: sqlite3.Connection, code: str, name: str, address: str) -> 'Airport':
        airport = cls(code, name, address)
        airport.save(conn)
        return airport

    @classmethod
    def get_by_code(cls, conn: sqlite3.Connection, code: str) -> Optional['Airport']:
        cursor = conn.cursor()
        cursor.execute('SELECT code, name, address FROM airports WHERE code = ?', (code,))
        row = cursor.fetchone()
        return cls(*row) if row else None

    @classmethod
    def get_all(cls, conn: sqlite3.Connection) -> List['Airport']:
        cursor = conn.cursor()
        cursor.execute('SELECT code, name, address FROM airports')
        return [cls(*row) for row in cursor.fetchall()]

    def delete(self, conn: sqlite3.Connection) -> None:
        conn.execute('DELETE FROM airports WHERE code = ?', (self.code,))

    @classmethod
    def delete_by_code(cls, conn: sqlite3.Connection, code: str) -> None:
        conn.execute('DELETE FROM airports WHERE code = ?', (code,))