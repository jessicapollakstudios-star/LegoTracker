# config.example.py
# ---------------------------------------------------------------
# SETUP INSTRUCTIONS:
# 1. Copy this file and rename the copy to config.py
# 2. Replace "your-key-here" with your real Rebrickable API key
# 3. Get a free key at: https://rebrickable.com/api/
# ---------------------------------------------------------------

REBRICKABLE_API_KEY = "your-key-here"

REBRICKABLE_BASE_URL = "https://rebrickable.com/api/v3"

DATABASE_FILE = "lego_collection.db"

VALID_STATUSES = [
    "Built",
    "In Box",
    "In Storage",
    "Incomplete",
    "At Paps",
    "Inbox at Paps",
    "Built at Paps",
]
