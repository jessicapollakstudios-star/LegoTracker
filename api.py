# api.py
# All communication with the Rebrickable API.
# Each function returns either data or None on failure.

import requests

from config import REBRICKABLE_API_KEY, REBRICKABLE_BASE_URL


def _get_headers():
    """Build the authorization headers required by Rebrickable.

    The API key goes in the Authorization header, not the URL,
    so it doesn't accidentally end up in server logs.
    """
    return {"Authorization": f"key {REBRICKABLE_API_KEY}"}


def fetch_set_details(set_number):
    """Look up a LEGO set by its set number on Rebrickable.

    Rebrickable set numbers usually end with "-1" (e.g., "75192-1").
    This function tries the number as-is first, then appends "-1"
    automatically so users don't have to remember that detail.

    Returns a dictionary with these keys on success:
        set_number  - the Rebrickable set number (e.g., "75192-1")
        set_name    - the official LEGO set name
        year        - the year the set was released
        theme       - the theme name (e.g., "Star Wars")
        piece_count - number of pieces in the set

    Returns None on any error (bad set number, network issue, etc.).
    """
    # If the user typed "75192", turn it into "75192-1".
    # If they already typed "75192-1", leave it alone.
    if "-" not in set_number:
        rebrickable_number = f"{set_number}-1"
    else:
        rebrickable_number = set_number

    url = f"{REBRICKABLE_BASE_URL}/lego/sets/{rebrickable_number}/"

    try:
        response = requests.get(url, headers=_get_headers(), timeout=10)

        if response.status_code == 404:
            # The set number doesn't exist in Rebrickable's database.
            return None

        if response.status_code == 401:
            # The API key is wrong or missing.
            print("\n[API Error] Invalid API key. Please check config.py.")
            return None

        if response.status_code == 429:
            # We sent too many requests too fast.
            print("\n[API Error] Rate limited by Rebrickable. Please wait a moment and try again.")
            return None

        # For any other non-200 status, raise an exception.
        response.raise_for_status()

        data = response.json()

        # Rebrickable stores theme info in a separate "theme_id" field.
        # We fetch the theme name in a second call below.
        theme_name = fetch_theme_name(data.get("theme_id"))

        return {
            "set_number": data["set_num"],
            "set_name": data["name"],
            "year": data["year"],
            "theme": theme_name,
            "piece_count": data["num_parts"],
        }

    except requests.exceptions.ConnectionError:
        print("\n[API Error] Could not connect to Rebrickable. Check your internet connection.")
        return None

    except requests.exceptions.Timeout:
        print("\n[API Error] The request timed out. Rebrickable might be slow — try again.")
        return None

    except requests.exceptions.RequestException as error:
        print(f"\n[API Error] Something went wrong: {error}")
        return None


def fetch_theme_name(theme_id):
    """Look up a theme name by its numeric ID.

    Rebrickable stores themes separately from sets, so we need this
    second API call to get a human-readable name like "Star Wars".

    Returns the theme name string, or "Unknown" if anything goes wrong.
    """
    if theme_id is None:
        return "Unknown"

    url = f"{REBRICKABLE_BASE_URL}/lego/themes/{theme_id}/"

    try:
        response = requests.get(url, headers=_get_headers(), timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get("name", "Unknown")

    except requests.exceptions.RequestException:
        # Theme lookup failing is not critical — just return a fallback.
        return "Unknown"
