"""
sample_data.py - Fills the data files with demo data (for testing, screenshots
and the viva demo). Dates are created relative to today.
"""
from datetime import date, timedelta

from src import assignments, expenses, storage


def load_sample_data(today=None):
    today = today or date.today()
    storage.save("subjects", [{"name": n} for n in
                              ["Calculus", "Digital Design", "Python Programming", "Physics"]])
    storage.save("attendance", [
        {"subject": "Calculus", "attended": 15, "total": 24},         # low
        {"subject": "Digital Design", "attended": 22, "total": 26},   # ok
        {"subject": "Python Programming", "attended": 20, "total": 27},  # borderline/low
        {"subject": "Physics", "attended": 25, "total": 26},          # ok
    ])
    storage.save("marks", [
        {"subject": "Calculus", "exam": "Quiz 1", "scored": 4, "maximum": 10},
        {"subject": "Calculus", "exam": "Quiz 2", "scored": 12, "maximum": 25},
        {"subject": "Digital Design", "exam": "Quiz 1", "scored": 8, "maximum": 10},
        {"subject": "Python Programming", "exam": "Lab 1", "scored": 17, "maximum": 20},
        {"subject": "Physics", "exam": "Quiz 1", "scored": 6, "maximum": 10},
    ])

    def day(offset):
        return (today + timedelta(days=offset)).isoformat()

    storage.save("assignments", [
        {"title": "Limits worksheet", "subject": "Calculus", "deadline": day(-1), "status": assignments.PENDING},
        {"title": "K-map practice", "subject": "Digital Design", "deadline": day(3), "status": assignments.PENDING},
        {"title": "Mini project", "subject": "Python Programming", "deadline": day(3), "status": assignments.PENDING},
        {"title": "Lab report", "subject": "Physics", "deadline": day(12), "status": assignments.PENDING},
        {"title": "Number systems HW", "subject": "Digital Design", "deadline": day(-5), "status": assignments.DONE},
    ])

    spend = [(0, "Food", 120, "Canteen lunch"), (1, "Travel", 60, "Metro"),
             (2, "Books", 350, "Calculus guide"), (3, "Food", 90, "Snacks"),
             (4, "Entertainment", 200, "Movie"), (5, "Stationery", 80, "Notebooks")]
    rows = []
    for offset, category, amount, note in spend:
        # keep every demo expense inside the current month
        when = today - timedelta(days=min(offset, today.day - 1))
        rows.append({"date": when.isoformat(), "category": category,
                     "amount": amount, "note": note})
    storage.save("expenses", rows)
    expenses.save_budget(1000)
