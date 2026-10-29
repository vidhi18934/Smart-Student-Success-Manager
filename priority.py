"""
priority.py - The "brain" of the project: the Priority Dashboard.

For every subject a priority SCORE from 0 to 100 is calculated from three
rules, then the subjects are ranked. A higher score = needs attention sooner.

    attendance part : grows as attendance falls below 75%
    marks part      : grows as the subject average falls below 60%
    assignment part : grows with the number and urgency of pending work

    score = 0.4 * attendance part + 0.3 * marks part + 0.3 * assignment part
"""
from datetime import date

from src import assignments, attendance, expenses, marks, subjects, utils

W_ATTENDANCE = 0.4
W_MARKS = 0.3
W_ASSIGNMENTS = 0.3
MARKS_COMFORT = 60     # averages below this start adding points
HIGH_FROM = 60         # score >= 60 -> HIGH
MEDIUM_FROM = 30       # score >= 30 -> MEDIUM


# ---------- scoring rules ----------
def attendance_score(pct):
    """0 at or above 75%; 4 points for every % below, capped at 100."""
    return min(100.0, max(0.0, attendance.TARGET - pct) * 4)


def marks_score(avg):
    """0 at or above 60%; 2.5 points for every % below, capped at 100."""
    return min(100.0, max(0.0, MARKS_COMFORT - avg) * 2.5)


def urgency_points(days):
    """How urgent one pending assignment is, depending on days left."""
    if days < 0:
        return 100
    if days == 0:
        return 90
    if days == 1:
        return 80
    if days <= 3:
        return 60
    if days <= 7:
        return 30
    return 10


def assignment_score(days_list):
    """Add the urgency of every pending assignment, capped at 100."""
    return min(100.0, float(sum(urgency_points(d) for d in days_list)))


def priority_level(score):
    if score >= HIGH_FROM:
        return "HIGH"
    if score >= MEDIUM_FROM:
        return "MEDIUM"
    return "LOW"


# ---------- ranking ----------
def build_priority(subject_names, attendance_records, marks_rows, assignment_rows, today=None):
    """
    Return a list of dictionaries (one per subject), highest score first:
    {"subject", "score", "level", "reasons": [text, ...]}
    """
    today = today or date.today()
    averages = marks.subject_averages(marks_rows)
    result = []

    for name in subject_names:
        reasons = []
        att_part = marks_part = assign_part = 0.0

        record = attendance.find_record(attendance_records, name)
        if record and record["total"] > 0:
            pct = attendance.percentage(record["attended"], record["total"])
            att_part = attendance_score(pct)
            if pct < attendance.TARGET:
                need = attendance.classes_needed(record["attended"], record["total"])
                reasons.append(f"Attendance is {pct:.1f}% (below {attendance.TARGET}%). "
                               f"Attend the next {need} class(es).")

        if name in averages:
            marks_part = marks_score(averages[name])
            if averages[name] < MARKS_COMFORT:
                reasons.append(f"Average marks are {averages[name]:.1f}%. Revise this subject.")

        pending_days = [
            assignments.days_left(row["deadline"], today)
            for row in assignment_rows
            if row["subject"] == name and row["status"] == assignments.PENDING
        ]
        if pending_days:
            assign_part = assignment_score(pending_days)
            overdue = sum(1 for d in pending_days if d < 0)
            soonest = min(pending_days)
            text = f"{len(pending_days)} pending assignment(s)"
            if overdue:
                text += f", {overdue} overdue"
            text += f". Nearest deadline: {assignments.urgency_label(soonest)}."
            reasons.append(text)

        score = W_ATTENDANCE * att_part + W_MARKS * marks_part + W_ASSIGNMENTS * assign_part
        if not reasons:
            reasons.append("Nothing urgent. Keep going!")
        result.append({"subject": name, "score": score,
                       "level": priority_level(score), "reasons": reasons})

    result.sort(key=lambda item: item["score"], reverse=True)
    return result


def rank_tasks(assignment_rows, today=None):
    """Pending assignments ordered by deadline: [(days_left, row), ...]."""
    today = today or date.today()
    pending = [(assignments.days_left(row["deadline"], today), row)
               for row in assignments.pending_only(assignment_rows)]
    pending.sort(key=lambda item: item[0])
    return pending


# ---------- dashboard screen ----------
def show_dashboard():
    today = date.today()
    names = subjects.load_subjects()
    if not names:
        print("  Add subjects and some data first, then the dashboard can help you.")
        return

    att_records = attendance.load_attendance()
    marks_rows = marks.load_marks()
    assignment_rows = assignments.load_assignments()
    expense_rows = expenses.load_expenses()

    utils.header(f"SMART STUDENT SUCCESS DASHBOARD  ({today})")

    # --- overall picture ---
    print("OVERALL STATUS")
    if att_records:
        print(f"  Overall attendance : {attendance.overall_percentage(att_records):.1f}%")
    else:
        print("  Overall attendance : no data")
    averages = marks.subject_averages(marks_rows)
    if averages:
        print(f"  Average marks      : {marks.overall_average(averages):.1f}%")
    else:
        print("  Average marks      : no data")
    pending = assignments.pending_only(assignment_rows)
    overdue = [r for r in pending if assignments.days_left(r["deadline"], today) < 0]
    print(f"  Pending assignments: {len(pending)}  (overdue: {len(overdue)})")
    month_rows = expenses.filter_month(expense_rows, expenses.month_of(today.isoformat()))
    spent = expenses.total_of(month_rows)
    print(f"  Spent this month   : Rs. {spent:.2f}")
    print("  Budget             : " + expenses.budget_status(spent, expenses.load_budget())[1])

    # --- ranked subjects ---
    ranking = build_priority(names, att_records, marks_rows, assignment_rows, today)
    print("\nSUBJECT PRIORITY (highest first)")
    utils.line()
    for position, item in enumerate(ranking, start=1):
        print(f"{position}. {item['subject']:<20} score {item['score']:5.1f}  [{item['level']}]")
        for reason in item["reasons"]:
            print(f"     - {reason}")

    # --- next tasks ---
    tasks = rank_tasks(assignment_rows, today)[:5]
    print("\nNEXT DEADLINES")
    utils.line()
    if not tasks:
        print("  No pending assignments.")
    for days, row in tasks:
        print(f"  {row['deadline']}  {row['title']} ({row['subject']}) - {assignments.urgency_label(days)}")

    # --- final advice ---
    print()
    utils.line()
    top = ranking[0]
    if top["level"] == "LOW":
        print("RECOMMENDATION: You are in good shape in every subject. Keep revising regularly.")
    else:
        print(f"RECOMMENDATION: Focus on {top['subject']} first ({top['level']} priority).")
    clashes = assignments.find_deadline_clashes(assignment_rows)
    for day, titles in sorted(clashes.items()):
        print(f"WARNING: deadline clash on {day}: {', '.join(titles)}. Start one of them early.")
