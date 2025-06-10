from flight_manager.models.pilot import Pilot
from flight_manager.models.airports import Airport
from flight_manager.models.flight import Flight
from flight_manager.views.airport_menus import menu_options as aiport_menu
from flight_manager.views.pilot_menus import menu_options as pilot_menu
from flight_manager.views.flight_menus import menu_options as flight_menu
from flight_manager.views.menu import create_menu

from flight_manager.models.db import get_connection


def initialize_database():
    with get_connection() as conn:
        Airport.create_table(conn)
        Pilot.create_table(conn)
        Flight.create_table(conn)


def main():
    initialize_database()
    menu_options = [
        ("View/Edit Airports", create_menu("Airports", aiport_menu)),
        ("View/Edit Pilots", create_menu("Pilots", pilot_menu)),
        ("View/Edit Flights", create_menu("Flights", flight_menu))
    ]
    create_menu("Airline Management System", menu_options)()
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
