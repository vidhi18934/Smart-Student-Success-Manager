"""
marks.py - Marks tracking and analysis.

Each record is a dictionary:
    {"subject": "Calculus", "exam": "Quiz 1", "scored": 8.0, "maximum": 10.0}

Feature: converts every exam to a percentage, averages per subject, assigns
a grade, and finds the strongest and weakest subjects.
"""
from src import storage, subjects, utils

WEAK_BELOW = 50   # subject average below this % is called "weak"


# ---------- data handling ----------
def load_marks():
    rows = []
    for row in storage.load("marks"):
        try:
            rows.append({
                "subject": row["subject"],
                "exam": row["exam"],
                "scored": float(row["scored"]),
                "maximum": float(row["maximum"]),
            })
        except ValueError:
            continue
    return rows


def save_marks(rows):
    storage.save("marks", rows)


# ---------- calculations ----------
def percent(scored, maximum):
    if maximum <= 0:
        return 0.0
    return scored / maximum * 100


def grade(pct):
    """Convert a percentage into a letter grade."""
    if pct >= 85:
        return "A"
    if pct >= 70:
        return "B"
    if pct >= 55:
        return "C"
    if pct >= 40:
        return "D"
    return "F"


def subject_averages(rows):
    """Return {subject: average percentage of all its exams}."""
    collected = {}
    for row in rows:
        collected.setdefault(row["subject"], []).append(
            percent(row["scored"], row["maximum"])
        )
    return {name: sum(values) / len(values) for name, values in collected.items()}


def best_and_worst(averages):
    """Return ((best_subject, avg), (worst_subject, avg)) or (None, None)."""
    if not averages:
        return None, None
    best = max(averages.items(), key=lambda item: item[1])
    worst = min(averages.items(), key=lambda item: item[1])
    return best, worst


def weak_subjects(averages):
    return [name for name, avg in averages.items() if avg < WEAK_BELOW]


def overall_average(averages):
    if not averages:
        return 0.0
    return sum(averages.values()) / len(averages)


# ---------- screens ----------
def add_marks():
    subject = subjects.choose_subject("Add marks for which subject")
    if subject is None:
        return
    exam = utils.get_text("Exam / test name (e.g. Quiz 1): ")
    maximum = utils.get_float("Maximum marks: ", 0.01)
    scored = utils.get_float("Marks you scored: ", 0, maximum)
    rows = load_marks()
    rows.append({"subject": subject, "exam": exam, "scored": scored, "maximum": maximum})
    save_marks(rows)
    pct = percent(scored, maximum)
    print(f"  Saved. {pct:.1f}% (grade {grade(pct)})")


def view_marks():
    rows = load_marks()
    if not rows:
        print("  No marks recorded yet.")
        return
    utils.header("ALL MARKS")
    print(f"{'#':<4}{'Subject':<20}{'Exam':<18}{'Score':<12}{'%':>7}  Grade")
    utils.line()
    for number, row in enumerate(rows, start=1):
        pct = percent(row["scored"], row["maximum"])
        score = f"{row['scored']:g}/{row['maximum']:g}"
        print(f"{number:<4}{row['subject']:<20}{row['exam']:<18}{score:<12}{pct:>6.1f}%  {grade(pct)}")


def show_analysis():
    rows = load_marks()
    averages = subject_averages(rows)
    if not averages:
        print("  No marks recorded yet.")
        return
    utils.header("MARKS ANALYSIS")
    print(f"{'Subject':<24}{'Average %':>10}  Grade")
    utils.line()
    for name, avg in sorted(averages.items(), key=lambda item: item[1], reverse=True):
        print(f"{name:<24}{avg:>9.1f}%  {grade(avg)}")
    utils.line()
    best, worst = best_and_worst(averages)
    print(f"Overall average : {overall_average(averages):.1f}%")
    print(f"Strongest subject: {best[0]} ({best[1]:.1f}%)")
    print(f"Weakest subject  : {worst[0]} ({worst[1]:.1f}%)")
    weak = weak_subjects(averages)
    if weak:
        print(f"Needs improvement (below {WEAK_BELOW}%): {', '.join(weak)}")
    else:
        print(f"No subject is below {WEAK_BELOW}%. Keep it up!")


def delete_marks():
    rows = load_marks()
    if not rows:
        print("  No marks to delete.")
        return
    view_marks()
    number = utils.get_int("Number of the entry to delete (0 to cancel): ", 0, len(rows))
    if number == 0:
        return
    removed = rows.pop(number - 1)
    save_marks(rows)
    print(f"  Deleted {removed['subject']} - {removed['exam']}.")


def menu():
    while True:
        choice = utils.show_menu("MARKS", [
            "Add marks",
            "View all marks",
            "Subject-wise analysis",
            "Delete an entry",
        ])
        if choice == 0:
            return
        if choice == 1:
            add_marks()
        elif choice == 2:
            view_marks()
        elif choice == 3:
            show_analysis()
        elif choice == 4:
            delete_marks()
        utils.pause()
