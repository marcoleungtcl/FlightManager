from datetime import datetime
from flight_manager.models.db import get_connection
from flight_manager.models.flight import FlightStatus, Flight
from flight_manager.models.pilot import Pilot
from flight_manager.models.airports import Airport
from flight_manager.views.airport_menus import view_airports


def add_flight():
    with get_connection() as conn:
        flight_code = input("Flight code: ")
        company = input("Airline company: ")

        airports = Airport.get_all(conn)
        print("\nAvailable Airports:")
        for airport in airports:
            print(f"{airport.code} - {airport.name}")
        origin_code = input("Select origin airport (3 letters): ")
        origin_airport = Airport.get_by_code(conn, origin_code)
        if origin_airport is None:
            print(f"Airport with code {origin_code} not found")
            return

        dest_code = input("Select destination airport (3 letters): ")
        dest_airport = Airport.get_by_code(conn, dest_code)
        if dest_airport is None:
            print(f"Airport with code {dest_code} not found")
            return

        departure = input("Scheduled departure (YYYY-MM-DD HH:MM): ")
        arrival = input("Estimated arrival (YYYY-MM-DD HH:MM): ")

        flight = Flight.create(
            conn,
            flight_number=flight_code,
            origin_airport=origin_airport,
            destination_airport=dest_airport,
            scheduled_departure_time=datetime.strptime(departure, "%Y-%m-%d %H:%M"),
            estimated_arrival_time=datetime.strptime(arrival, "%Y-%m-%d %H:%M"),
            company=company,
        )
        print(f"Flight {flight.flight_number} created with ID {flight.flight_id}")


def assign_pilot_to_flight(flight: Flight):
    """Assign a pilot to a flight object without saving to database"""
    with get_connection() as conn:

        pilots = Pilot.get_all(conn)
        print("\nAvailable Pilots:")
        for i, pilot in enumerate(pilots, 1):
            print(f"{i}. {pilot.first_name} {pilot.last_name} (ID: {pilot.pilot_id})")
        pilot_idx = int(input("Select pilot (number): ")) - 1

        flight.pilot = pilots[pilot_idx]
        print(
            f"Pilot {pilots[pilot_idx].first_name} {pilots[pilot_idx].last_name} assigned to flight {flight.flight_number}"
        )


def view_flights():
    """View flights with optional filtering using key=value pairs"""
    print("Enter filter criteria as key=value pairs (comma separated)")
    print(
        "Available filters: flight_number, status, company, pilot_id, origin, destination"
    )
    print("Example: status=boarding,company=Delta,origin=JFK")
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

        flight_number = filters.get("flight_number")
        status = FlightStatus(filters["status"]) if "status" in filters else None
        company = filters.get("company")
        pilot_id = filters.get("pilot_id")
        origin_code = filters.get("origin")
        destination_code = filters.get("destination")

        pilot = None
        if pilot_id:
            pilot = Pilot.get_by_id(conn, pilot_id)
            if not pilot:
                print(f"\nError: No pilot found with ID {pilot_id}")
                return

        origin_airport = None
        if origin_code:
            origin_airport = Airport.get_by_code(conn, origin_code.upper())
            if not origin_airport:
                print(f"\nError: No airport found with code {origin_code}")
                return

        destination_airport = None
        if destination_code:
            destination_airport = Airport.get_by_code(conn, destination_code.upper())
            if not destination_airport:
                print(f"\nError: No airport found with code {destination_code}")
                return

        flights = Flight.get_all(
            conn,
            flight_number=flight_number,
            status=status,
            company=company,
            pilot=pilot,
            origin_airport=origin_airport,
            destination_airport=destination_airport,
        )

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


def update_flight_number(flight: Flight):
    new_value = input(
        f"Enter new flight number (current: {flight.flight_number}): "
    ).strip()
    if new_value:
        flight.flight_number = new_value


def update_origin_airport(flight: Flight):
    with get_connection() as conn:
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


def update_destination_airport(flight: Flight):
    with get_connection() as conn:
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


def update_scheduled_departure(flight: Flight):
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


def update_estimated_arrival(flight: Flight):
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


def update_status(flight: Flight):
    print("\nAvailable statuses:")
    for i, status in enumerate(FlightStatus, 1):
        print(f"{i}. {status.value}")
    status_choice = input(
        f"\nSelect new status (current: {flight.status.value}): "
    ).strip()
    if status_choice.isdigit() and 1 <= int(status_choice) <= len(FlightStatus):
        flight.status = list(FlightStatus)[int(status_choice) - 1]
    else:
        print("Invalid status selection")


def update_company(flight: Flight):
    new_company = input(f"Enter new company (current: {flight.company}): ").strip()
    if new_company:
        flight.company = new_company


def update_departure_time(flight: Flight):
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
                flight.departure_time = datetime.strptime(new_time, "%Y-%m-%d %H:%M")
            except ValueError:
                print("Invalid datetime format. Please use YYYY-MM-DD HH:MM")


def update_arrival_time(flight: Flight):
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
                flight.arrival_time = datetime.strptime(new_time, "%Y-%m-%d %H:%M")
            except ValueError:
                print("Invalid datetime format. Please use YYYY-MM-DD HH:MM")


def update_flight():
    """Update flight details through an interactive menu"""

    view_flights()

    flight_code = input("\nEnter ID of flight to update (or 'cancel' to abort): ").strip()
    if flight_code.lower() == "cancel":
        return

    with get_connection() as conn:
        flight = Flight.get_by_id(conn, flight_code)
        if not flight:
            print(f"No flight found with ID {flight_code}")
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
                update_flight_number(flight)
            elif choice == "2":
                update_origin_airport(flight)
            elif choice == "3":
                update_destination_airport(flight)
            elif choice == "4":
                update_scheduled_departure(flight)
            elif choice == "5":
                update_estimated_arrival(flight)
            elif choice == "6":
                update_status(flight)
            elif choice == "7":
                update_company(flight)
            elif choice == "8":
                assign_pilot_to_flight(flight)
            elif choice == "9":
                update_departure_time(flight)
            elif choice == "10":
                update_arrival_time(flight)
            else:
                print("Invalid choice. Please try again.")


def delete_flight():
    """Delete a flight through an interactive menu"""

    view_flights()

    flight_id = input("\nEnter ID of flight to delete (or 'cancel' to abort): ").strip()
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

        print("\nFlight to be deleted:")
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

        confirmation = (
            input("\nAre you sure you want to delete this flight? (y/n): ")
            .strip()
            .lower()
        )
        if confirmation == "y":
            try:
                flight.delete(conn)
                print(
                    f"\nFlight {flight.flight_number} (ID: {flight.flight_id}) deleted successfully!"
                )
            except Exception as e:
                print(f"\nError deleting flight: {str(e)}")
        else:
            print("\nDeletion cancelled. No changes were made.")


menu_options = [
    ("View Flights", view_flights),
    ("Add Flight", add_flight),
    ("Edit Flights", update_flight),
    ("Delete Flight", delete_flight),
]
