from contextlib import contextmanager
from typing import Iterator
import sqlite3
from datetime import datetime
from models.pilot import Pilot
from models.airports import Airport
from models.flight import Flight, FlightStatus

@contextmanager
def get_connection(db_path: str = 'airline.db') -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_database():
    with get_connection() as conn:
        Airport.create_table(conn)
        Pilot.create_table(conn)
        Flight.create_table(conn)

def add_airport():
    with get_connection() as conn:
        code = input("Airport code (3 letters): ").upper()
        name = input("Airport name: ")
        address = input("Address: ")
        Airport.create(conn, code, name, address)
    print(f"Airport {code} added successfully!")

def add_pilot():
    with get_connection() as conn:
        first_name = input("First name: ")
        last_name = input("Last name: ")
        pilot = Pilot.create(conn, first_name, last_name)
    print(f"Pilot {pilot.pilot_id} created successfully!")

def add_flight():
    with get_connection() as conn:
        # Get required flight information
        flight_number = input("Flight number: ")
        company = input("Airline company: ")
        
        # Select origin airport
        airports = Airport.get_all(conn)
        print("\nAvailable Airports:")
        for i, airport in enumerate(airports, 1):
            print(f"{i}. {airport.code} - {airport.name}")
        origin_idx = int(input("Select origin airport (number): ")) - 1
        
        # Select destination airport
        dest_idx = int(input("Select destination airport (number): ")) - 1
        
        # Get flight times
        departure = input("Scheduled departure (YYYY-MM-DD HH:MM): ")
        arrival = input("Estimated arrival (YYYY-MM-DD HH:MM): ")
        
        flight = Flight.create(
            conn,
            flight_number=flight_number,
            origin_airport=airports[origin_idx],
            destination_airport=airports[dest_idx],
            scheduled_departure_time=datetime.strptime(departure, "%Y-%m-%d %H:%M"),
            estimated_arrival_time=datetime.strptime(arrival, "%Y-%m-%d %H:%M"),
            company=company
        )
    print(f"Flight {flight.flight_number} created with ID {flight.flight_id}")

def assign_pilot():
    with get_connection() as conn:
        # List available flights
        flights = Flight.get_all(conn)
        print("\nAvailable Flights:")
        for i, flight in enumerate(flights, 1):
            print(f"{i}. {flight.flight_number} (ID: {flight.flight_id})")
        flight_idx = int(input("Select flight (number): ")) - 1
        
        # List available pilots
        pilots = Pilot.get_all(conn)
        print("\nAvailable Pilots:")
        for i, pilot in enumerate(pilots, 1):
            print(f"{i}. {pilot.first_name} {pilot.last_name} (ID: {pilot.pilot_id})")
        pilot_idx = int(input("Select pilot (number): ")) - 1
        
        # Assign pilot
        flights[flight_idx].pilot = pilots[pilot_idx]
        flights[flight_idx].save(conn)
    print("Pilot assigned successfully!")

def view_flights():
    with get_connection() as conn:
        flights = Flight.get_all(conn)
        print("\nAll Flights:")
        for flight in flights:
            pilot = f"{flight.pilot.first_name} {flight.pilot.last_name}" if flight.pilot else "Unassigned"
            print(
                f"ID: {flight.flight_id} | {flight.flight_number} | "
                f"{flight.origin_airport.code} → {flight.destination_airport.code} | "
                f"Pilot: {pilot} | Status: {flight.status.value}"
            )

def main():
    initialize_database()
    
    menu_options = {
        '1': ("Add Airport", add_airport),
        '2': ("Add Pilot", add_pilot),
        '3': ("Add Flight", add_flight),
        '4': ("Assign Pilot", assign_pilot),
        '5': ("View Flights", view_flights),
        '6': ("Exit", lambda: None)
    }
    
    while True:
        print("\nAirline Management System")
        for key, (text, _) in menu_options.items():
            print(f"{key}. {text}")
        
        choice = input("\nEnter your choice: ")
        if choice == '6':
            print("Goodbye!")
            break
        
        if choice in menu_options:
            menu_options[choice][1]()
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()