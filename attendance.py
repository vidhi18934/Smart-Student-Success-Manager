"""
attendance.py - Attendance tracking.

Each record is a dictionary:
    {"subject": "Calculus", "attended": 18, "total": 20}

Feature: calculates the percentage, marks LOW attendance (below 75%) and
works out how many classes must be attended to recover, or how many classes
can still be skipped safely.
"""
from src import storage, subjects, utils

TARGET = 75          # minimum required attendance in percent
WARNING_MARGIN = 5   # within 5% above the target is "borderline"


# ---------- data handling ----------
def load_attendance():
    records = []
    for row in storage.load("attendance"):
        try:
            records.append({
                "subject": row["subject"],
                "attended": int(row["attended"]),
                "total": int(row["total"]),
            })
        except ValueError:
            continue  # ignore damaged rows
    return records


def save_attendance(records):
    storage.save("attendance", records)


def find_record(records, subject):
    for record in records:
        if record["subject"] == subject:
            return record
    return None


# ---------- calculations (no input/print, so they are easy to test) ----------
def percentage(attended, total):
    """Attendance percentage. 0 if no classes have been held."""
    if total <= 0:
        return 0.0
    return attended / total * 100


def classes_needed(attended, total, target=TARGET):
    """
    Minimum number of consecutive classes to attend to reach `target` %.
    Solve (attended + x) / (total + x) >= target/100 for x.
    """
    if total <= 0 or percentage(attended, total) >= target:
        return 0
    numerator = target * total - 100 * attended
    denominator = 100 - target
    return -(-numerator // denominator)  # ceiling division


def classes_can_skip(attended, total, target=TARGET):
    """
    Maximum number of future classes that can be missed while staying at or
    above `target` %. Solve attended / (total + m) >= target/100 for m.
    """
    if total <= 0 or percentage(attended, total) < target:
        return 0
    return max(0, (100 * attended - target * total) // target)


def status(pct, target=TARGET):
    """Return 'LOW', 'BORDERLINE' or 'OK'."""
    if pct < target:
        return "LOW"
    if pct < target + WARNING_MARGIN:
        return "BORDERLINE"
    return "OK"


def mark_class(records, subject, present):
    """Add one class (present or absent) to a subject's record."""
    record = find_record(records, subject)
    if record is None:
        record = {"subject": subject, "attended": 0, "total": 0}
        records.append(record)
    record["total"] += 1
    if present:
        record["attended"] += 1
    return record


def overall_percentage(records):
    attended = sum(r["attended"] for r in records)
    total = sum(r["total"] for r in records)
    return percentage(attended, total)


# ---------- screens ----------
def record_class():
    subject = subjects.choose_subject("Which subject had a class")
    if subject is None:
        return
    answer = ""
    while answer not in ("p", "a"):
        answer = input("Were you Present (p) or Absent (a)? ").strip().lower()
        if answer not in ("p", "a"):
            print("  Please type p or a.")
    records = load_attendance()
    record = mark_class(records, subject, answer == "p")
    save_attendance(records)
    pct = percentage(record["attended"], record["total"])
    print(f"  Saved. {subject}: {record['attended']}/{record['total']} = {pct:.1f}%")


def set_totals():
    subject = subjects.choose_subject("Set attendance for which subject")
    if subject is None:
        return
    total = utils.get_int("Total classes held so far: ", 0)
    attended = utils.get_int("Classes you attended: ", 0, total)
    records = load_attendance()
    record = find_record(records, subject)
    if record is None:
        records.append({"subject": subject, "attended": attended, "total": total})
    else:
        record["attended"], record["total"] = attended, total
    save_attendance(records)
    print("  Attendance saved.")


def show_report():
    records = load_attendance()
    if not records:
        print("  No attendance recorded yet.")
        return
    utils.header("ATTENDANCE REPORT (required: %d%%)" % TARGET)
    print(f"{'Subject':<22}{'Att/Total':<11}{'%':>7}  {'Status':<11}Advice")
    utils.line()
    for record in records:
        pct = percentage(record["attended"], record["total"])
        state = status(pct)
        if state == "LOW":
            advice = f"Attend next {classes_needed(record['attended'], record['total'])} class(es)"
        else:
            advice = f"Can skip {classes_can_skip(record['attended'], record['total'])} class(es)"
        att_total = f"{record['attended']}/{record['total']}"
        print(f"{record['subject']:<22}{att_total:<11}{pct:>6.1f}%  {state:<11}{advice}")
    utils.line()
    print(f"Overall attendance: {overall_percentage(records):.1f}%")


def menu():
    while True:
        choice = utils.show_menu("ATTENDANCE", [
            "Record today's class (present/absent)",
            "Set total / attended classes directly",
            "View attendance report",
        ])
        if choice == 0:
            return
        if choice == 1:
            record_class()
        elif choice == 2:
            set_totals()
        elif choice == 3:
            show_report()
        utils.pause()
