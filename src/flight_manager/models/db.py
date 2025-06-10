import sqlite3
from typing import Iterator
from contextlib import contextmanager

@contextmanager
def get_connection(db_path: str = "airline.db") -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except (ValueError, KeyError) as e:
        conn.rollback()
        print(f"\n{e}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
