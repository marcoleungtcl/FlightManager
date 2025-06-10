from datetime import datetime
from models.db import get_connection
from models.flight import FlightStatus, Flight
from models.pilot import Pilot
from models.airports import Airport
from views.airport_menus import view_airports

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
            company=company,
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
    """View flights with optional filtering using key=value pairs"""
    print("Enter filter criteria as key=value pairs (comma separated)")
    print("Available filters: flight_number, status, company, pilot_id")
    print("Example: status=boarding,company=Delta")
    print("Leave empty to show all flights")

    filter_input = input("Enter filters: ").strip()

    filters = {}
    if filter_input:
        for pair in filter_input.split(","):
            pair = pair.strip()
            if "=" in pair:
                key, value = pair.split("=", 1)
                key = key.strip().lower()
                value = value.strip()
                filters[key] = value

    with get_connection() as conn:
        # Convert filters to appropriate types
        flight_number = filters.get("flight_number")
        status = FlightStatus(filters["status"]) if "status" in filters else None
        company = filters.get("company")
        pilot_id = filters.get("pilot_id")

        # Get pilot instance if pilot_id was provided
        pilot = None
        if pilot_id:
            pilot = Pilot.get_by_id(conn, pilot_id)
            if not pilot:
                print(f"\nError: No pilot found with ID {pilot_id}")
                return

        # Get filtered flights
        flights = Flight.get_all(
            conn,
            flight_number=flight_number,
            status=status,
            company=company,
            pilot=pilot,
        )

        # Display results
        print(f"\nFlights ({'all' if not filters else 'filtered'}):")
        if not flights:
            print("No flights found matching the criteria")
            return

        for flight in flights:
            pilot_name = (
                f"{flight.pilot.first_name} {flight.pilot.last_name}"
                if flight.pilot
                else "Unassigned"
            )
            print(
                f"ID: {flight.flight_id} | {flight.flight_number} | "
                f"{flight.origin_airport.code} → {flight.destination_airport.code} | "
                f"Depart: {flight.scheduled_departure_time.strftime('%Y-%m-%d %H:%M')} | "
                f"Pilot: {pilot_name} | Status: {flight.status.value} | "
                f"Company: {flight.company}"
            )


def update_flight():
    """Update flight details through an interactive menu"""

    # First show all flights so user can choose which to update
    view_flights()

    # Get flight ID to update
    flight_id = input("\nEnter ID of flight to update (or 'cancel' to abort): ").strip()
    if flight_id.lower() == "cancel":
        return
    if not flight_id.isdigit():
        print("Invalid flight ID")
        return

    with get_connection() as conn:
        flight = Flight.get_by_id(conn, int(flight_id))
        if not flight:
            print(f"No flight found with ID {flight_id}")
            return

        while True:
            print("\nCurrent flight details:")
            print(f"1. Flight Number: {flight.flight_number}")
            print(
                f"2. Origin Airport: {flight.origin_airport.code} ({flight.origin_airport.name})"
            )
            print(
                f"3. Destination Airport: {flight.destination_airport.code} ({flight.destination_airport.name})"
            )
            print(f"4. Scheduled Departure: {flight.scheduled_departure_time}")
            print(f"5. Estimated Arrival: {flight.estimated_arrival_time}")
            print(f"6. Status: {flight.status.value}")
            print(f"7. Company: {flight.company}")
            print(
                f"8. Pilot: {f'{flight.pilot.pilot_id} - {flight.pilot.first_name} {flight.pilot.last_name}' if flight.pilot else 'None'}"
            )
            print(
                f"9. Departure Time (actual): {flight.departure_time or 'Not departed'}"
            )
            print(f"10. Arrival Time (actual): {flight.arrival_time or 'Not arrived'}")

            print("\nSelect field to update:")
            print("1-10: Update corresponding field")
            print("s: Save changes")
            print("c: Cancel without saving")

            choice = input("\nEnter your choice: ").strip().lower()

            if choice == "s":
                try:
                    flight.save(conn)
                    print("\nFlight updated successfully!")
                    print(f"Updated flight ID {flight.flight_id}")
                    break
                except Exception as e:
                    print(f"\nError saving flight: {str(e)}")
            elif choice == "c":
                print("\nUpdate cancelled. No changes were made.")
                break
            elif choice == "1":
                new_value = input(
                    f"Enter new flight number (current: {flight.flight_number}): "
                ).strip()
                if new_value:
                    flight.flight_number = new_value
            elif choice == "2":
                view_airports()
                new_code = (
                    input(
                        f"Enter new origin airport code (current: {flight.origin_airport.code}): "
                    )
                    .strip()
                    .upper()
                )
                if new_code:
                    airport = Airport.get_by_code(conn, new_code)
                    if airport:
                        flight.origin_airport = airport
                    else:
                        print(f"Airport '{new_code}' not found")
            elif choice == "3":
                view_airports()
                new_code = (
                    input(
                        f"Enter new destination airport code (current: {flight.destination_airport.code}): "
                    )
                    .strip()
                    .upper()
                )
                if new_code:
                    airport = Airport.get_by_code(conn, new_code)
                    if airport:
                        flight.destination_airport = airport
                    else:
                        print(f"Airport '{new_code}' not found")
            elif choice == "4":
                new_time = input(
                    f"Enter new scheduled departure (YYYY-MM-DD HH:MM) (current: {flight.scheduled_departure_time}): "
                ).strip()
                if new_time:
                    try:
                        flight.scheduled_departure_time = datetime.strptime(
                            new_time, "%Y-%m-%d %H:%M"
                        )
                    except ValueError:
                        print("Invalid datetime format. Please use YYYY-MM-DD HH:MM")
            elif choice == "5":
                new_time = input(
                    f"Enter new estimated arrival (YYYY-MM-DD HH:MM) (current: {flight.estimated_arrival_time}): "
                ).strip()
                if new_time:
                    try:
                        flight.estimated_arrival_time = datetime.strptime(
                            new_time, "%Y-%m-%d %H:%M"
                        )
                    except ValueError:
                        print("Invalid datetime format. Please use YYYY-MM-DD HH:MM")
            elif choice == "6":
                print("\nAvailable statuses:")
                for i, status in enumerate(FlightStatus, 1):
                    print(f"{i}. {status.value}")
                status_choice = input(
                    f"\nSelect new status (current: {flight.status.value}): "
                ).strip()
                if status_choice.isdigit() and 1 <= int(status_choice) <= len(
                    FlightStatus
                ):
                    flight.status = list(FlightStatus)[int(status_choice) - 1]
                else:
                    print("Invalid status selection")
            elif choice == "7":
                new_company = input(
                    f"Enter new company (current: {flight.company}): "
                ).strip()
                if new_company:
                    flight.company = new_company
            elif choice == "8":
                new_pilot = (
                    input(
                        f"Enter new pilot ID (current: {flight.pilot.pilot_id if flight.pilot else 'None'}) or 'none': "
                    )
                    .strip()
                    .upper()
                )
                if new_pilot:
                    if new_pilot == "none":
                        flight.pilot = None
                    else:
                        pilot = Pilot.get_by_id(conn, new_pilot)
                        if pilot:
                            flight.pilot = pilot
                        else:
                            print(f"Pilot ID '{new_pilot}' not found")
            elif choice == "9":
                new_time = (
                    input(
                        f"Enter actual departure time (YYYY-MM-DD HH:MM or 'none') (current: {flight.departure_time}): "
                    )
                    .strip()
                    .lower()
                )
                if new_time:
                    if new_time == "none":
                        flight.departure_time = None
                    else:
                        try:
                            flight.departure_time = datetime.strptime(
                                new_time, "%Y-%m-%d %H:%M"
                            )
                        except ValueError:
                            print(
                                "Invalid datetime format. Please use YYYY-MM-DD HH:MM"
                            )
            elif choice == "10":
                new_time = (
                    input(
                        f"Enter actual arrival time (YYYY-MM-DD HH:MM or 'none') (current: {flight.arrival_time}): "
                    )
                    .strip()
                    .lower()
                )
                if new_time:
                    if new_time == "none":
                        flight.arrival_time = None
                    else:
                        try:
                            flight.arrival_time = datetime.strptime(
                                new_time, "%Y-%m-%d %H:%M"
                            )
                        except ValueError:
                            print(
                                "Invalid datetime format. Please use YYYY-MM-DD HH:MM"
                            )
            else:
                print("Invalid choice. Please try again.")

menu_options = [
    ("Add Flight", add_flight),
    ("Assign Pilot", assign_pilot),
    ("View Flights", view_flights),
    ("Edit Flights", update_flight),
    ("Exit", lambda: None),
]