"""
storage.py - Reads and writes the CSV files in the data/ folder.

All data of the project lives in CSV files, so it is still there the next
time the program is started. Every row is a dictionary whose keys are the
column names, e.g. {"subject": "Calculus", "attended": "18", "total": "20"}.
(CSV stores everything as text; each module converts to int/float itself.)
"""
import csv
import os

# data/ folder next to main.py. Tests change this variable to use a temp folder.
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)

# key -> (file name, column names)
SCHEMAS = {
    "subjects": ("subjects.csv", ["name"]),
    "attendance": ("attendance.csv", ["subject", "attended", "total"]),
    "marks": ("marks.csv", ["subject", "exam", "scored", "maximum"]),
    "assignments": ("assignments.csv", ["title", "subject", "deadline", "status"]),
    "expenses": ("expenses.csv", ["date", "category", "amount", "note"]),
    "settings": ("settings.csv", ["key", "value"]),
}


def _path(key):
    return os.path.join(DATA_DIR, SCHEMAS[key][0])


def load(key):
    """Return all rows of a CSV file as a list of dictionaries."""
    fields = SCHEMAS[key][1]
    path = _path(key)
    if not os.path.exists(path):
        return []
    rows = []
    try:
        with open(path, newline="", encoding="utf-8") as file:
            for row in csv.DictReader(file):
                # Skip damaged rows that miss a column.
                if all(row.get(name) is not None for name in fields):
                    rows.append({name: row[name] for name in fields})
    except (OSError, csv.Error) as error:
        print(f"  Warning: could not read {SCHEMAS[key][0]} ({error}).")
        return []
    return rows


def save(key, rows):
    """Write a list of dictionaries to its CSV file (replaces old content)."""
    fields = SCHEMAS[key][1]
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(_path(key), "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return True
    except OSError as error:
        print(f"  Error: could not save {SCHEMAS[key][0]} ({error}).")
        return False


def get_setting(name, default=None):
    """Read one value from settings.csv."""
    for row in load("settings"):
        if row["key"] == name:
            return row["value"]
    return default


def set_setting(name, value):
    """Store one value in settings.csv."""
    rows = [row for row in load("settings") if row["key"] != name]
    rows.append({"key": name, "value": str(value)})
    save("settings", rows)
