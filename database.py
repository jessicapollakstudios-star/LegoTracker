# database.py
# All SQLite database operations for the LEGO Inventory Tracker.
# Each function does exactly one thing: talk to the database.

import sqlite3
from datetime import date

from config import DATABASE_FILE


def get_connection():
    """Open and return a connection to the SQLite database.

    Using check_same_thread=False is fine here because we only
    ever use one thread in this app (no async, no background tasks).
    """
    connection = sqlite3.connect(DATABASE_FILE)
    # Row factory lets us access columns by name (row["set_name"])
    # instead of by index (row[1]), which is much easier to read.
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the sets table if it doesn't already exist.

    This is safe to call every time the app starts — if the table
    already exists, nothing changes.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            set_number  TEXT    NOT NULL UNIQUE,
            set_name    TEXT    NOT NULL,
            year        INTEGER,
            theme       TEXT,
            piece_count INTEGER,
            status      TEXT    NOT NULL DEFAULT 'In Box',
            date_added  TEXT    NOT NULL,
            notes       TEXT
        )
    """)

    connection.commit()
    connection.close()


def add_set(set_number, set_name, year, theme, piece_count, status="In Box", notes=""):
    """Insert a new LEGO set into the database.

    Returns True if the set was added, or False if a set with that
    number already exists in the collection.
    """
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO sets
                (set_number, set_name, year, theme, piece_count, status, date_added, notes)
            VALUES
                (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            set_number,
            set_name,
            year,
            theme,
            piece_count,
            status,
            date.today().isoformat(),  # e.g. "2024-08-15"
            notes,
        ))
        connection.commit()
        return True

    except sqlite3.IntegrityError:
        # UNIQUE constraint on set_number was violated — already exists.
        return False

    finally:
        connection.close()


def get_all_sets():
    """Return every set in the collection, ordered by date added (newest first)."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM sets ORDER BY date_added DESC")
    rows = cursor.fetchall()

    connection.close()
    return rows


def search_sets(query):
    """Return sets where set_number, set_name, or theme matches the query.

    The search is case-insensitive and matches partial strings.
    For example, searching "star" will find sets named "Star Wars".
    """
    connection = get_connection()
    cursor = connection.cursor()

    # The % wildcards allow partial matches anywhere in the string.
    like_query = f"%{query}%"

    cursor.execute("""
        SELECT * FROM sets
        WHERE  set_number LIKE ?
           OR  set_name   LIKE ?
           OR  theme      LIKE ?
        ORDER BY set_name
    """, (like_query, like_query, like_query))

    rows = cursor.fetchall()
    connection.close()
    return rows


def get_set_by_number(set_number):
    """Return a single set row by its set number, or None if not found."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM sets WHERE set_number = ?", (set_number,))
    row = cursor.fetchone()

    connection.close()
    return row


def update_status(set_number, new_status):
    """Change the status of a set. Returns True if a row was updated."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE sets SET status = ? WHERE set_number = ?",
        (new_status, set_number),
    )
    connection.commit()

    # rowcount tells us how many rows were changed.
    updated = cursor.rowcount > 0
    connection.close()
    return updated


def update_notes(set_number, new_notes):
    """Update the notes field for a set. Returns True if a row was updated."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE sets SET notes = ? WHERE set_number = ?",
        (new_notes, set_number),
    )
    connection.commit()

    updated = cursor.rowcount > 0
    connection.close()
    return updated


def delete_set(set_number):
    """Remove a set from the collection. Returns True if a row was deleted."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM sets WHERE set_number = ?", (set_number,))
    connection.commit()

    deleted = cursor.rowcount > 0
    connection.close()
    return deleted


def get_stats():
    """Return summary statistics about the collection.

    Returns a dictionary with:
        total_sets    - total number of sets
        total_pieces  - sum of all piece counts
        by_status     - list of (status, count) tuples
        by_theme      - list of (theme, count) tuples, sorted by count
    """
    connection = get_connection()
    cursor = connection.cursor()

    # Total sets and pieces.
    cursor.execute("SELECT COUNT(*) as total_sets, SUM(piece_count) as total_pieces FROM sets")
    totals = cursor.fetchone()

    # Group by status.
    cursor.execute("""
        SELECT status, COUNT(*) as count
        FROM sets
        GROUP BY status
        ORDER BY count DESC
    """)
    by_status = cursor.fetchall()

    # Group by theme.
    cursor.execute("""
        SELECT theme, COUNT(*) as count
        FROM sets
        GROUP BY theme
        ORDER BY count DESC
    """)
    by_theme = cursor.fetchall()

    connection.close()

    return {
        "total_sets": totals["total_sets"] or 0,
        "total_pieces": totals["total_pieces"] or 0,
        "by_status": by_status,
        "by_theme": by_theme,
    }
