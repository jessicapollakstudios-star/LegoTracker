#!/usr/bin/env python3
# main.py
# Entry point for the LEGO Inventory Tracker.
# This file contains the main menu loop and one function per menu option.
# All the real work is done in database.py, api.py, and display.py.

import sys

import database
import api
import display
from config import VALID_STATUSES, REBRICKABLE_API_KEY


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def prompt(message):
    """Ask the user a question and return their answer (stripped of whitespace).

    Using a wrapper around input() makes it easy to find all the places
    where we ask the user for something.
    """
    return input(message).strip()


def confirm(message):
    """Ask a yes/no question. Returns True if the user types 'y' or 'yes'."""
    answer = prompt(f"{message} (y/n): ").lower()
    return answer in ("y", "yes")


def pick_from_list(items, display_fn=str):
    """Show a numbered list and return the chosen item, or None if cancelled.

    'items'      - the list of things to choose from
    'display_fn' - a function that turns each item into a display string

    The user types a number. If the number is out of range, or if they
    press Enter without typing anything, we return None.
    """
    for index, item in enumerate(items, start=1):
        print(f"  {index}. {display_fn(item)}")
    print()

    choice_str = prompt("Enter number (or press Enter to cancel): ")
    if not choice_str:
        return None

    try:
        choice_num = int(choice_str)
        if 1 <= choice_num <= len(items):
            return items[choice_num - 1]
        else:
            display.print_warning("That number is out of range.")
            return None
    except ValueError:
        display.print_warning("Please type a number.")
        return None


# ---------------------------------------------------------------------------
# Menu actions — one function per menu option
# ---------------------------------------------------------------------------

def action_add_set():
    """Add a new LEGO set by looking it up on Rebrickable."""
    display.print_info("Enter the LEGO set number (e.g., 75192 or 75192-1).")
    set_number = prompt("Set number: ")

    if not set_number:
        display.print_warning("No set number entered. Returning to menu.")
        return

    display.print_info("Looking up set on Rebrickable…")
    set_data = api.fetch_set_details(set_number)

    if set_data is None:
        display.print_error(
            f"Could not find set '{set_number}'. "
            "Check the number and make sure your API key is set in config.py."
        )
        return

    # Show the user what we found so they can confirm.
    display.print_set_preview(set_data)

    if not confirm("Does this look right? Save it to your collection?"):
        display.print_info("Cancelled. Nothing was saved.")
        return

    # Optional notes before saving.
    notes = prompt("Add any notes? (or press Enter to skip): ")

    # Ask for an initial status.
    display.print_info("What is the current status of this set?")
    display.print_status_menu(VALID_STATUSES)
    status_choice = prompt(f"Enter number (1–{len(VALID_STATUSES)}) or press Enter for 'In Box': ")

    status = "In Box"
    if status_choice:
        try:
            status_index = int(status_choice) - 1
            if 0 <= status_index < len(VALID_STATUSES):
                status = VALID_STATUSES[status_index]
            else:
                display.print_warning("Invalid choice, defaulting to 'In Box'.")
        except ValueError:
            display.print_warning("Invalid input, defaulting to 'In Box'.")

    # Save to the database.
    added = database.add_set(
        set_number  = set_data["set_number"],
        set_name    = set_data["set_name"],
        year        = set_data["year"],
        theme       = set_data["theme"],
        piece_count = set_data["piece_count"],
        status      = status,
        notes       = notes,
    )

    if added:
        display.print_success(f"'{set_data['set_name']}' added to your collection!")
    else:
        display.print_warning(
            f"Set {set_data['set_number']} is already in your collection."
        )


def action_list_sets():
    """Show all sets in the collection."""
    rows = database.get_all_sets()
    display.print_sets_table(rows, title="My LEGO Collection")


def action_update_status():
    """Change the status of an existing set."""
    set_number = prompt("Enter the set number to update (e.g., 75192-1): ")

    if not set_number:
        display.print_warning("No set number entered. Returning to menu.")
        return

    # Make sure the set exists before offering status choices.
    existing = database.get_set_by_number(set_number)

    # Try without the "-1" suffix if the user didn't include it.
    if existing is None and "-" not in set_number:
        existing = database.get_set_by_number(f"{set_number}-1")
        if existing:
            set_number = f"{set_number}-1"

    if existing is None:
        display.print_error(f"Set '{set_number}' not found in your collection.")
        return

    display.print_info(f"Current status of '{existing['set_name']}': {existing['status']}")
    display.print_status_menu(VALID_STATUSES)

    choice_str = prompt(f"Choose new status (1–{len(VALID_STATUSES)}): ")
    try:
        choice_index = int(choice_str) - 1
        if 0 <= choice_index < len(VALID_STATUSES):
            new_status = VALID_STATUSES[choice_index]
        else:
            display.print_warning("That number is out of range.")
            return
    except ValueError:
        display.print_warning("Please type a number.")
        return

    database.update_status(set_number, new_status)
    display.print_success(f"Status updated to '{new_status}'.")


def action_search():
    """Search the collection by set number, name, or theme."""
    query = prompt("Search for (set number, name, or theme): ")

    if not query:
        display.print_warning("No search term entered. Returning to menu.")
        return

    rows = database.search_sets(query)
    display.print_sets_table(rows, title=f"Search results for '{query}'")


def action_delete_set():
    """Remove a set from the collection."""
    set_number = prompt("Enter the set number to delete (e.g., 75192-1): ")

    if not set_number:
        display.print_warning("No set number entered. Returning to menu.")
        return

    existing = database.get_set_by_number(set_number)

    # Try without the "-1" suffix if needed.
    if existing is None and "-" not in set_number:
        existing = database.get_set_by_number(f"{set_number}-1")
        if existing:
            set_number = f"{set_number}-1"

    if existing is None:
        display.print_error(f"Set '{set_number}' not found in your collection.")
        return

    display.print_warning(
        f"You are about to delete '{existing['set_name']}' ({set_number})."
    )

    if not confirm("Are you sure?"):
        display.print_info("Cancelled. Nothing was deleted.")
        return

    database.delete_set(set_number)
    display.print_success(f"'{existing['set_name']}' has been removed from your collection.")


def action_show_stats():
    """Show overall collection statistics."""
    stats = database.get_stats()

    if stats["total_sets"] == 0:
        display.print_warning("Your collection is empty. Add some sets first!")
        return

    display.print_stats(stats)


# ---------------------------------------------------------------------------
# Startup checks
# ---------------------------------------------------------------------------

def check_api_key():
    """Warn the user if they haven't replaced the placeholder API key."""
    if REBRICKABLE_API_KEY == "your-key-here":
        display.print_warning(
            "Your Rebrickable API key is not set!\n"
            "  Open config.py and replace 'your-key-here' with your actual key.\n"
            "  Get a free key at: https://rebrickable.com/api/\n"
            "  (You can still view, search, and manage sets, but adding new ones will fail.)"
        )


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    """The main application loop.

    Sets up the database, then shows the menu over and over until
    the user chooses to exit.
    """
    # Make sure the database and table exist on first run.
    database.initialize_database()

    # Warn if the API key is still the placeholder.
    check_api_key()

    # Map each menu number to its action function.
    actions = {
        "1": action_add_set,
        "2": action_list_sets,
        "3": action_update_status,
        "4": action_search,
        "5": action_delete_set,
        "6": action_show_stats,
    }

    while True:
        display.print_menu()
        choice = prompt("Enter a number: ")

        if choice == "7":
            display.print_info("See you next time! Keep on building! 🧱")
            sys.exit(0)

        action = actions.get(choice)

        if action is None:
            display.print_warning("That's not a valid option. Please pick a number from 1 to 7.")
        else:
            # Run the chosen action. Any exception that reaches here is a bug
            # — print it so the user can report it, then keep the app alive.
            try:
                action()
            except KeyboardInterrupt:
                # Ctrl+C during an action cancels just that action.
                display.print_info("\nAction cancelled.")
            except Exception as error:
                display.print_error(f"Unexpected error: {error}")
                display.print_info("Returning to the main menu.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C from the main menu exits cleanly.
        print("\n")
        display.print_info("Goodbye! Keep on building! 🧱")
        sys.exit(0)
