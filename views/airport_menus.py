from models.db import get_connection
from models.airports import Airport, AirportStatus

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
    
    # First show all airports so user can choose which to update
    view_airports()
    
    # Get airport code to update
    airport_code = input("\nEnter code of airport to update (or 'cancel' to abort): ").strip().upper()
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
                try:
                    airport.save(conn)
                    print("\nAirport updated successfully!")
                    print(f"Updated airport {airport.code}")
                    break
                except Exception as e:
                    print(f"\nError saving airport: {str(e)}")
            elif choice == "c":
                print("\nUpdate cancelled. No changes were made.")
                break
            elif choice == "1":
                new_name = input(f"Enter new name (current: {airport.name}): ").strip()
                if new_name:
                    airport.name = new_name
            elif choice == "2":
                new_address = input(f"Enter new address (current: {airport.address}): ").strip()
                if new_address:
                    airport.address = new_address
            elif choice == "3":
                print("\nAvailable statuses:")
                for i, status in enumerate(AirportStatus, 1):
                    print(f"{i}. {status.value}")
                status_choice = input(
                    f"\nSelect new status (current: {airport.status.value}): "
                ).strip()
                if status_choice.isdigit() and 1 <= int(status_choice) <= len(AirportStatus):
                    airport.status = list(AirportStatus)[int(status_choice) - 1]
                else:
                    print("Invalid status selection")
            else:
                print("Invalid choice. Please try again.")


menu_options = [
    ("View Airports", view_airports),
    ("Add Airport", add_airport),
    ("Update Airport", update_airport)
]