from typing import Callable
from models.pilot import Pilot
from models.airports import Airport
from models.flight import Flight
from views.airport_menus import menu_options as aiport_menu
from views.pilot_menus import menu_options as pilot_menu
from views.flight_menus import menu_options as flight_menu
from views.menu import create_menu

from models.db import get_connection


def initialize_database():
    with get_connection() as conn:
        Airport.create_table(conn)
        Pilot.create_table(conn)
        Flight.create_table(conn)


def main():
    menu_options = [
        ("View/Edit Airports", create_menu("Airports", aiport_menu)),
        ("View/Edit Pilots", create_menu("Pilots", pilot_menu)),
        ("View/Edit Flights", create_menu("Flights", flight_menu))
    ]
    create_menu("Airline Management System", menu_options)()
    print("\nGoodbye!")


if __name__ == "__main__":
    main()
