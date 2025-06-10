from typing import Callable

def create_menu(title: str, menu_options: list[tuple[str, Callable[[], None]]]):
    def menu():
        while True:
            print(f"\n{title}\n")
            for key, (text, _) in enumerate(menu_options, 1):
                print(f"{key}. {text}")
            print(f"{len(menu_options) + 1}. Exit Menu")

            try:
                choice = int(input("\nEnter your choice: "))
            except ValueError:
                print("Invalid choice, please try again.")
                continue
        
            if choice == len(menu_options) + 1:
                break

            elif choice <= len(menu_options) and choice >= 1:
                menu_options[choice - 1][1]()
            else:
                print("Invalid choice, please try again.")
    return menu