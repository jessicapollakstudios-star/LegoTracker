# display.py
# All terminal output formatting using the Rich library.
# Nothing in this file talks to the database or the API.

from rich.console import Console
from rich.table import Table
from rich import box

# A single shared Console object that all functions use.
# Rich uses this to print styled text to the terminal.
console = Console()


# ---------------------------------------------------------------------------
# Simple message helpers
# ---------------------------------------------------------------------------

def print_success(message):
    """Print a green success message."""
    console.print(f"[bold green]✓ {message}[/bold green]")


def print_warning(message):
    """Print a yellow warning message."""
    console.print(f"[bold yellow]⚠ {message}[/bold yellow]")


def print_error(message):
    """Print a red error message."""
    console.print(f"[bold red]✗ {message}[/bold red]")


def print_info(message):
    """Print a regular informational message."""
    console.print(f"[cyan]{message}[/cyan]")


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

def print_menu():
    """Print the main menu with numbered options."""
    console.print()
    console.print("[bold yellow]╔══════════════════════════════════╗[/bold yellow]")
    console.print("[bold yellow]║   🧱 Carson's LEGO Tracker   🧱  ║[/bold yellow]")
    console.print("[bold yellow]╚══════════════════════════════════╝[/bold yellow]")
    console.print()
    console.print("  [bold]1.[/bold] Add a set")
    console.print("  [bold]2.[/bold] List all sets")
    console.print("  [bold]3.[/bold] Update set status")
    console.print("  [bold]4.[/bold] Search collection")
    console.print("  [bold]5.[/bold] Delete a set")
    console.print("  [bold]6.[/bold] Collection stats")
    console.print("  [bold]7.[/bold] Exit")
    console.print()


# ---------------------------------------------------------------------------
# Set tables
# ---------------------------------------------------------------------------

def _status_color(status):
    """Return a Rich color name for a given status string."""
    colors = {
        "Built":      "green",
        "In Box":     "blue",
        "In Storage": "cyan",
        "Incomplete": "yellow",
        "At Paps":        "magenta",
        "Inbox at Paps":  "bright_magenta",
        "Built at Paps":  "green",
    }
    # Default to white if the status is somehow unexpected.
    return colors.get(status, "white")


def print_sets_table(rows, title="My LEGO Collection"):
    """Print a Rich table showing a list of sets.

    'rows' is a list of sqlite3.Row objects from database.py.
    Each row has columns: set_number, set_name, year, theme,
                          piece_count, status, date_added, notes.
    """
    if not rows:
        print_warning("No sets found.")
        return

    # Create a table with a colored border.
    table = Table(
        title=f"[bold]{title}[/bold]",
        box=box.ROUNDED,
        border_style="yellow",
        show_lines=False,
        expand=False,
    )

    # Define the columns.
    table.add_column("#",           style="dim",    width=4,  justify="right")
    table.add_column("Set Number",  style="bold",   min_width=10)
    table.add_column("Name",                        min_width=25)
    table.add_column("Year",        justify="right",width=6)
    table.add_column("Theme",                       min_width=14)
    table.add_column("Pieces",      justify="right",width=7)
    table.add_column("Status",                      min_width=12)
    table.add_column("Date Added",                  width=12)

    for index, row in enumerate(rows, start=1):
        status = row["status"]
        color  = _status_color(status)

        table.add_row(
            str(index),
            row["set_number"],
            row["set_name"],
            str(row["year"] or "—"),
            row["theme"] or "—",
            str(row["piece_count"] or "—"),
            f"[{color}]{status}[/{color}]",
            row["date_added"],
        )

    console.print()
    console.print(table)
    console.print(f"  [dim]{len(rows)} set(s) shown.[/dim]")
    console.print()


# ---------------------------------------------------------------------------
# Set detail / confirmation panel
# ---------------------------------------------------------------------------

def print_set_preview(set_data):
    """Print a preview panel for a set fetched from the API.

    Used when adding a set so the user can confirm before saving.
    'set_data' is the dictionary returned by api.fetch_set_details().
    """
    console.print()
    console.print("[bold cyan]─── Set found on Rebrickable ───────────────────[/bold cyan]")
    console.print(f"  [bold]Set Number:[/bold]  {set_data['set_number']}")
    console.print(f"  [bold]Name:[/bold]        {set_data['set_name']}")
    console.print(f"  [bold]Year:[/bold]        {set_data['year']}")
    console.print(f"  [bold]Theme:[/bold]       {set_data['theme']}")
    console.print(f"  [bold]Pieces:[/bold]      {set_data['piece_count']}")
    console.print("[bold cyan]────────────────────────────────────────────────[/bold cyan]")
    console.print()


# ---------------------------------------------------------------------------
# Stats display
# ---------------------------------------------------------------------------

def print_stats(stats):
    """Print a summary of the whole collection.

    'stats' is the dictionary returned by database.get_stats().
    """
    console.print()
    console.print("[bold yellow]╔══════════════════════════╗[/bold yellow]")
    console.print("[bold yellow]║   Collection Statistics  ║[/bold yellow]")
    console.print("[bold yellow]╚══════════════════════════╝[/bold yellow]")
    console.print()

    console.print(f"  [bold]Total sets:[/bold]   [green]{stats['total_sets']}[/green]")
    console.print(f"  [bold]Total pieces:[/bold] [green]{stats['total_pieces']:,}[/green]")
    console.print()

    # --- By status ---
    if stats["by_status"]:
        status_table = Table(
            title="Breakdown by Status",
            box=box.SIMPLE,
            show_header=True,
        )
        status_table.add_column("Status", min_width=14)
        status_table.add_column("Sets", justify="right")

        for row in stats["by_status"]:
            color = _status_color(row["status"])
            status_table.add_row(
                f"[{color}]{row['status']}[/{color}]",
                str(row["count"]),
            )
        console.print(status_table)
        console.print()

    # --- By theme ---
    if stats["by_theme"]:
        theme_table = Table(
            title="Breakdown by Theme",
            box=box.SIMPLE,
            show_header=True,
        )
        theme_table.add_column("Theme", min_width=18)
        theme_table.add_column("Sets", justify="right")

        for row in stats["by_theme"]:
            theme_table.add_row(
                row["theme"] or "Unknown",
                str(row["count"]),
            )
        console.print(theme_table)

    console.print()


# ---------------------------------------------------------------------------
# Status picker
# ---------------------------------------------------------------------------

def print_status_menu(valid_statuses):
    """Print the numbered status options for the update-status flow."""
    console.print()
    console.print("[bold]Choose a new status:[/bold]")
    for index, status in enumerate(valid_statuses, start=1):
        color = _status_color(status)
        console.print(f"  [bold]{index}.[/bold] [{color}]{status}[/{color}]")
    console.print()
