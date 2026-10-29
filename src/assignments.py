"""
assignments.py - Assignments and deadlines.

Each record is a dictionary:
    {"title": "Lab 3", "subject": "Physics", "deadline": "2026-11-05", "status": "Pending"}

Features: days-left calculation, overdue detection and deadline CLASH
detection (two or more pending assignments due on the same day).
"""
from datetime import date

from src import storage, subjects, utils

PENDING = "Pending"
DONE = "Done"


# ---------- data handling ----------
def load_assignments():
    rows = []
    for row in storage.load("assignments"):
        if utils.parse_date(row["deadline"]) is None:
            continue  # ignore damaged rows
        if row["status"] not in (PENDING, DONE):
            row["status"] = PENDING
        rows.append(row)
    return rows


def save_assignments(rows):
    storage.save("assignments", rows)


# ---------- calculations ----------
def days_left(deadline_text, today=None):
    """Days from today to the deadline (negative = overdue). None if invalid."""
    deadline = utils.parse_date(deadline_text)
    if deadline is None:
        return None
    today = today or date.today()
    return (deadline - today).days


def urgency_label(days):
    if days is None:
        return "Unknown"
    if days < 0:
        return f"OVERDUE by {-days} day(s)"
    if days == 0:
        return "Due TODAY"
    if days == 1:
        return "Due tomorrow"
    return f"{days} days left"


def pending_only(rows):
    return [row for row in rows if row["status"] == PENDING]


def sort_for_display(rows):
    """Pending first (earliest deadline first), finished ones at the end."""
    return sorted(rows, key=lambda row: (row["status"] == DONE, row["deadline"]))


def find_deadline_clashes(rows):
    """Return {deadline: [titles]} for dates with 2+ pending assignments."""
    by_date = {}
    for row in pending_only(rows):
        by_date.setdefault(row["deadline"], []).append(row["title"])
    return {day: titles for day, titles in by_date.items() if len(titles) >= 2}


# ---------- screens ----------
def add_assignment():
    subject = subjects.choose_subject("Assignment is for which subject")
    if subject is None:
        return
    title = utils.get_text("Assignment title: ")
    today = date.today()
    while True:
        deadline = utils.get_date("Deadline (YYYY-MM-DD): ")
        if deadline < today and not utils.confirm("That date is in the past. Add anyway?"):
            continue
        break
    rows = load_assignments()
    rows.append({"title": title, "subject": subject,
                 "deadline": deadline.isoformat(), "status": PENDING})
    save_assignments(rows)
    print("  Assignment added.")
    clashes = find_deadline_clashes(rows)
    if deadline.isoformat() in clashes:
        print(f"  WARNING: deadline clash on {deadline.isoformat()}: "
              + ", ".join(clashes[deadline.isoformat()]))


def view_assignments():
    rows = sort_for_display(load_assignments())
    if not rows:
        print("  No assignments yet.")
        return rows
    utils.header("ASSIGNMENTS")
    print(f"{'#':<4}{'Title':<22}{'Subject':<18}{'Deadline':<12}Status")
    utils.line()
    for number, row in enumerate(rows, start=1):
        if row["status"] == DONE:
            state = "Done"
        else:
            state = urgency_label(days_left(row["deadline"]))
        print(f"{number:<4}{row['title']:<22}{row['subject']:<18}{row['deadline']:<12}{state}")
    clashes = find_deadline_clashes(rows)
    if clashes:
        utils.line()
        for day, titles in sorted(clashes.items()):
            print(f"  CLASH on {day}: " + ", ".join(titles))
    return rows


def mark_done():
    rows = load_assignments()
    shown = sort_for_display(rows)
    if not pending_only(shown):
        print("  No pending assignments.")
        return
    view_assignments()
    number = utils.get_int("Number of the assignment you finished (0 to cancel): ", 0, len(shown))
    if number == 0:
        return
    chosen = shown[number - 1]
    if chosen["status"] == DONE:
        print("  That one is already done.")
        return
    chosen["status"] = DONE      # `shown` holds the same dictionaries as `rows`
    save_assignments(rows)
    print("  Marked as done. Well done!")


def delete_assignment():
    rows = load_assignments()
    shown = sort_for_display(rows)
    if not shown:
        print("  No assignments to delete.")
        return
    view_assignments()
    number = utils.get_int("Number of the assignment to delete (0 to cancel): ", 0, len(shown))
    if number == 0:
        return
    chosen = shown[number - 1]
    rows = [row for row in rows if row is not chosen]
    save_assignments(rows)
    print("  Deleted.")


def menu():
    while True:
        choice = utils.show_menu("ASSIGNMENTS & DEADLINES", [
            "Add an assignment",
            "View assignments",
            "Mark an assignment as done",
            "Delete an assignment",
        ])
        if choice == 0:
            return
        if choice == 1:
            add_assignment()
        elif choice == 2:
            view_assignments()
        elif choice == 3:
            mark_done()
        elif choice == 4:
            delete_assignment()
        utils.pause()
