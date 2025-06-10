from flight_manager.models.db import get_connection
from flight_manager.models.pilot import Pilot
from flight_manager.models.flight import Flight

def add_pilot():
    with get_connection() as conn:
        first_name = input("First name: ")
        last_name = input("Last name: ")
        pilot = Pilot.create(conn, first_name, last_name)
    print(f"Pilot {pilot.pilot_id} created successfully!")


def view_pilots():
    """View all pilots with their details"""
    with get_connection() as conn:
        pilots = Pilot.get_all(conn)
        
    print("\nAll Pilots:")
    if not pilots:
        print("No pilots found")
        return
        
    for pilot in pilots:
        print(
            f"ID: {pilot.pilot_id} | Name: {pilot.first_name} {pilot.last_name}"
        )


def update_pilot():
    """Update pilot details through an interactive menu"""
    
    # First show all pilots so user can choose which to update
    view_pilots()
    
    # Get pilot ID to update
    pilot_id = input("\nEnter ID of pilot to update (or 'cancel' to abort): ").strip().upper()
    if pilot_id.lower() == "cancel":
        return

    with get_connection() as conn:
        pilot = Pilot.get_by_id(conn, pilot_id)
        if not pilot:
            print(f"No pilot found with ID {pilot_id}")
            return

        while True:
            print("\nCurrent pilot details:")
            print(f"1. First Name: {pilot.first_name}")
            print(f"2. Last Name: {pilot.last_name}")
            
            print("\nSelect field to update:")
            print("1-2: Update corresponding field")
            print("s: Save changes")
            print("c: Cancel without saving")

            choice = input("\nEnter your choice: ").strip().lower()

            if choice == "s":
                try:
                    pilot.save(conn)
                    print("\nPilot updated successfully!")
                    print(f"Updated pilot ID {pilot.pilot_id}")
                    break
                except Exception as e:
                    print(f"\nError saving pilot: {str(e)}")
            elif choice == "c":
                print("\nUpdate cancelled. No changes were made.")
                break
            elif choice == "1":
                new_first_name = input(f"Enter new first name (current: {pilot.first_name}): ").strip()
                if new_first_name:
                    pilot.first_name = new_first_name
            elif choice == "2":
                new_last_name = input(f"Enter new last name (current: {pilot.last_name}): ").strip()
                if new_last_name:
                    pilot.last_name = new_last_name
            else:
                print("Invalid choice. Please try again.")


def delete_pilot():
    """Delete a pilot through an interactive menu"""
    # First show all pilots so user can choose which to delete
    view_pilots()

    # Get pilot ID to delete
    pilot_id = input("\nEnter ID of pilot to delete (or 'cancel' to abort): ").strip()
    if pilot_id.lower() == "cancel":
        return
    if not pilot_id.isdigit():
        print("Invalid pilot ID - must be a number")
        return

    with get_connection() as conn:
        pilot = Pilot.get_by_id(conn, int(pilot_id))
        if not pilot:
            print(f"No pilot found with ID {pilot_id}")
            return

        # Show confirmation with pilot details
        print("\nPilot to be deleted:")
        print(f"ID: {pilot.pilot_id} | Name: {pilot.first_name} {pilot.last_name}")

        # Check if pilot is assigned to any flights
        flights = Flight.get_all(conn, pilot=pilot)
        if flights:
            print("\nCannot delete pilot - assigned to the following flights:")
            for flight in flights:
                print(f"Flight {flight.flight_number} (ID: {flight.flight_id})")
            print("\nPlease reassign or delete these flights first.")
            return

        confirmation = input("\nAre you sure you want to delete this pilot? (y/n): ").strip().lower()
        if confirmation == 'y':
            try:
                pilot.delete(conn)
                print(f"\nPilot {pilot.first_name} {pilot.last_name} (ID: {pilot.pilot_id}) deleted successfully!")
            except Exception as e:
                print(f"\nError deleting pilot: {str(e)}")
        else:
            print("\nDeletion cancelled. No changes were made.")


menu_options = [
    ("View Pilots", view_pilots),
    ("Add Pilot", add_pilot),
    ("Update Pilot", update_pilot),
    ("Delete Pilot", delete_pilot)
]
