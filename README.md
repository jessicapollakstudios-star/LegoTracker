# 🧱 Carson's LEGO Tracker

A command-line app for tracking a LEGO collection — built by Carson and his aunt as a learning project. Add sets by number, see them in a colorful table, update their status, and browse collection stats, all from your terminal.

Built with Python, SQLite, and the [Rebrickable API](https://rebrickable.com/api/).

---

## Features

- **Add sets by number** — pulls the name, piece count, year, and theme automatically from Rebrickable
- **Colorful table view** — see your whole collection at a glance
- **Status tracking** — Built, In Box, In Storage, Incomplete, At Paps, Inbox at Paps, Built at Paps
- **Search** — by set number, name, or theme
- **Collection stats** — total sets, total pieces, breakdown by status and theme
- **Works on Mac and PC**

---

## Setup

### 1. Make sure Python is installed

```bash
python3 --version
```

Download from [python.org](https://www.python.org/downloads/) if needed. Check **"Add to PATH"** on Windows.

### 2. Clone or download this repo

```bash
git clone https://github.com/YOUR_USERNAME/carsons-lego-tracker.git
cd carsons-lego-tracker
```

### 3. Set up your config file

```bash
cp config.example.py config.py
```

Open `config.py` and replace `"your-key-here"` with your Rebrickable API key.

### 4. Get a free Rebrickable API key

1. Go to [https://rebrickable.com/api/](https://rebrickable.com/api/)
2. Create a free account and click **Generate new key**
3. Paste the key into `config.py`

### 5. Install dependencies

```bash
pip3 install -r requirements.txt
```

### 6. Run it

```bash
python3 main.py
```

On Windows:
```powershell
python main.py
```

---

## How to Use

| Option | What it does |
|--------|-------------|
| 1 | Add a set by entering its number (e.g., `75192`) |
| 2 | List every set in the collection |
| 3 | Update a set's status |
| 4 | Search by name, set number, or theme |
| 5 | Remove a set |
| 6 | View collection stats |
| 7 | Exit |

---

## Project Structure

```
carsons-lego-tracker/
├── main.py             # Entry point and menu loop
├── database.py         # All SQLite operations
├── api.py              # Rebrickable API calls
├── display.py          # Rich table formatting and output
├── config.example.py   # Config template (copy to config.py)
├── requirements.txt    # Python dependencies
└── README.md
```

---

## What We Learned Building This

- How to call a real API using Python (`requests`)
- How to store data in a SQLite database
- How to split code across multiple files
- How to make a terminal app look great with the `rich` library
- How to use git and GitHub to share code

---

## Future Ideas

- Add current market value tracking (BrickLink integration)
- Export collection to CSV
- Track missing pieces per set
- Add photo/location notes for storage tracking
- Barcode scanning via webcam

---

*Built with ❤️ by Carson and his aunt.*
