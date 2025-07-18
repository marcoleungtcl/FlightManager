from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
import sqlite3

from flight_manager.models.pilot import Pilot
from flight_manager.models.airports import Airport


class FlightStatus(Enum):
    PENDING = "pending"
    BOARDING = "boarding"
    DELAYED = "delayed"
    IN_FLIGHT = "in_flight"
    ALIGHT = "alight"
    ARRIVED = "arrived"


@dataclass
class Flight:
    flight_id: int
    flight_number: str
    origin_airport: Airport
    destination_airport: Airport
    scheduled_departure_time: datetime
    estimated_arrival_time: datetime
    departure_time: Optional[datetime]
    arrival_time: Optional[datetime]
    status: FlightStatus
    pilot: Optional[Pilot]
    company: str

    @classmethod
    def create_table(cls, conn: sqlite3.Connection) -> None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS flights (
                flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
                flight_number TEXT NOT NULL,
                origin_airport_code TEXT NOT NULL,
                destination_airport_code TEXT NOT NULL,
                scheduled_departure_time TEXT NOT NULL,
                estimated_arrival_time TEXT NOT NULL,
                departure_time TEXT,
                arrival_time TEXT,
                status TEXT NOT NULL,
                pilot_id TEXT,
                company TEXT NOT NULL,
                FOREIGN KEY(origin_airport_code) REFERENCES airports(code),
                FOREIGN KEY(destination_airport_code) REFERENCES airports(code),
                FOREIGN KEY(pilot_id) REFERENCES pilots(pilot_id)
            )
        """
        )

    @classmethod
    def drop_table(cls, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS flights")

    def save(self, conn: sqlite3.Connection) -> None:
        cursor = conn.cursor()
        if self.flight_id:  
            cursor.execute(
                """
                UPDATE flights SET
                    flight_number = ?,
                    origin_airport_code = ?,
                    destination_airport_code = ?,
                    scheduled_departure_time = ?,
                    estimated_arrival_time = ?,
                    departure_time = ?,
                    arrival_time = ?,
                    status = ?,
                    pilot_id = ?,
                    company = ?
                WHERE flight_id = ?
            """,
                (
                    self.flight_number,
                    self.origin_airport.code,
                    self.destination_airport.code,
                    self.scheduled_departure_time.isoformat(),
                    self.estimated_arrival_time.isoformat(),
                    self.departure_time.isoformat() if self.departure_time else None,
                    self.arrival_time.isoformat() if self.arrival_time else None,
                    self.status.value,
                    self.pilot.pilot_id if self.pilot else None,
                    self.company,
                    self.flight_id,
                ),
            )
        else:  
            cursor.execute(
                """
                INSERT INTO flights (
                    flight_number,
                    origin_airport_code,
                    destination_airport_code,
                    scheduled_departure_time,
                    estimated_arrival_time,
                    departure_time,
                    arrival_time,
                    status,
                    pilot_id,
                    company
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    self.flight_number,
                    self.origin_airport.code,
                    self.destination_airport.code,
                    self.scheduled_departure_time.isoformat(),
                    self.estimated_arrival_time.isoformat(),
                    self.departure_time.isoformat() if self.departure_time else None,
                    self.arrival_time.isoformat() if self.arrival_time else None,
                    self.status.value,
                    self.pilot.pilot_id if self.pilot else None,
                    self.company,
                ),
            )
            self.flight_id = cursor.lastrowid

    @classmethod
    def create(
        cls,
        conn: sqlite3.Connection,
        flight_number: str,
        origin_airport: Airport,
        destination_airport: Airport,
        scheduled_departure_time: datetime,
        estimated_arrival_time: datetime,
        company: str,
        pilot: Optional[Pilot] = None,
        status: FlightStatus = FlightStatus.PENDING,
    ) -> "Flight":
        flight = cls(
            flight_id=None,
            flight_number=flight_number,
            origin_airport=origin_airport,
            destination_airport=destination_airport,
            scheduled_departure_time=scheduled_departure_time,
            estimated_arrival_time=estimated_arrival_time,
            departure_time=None,
            arrival_time=None,
            status=status,
            pilot=pilot,
            company=company,
        )
        flight.save(conn)
        return flight

    @classmethod
    def get_by_id(cls, conn: sqlite3.Connection, flight_id: int) -> Optional["Flight"]:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                f.flight_id,
                f.flight_number,
                f.scheduled_departure_time,
                f.estimated_arrival_time,
                f.departure_time,
                f.arrival_time,
                f.status,
                f.company,
                a1.code, a1.name, a1.address, a1.status,
                a2.code, a2.name, a2.address, a2.status,
                p.pilot_id, p.first_name, p.last_name
            FROM flights f
            JOIN airports a1 ON f.origin_airport_code = a1.code
            JOIN airports a2 ON f.destination_airport_code = a2.code
            LEFT JOIN pilots p ON f.pilot_id = p.pilot_id
            WHERE f.flight_id = ?
        """,
            (flight_id,),
        )

        row = cursor.fetchone()
        if not row:
            return None

        origin = Airport(row[8], row[9], row[10], row[11])
        destination = Airport(row[12], row[13], row[14], row[15])
        pilot = Pilot(row[16], row[17], row[18]) if row[16] else None

        return cls(
            flight_id=row[0],
            flight_number=row[1],
            origin_airport=origin,
            destination_airport=destination,
            scheduled_departure_time=datetime.fromisoformat(row[2]),
            estimated_arrival_time=datetime.fromisoformat(row[3]),
            departure_time=datetime.fromisoformat(row[4]) if row[4] else None,
            arrival_time=datetime.fromisoformat(row[5]) if row[5] else None,
            status=FlightStatus(row[6]),
            pilot=pilot,
            company=row[7],
        )

    @classmethod
    def get_all(
        cls,
        conn: sqlite3.Connection,
        flight_number: Optional[str] = None,
        status: Optional[FlightStatus] = None,
        company: Optional[str] = None,
        pilot: Optional[Pilot] = None,
        origin_airport: Optional[Airport] = None,
        destination_airport: Optional[Airport] = None
    ) -> List["Flight"]:
        cursor = conn.cursor()

        
        query = """
            SELECT 
                f.flight_id,
                f.flight_number,
                f.scheduled_departure_time,
                f.estimated_arrival_time,
                f.departure_time,
                f.arrival_time,
                f.status,
                f.company,
                a1.code, a1.name, a1.address, a1.status,
                a2.code, a2.name, a2.address, a2.status,
                p.pilot_id, p.first_name, p.last_name
            FROM flights f
            JOIN airports a1 ON f.origin_airport_code = a1.code
            JOIN airports a2 ON f.destination_airport_code = a2.code
            LEFT JOIN pilots p ON f.pilot_id = p.pilot_id
        """

        
        conditions = []
        params = []

        if flight_number is not None:
            conditions.append("f.flight_number LIKE ?")
            params.append(f"%{flight_number}%")

        if status is not None:
            conditions.append("f.status = ?")
            params.append(status.value)

        if company is not None:
            conditions.append("f.company LIKE ?")
            params.append(f"%{company}%")

        if pilot is not None:
            conditions.append("f.pilot_id = ?")
            params.append(pilot.pilot_id)

        if origin_airport is not None:
            conditions.append("f.origin_airport_code = ?")
            params.append(origin_airport.code)

        if destination_airport is not None:
            conditions.append("f.destination_airport_code = ?")
            params.append(destination_airport.code)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY f.scheduled_departure_time"

        cursor.execute(query, params)

        flights = []
        for row in cursor.fetchall():
            origin = Airport(row[8], row[9], row[10], row[11])
            destination = Airport(row[12], row[13], row[14], row[15])
            pilot = Pilot(row[16], row[17], row[18]) if row[16] else None

            flights.append(
                cls(
                    flight_id=row[0],
                    flight_number=row[1],
                    origin_airport=origin,
                    destination_airport=destination,
                    scheduled_departure_time=datetime.fromisoformat(row[2]),
                    estimated_arrival_time=datetime.fromisoformat(row[3]),
                    departure_time=datetime.fromisoformat(row[4]) if row[4] else None,
                    arrival_time=datetime.fromisoformat(row[5]) if row[5] else None,
                    status=FlightStatus(row[6]),
                    pilot=pilot,
                    company=row[7],
                )
            )
        return flights

    def delete(self, conn: sqlite3.Connection) -> None:
        if self.flight_id:
            conn.execute("DELETE FROM flights WHERE flight_id = ?", (self.flight_id,))

    @classmethod
    def delete_by_id(cls, conn: sqlite3.Connection, flight_id: int) -> None:
        conn.execute("DELETE FROM flights WHERE flight_id = ?", (flight_id,))

    def update_status(self, conn: sqlite3.Connection, new_status: FlightStatus) -> None:
        self.status = new_status
        self.save(conn)

    def record_departure(
        self, conn: sqlite3.Connection, departure_time: datetime
    ) -> None:
        self.departure_time = departure_time
        self.status = FlightStatus.IN_FLIGHT
        self.save(conn)

    def record_arrival(self, conn: sqlite3.Connection, arrival_time: datetime) -> None:
        self.arrival_time = arrival_time
        self.status = FlightStatus.ARRIVED
        self.save(conn)
