from flight_manager.models.db import get_connection
from flight_manager.models.airports import Airport, AirportStatus
from flight_manager.models.flight import Flight


def add_airport():
    with get_connection() as conn:
        code = input("Airport code (3 letters): ").upper()
        name = input("Airport name: ")
        address = input("Address: ")

        print("\nSelect airport status:")
        for i, status in enumerate(AirportStatus, 1):
            print(f"{i}. {status.value}")
        status_choice = input("Enter status number: ").strip()

        if status_choice.isdigit() and 1 <= int(status_choice) <= len(AirportStatus):
            status = list(AirportStatus)[int(status_choice) - 1]
            Airport.create(conn, code, name, address, status)
            print(f"Airport {code} added successfully!")
        else:
            print("Invalid status selection")


def view_airports():
    """View all airports with their details"""
    with get_connection() as conn:
        airports = Airport.get_all(conn)

    print("\nAll Airports:")
    if not airports:
        print("No airports found")
        return

    for airport in airports:
        print(
            f"Code: {airport.code} | Name: {airport.name} | "
            f"Address: {airport.address} | Status: {airport.status.value}"
        )


def update_airport():
    """Update airport details through an interactive menu"""
    print("\nUpdate Airport")

    view_airports()

    airport_code = (
        input("\nEnter code of airport to update (or 'cancel' to abort): ")
        .strip()
        .upper()
    )
    if airport_code.lower() == "cancel":
        return
    if len(airport_code) != 3:
        print("Airport code must be 3 letters")
        return

    with get_connection() as conn:
        airport = Airport.get_by_code(conn, airport_code)
        if not airport:
            print(f"No airport found with code {airport_code}")
            return

        while True:
            print("\nCurrent airport details:")
            print(f"1. Name: {airport.name}")
            print(f"2. Address: {airport.address}")
            print(f"3. Status: {airport.status.value}")

            print("\nSelect field to update:")
            print("1-3: Update corresponding field")
            print("s: Save changes")
            print("c: Cancel without saving")

            choice = input("\nEnter your choice: ").strip().lower()

            if choice == "s":
                airport.update(conn)
                print("\nAirport updated successfully!")
                print(f"Updated airport {airport.code}")
                break
            elif choice == "c":
                print("\nUpdate cancelled. No changes were made.")
                break
            elif choice == "1":
                new_name = input(f"Enter new name (current: {airport.name}): ").strip()
                if new_name:
                    airport.name = new_name
            elif choice == "2":
                new_address = input(
                    f"Enter new address (current: {airport.address}): "
                ).strip()
                if new_address:
                    airport.address = new_address
            elif choice == "3":
                print("\nAvailable statuses:")
                for i, status in enumerate(AirportStatus, 1):
                    print(f"{i}. {status.value}")
                status_choice = input(
                    f"\nSelect new status (current: {airport.status.value}): "
                ).strip()
                if status_choice.isdigit() and 1 <= int(status_choice) <= len(
                    AirportStatus
                ):
                    airport.status = list(AirportStatus)[int(status_choice) - 1]
                else:
                    print("Invalid status selection")
            else:
                print("Invalid choice. Please try again.")


def delete_airport():
    """Delete an airport through an interactive menu"""
    view_airports()

    airport_code = (
        input("\nEnter code of airport to delete (or 'cancel' to abort): ")
        .strip()
        .upper()
    )
    if airport_code.lower() == "cancel":
        return
    if len(airport_code) != 3:
        print("Airport code must be 3 letters")
        return

    with get_connection() as conn:
        airport = Airport.get_by_code(conn, airport_code)
        if not airport:
            print(f"No airport found with code {airport_code}")
            return

        print("\nAirport to be deleted:")
        print(
            f"Code: {airport.code} | Name: {airport.name} | "
            f"Address: {airport.address} | Status: {airport.status.value}"
        )

        confirmation = (
            input("\nAre you sure you want to delete this airport? (y/n): ")
            .strip()
            .lower()
        )
        if confirmation == "y":
            try:
                flights = Flight.get_all(conn, origin_airport=airport) + Flight.get_all(
                    conn, destination_airport=airport
                )
                if flights:
                    print(
                        "\nCannot delete airport - it is referenced in the following flights:"
                    )
                    for flight in flights:
                        print(f"Flight {flight.flight_number} (ID: {flight.flight_id})")
                    print("\nPlease delete or update these flights first.")
                    return

                airport.delete(conn)
                print(f"\nAirport {airport.code} deleted successfully!")
            except Exception as e:
                print(f"\nError deleting airport: {str(e)}")
        else:
            print("\nDeletion cancelled. No changes were made.")


menu_options = [
    ("View Airports", view_airports),
    ("Add Airport", add_airport),
    ("Update Airport", update_airport),
    ("Delete Airport", delete_airport),
]
