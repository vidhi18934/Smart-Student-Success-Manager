"""
expenses.py - Personal expense tracking with a monthly budget.

Each record is a dictionary:
    {"date": "2026-10-20", "category": "Food", "amount": 120.0, "note": "Canteen"}

Features: category totals, highest-spending category and rule-based budget
alerts (warning at 80% of the budget, alert when it is crossed).
"""
from datetime import date

from src import storage, utils

CATEGORIES = ["Food", "Travel", "Books", "Stationery", "Entertainment", "Hostel/Rent", "Other"]
WARNING_FRACTION = 0.8   # warn when 80% of the budget is used


# ---------- data handling ----------
def load_expenses():
    rows = []
    for row in storage.load("expenses"):
        try:
            if utils.parse_date(row["date"]) is None:
                continue
            rows.append({
                "date": row["date"],
                "category": row["category"],
                "amount": float(row["amount"]),
                "note": row["note"],
            })
        except ValueError:
            continue
    return rows


def save_expenses(rows):
    storage.save("expenses", rows)


def load_budget():
    """Monthly budget in Rs. 0 means 'not set'."""
    try:
        return float(storage.get_setting("monthly_budget", "0"))
    except ValueError:
        return 0.0


def save_budget(amount):
    storage.set_setting("monthly_budget", amount)


# ---------- calculations ----------
def month_of(date_text):
    """'2026-10-20' -> '2026-10'."""
    return date_text[:7]


def filter_month(rows, month):
    return [row for row in rows if month_of(row["date"]) == month]


def total_of(rows):
    return sum(row["amount"] for row in rows)


def category_totals(rows):
    """Return {category: total amount}."""
    totals = {}
    for row in rows:
        totals[row["category"]] = totals.get(row["category"], 0.0) + row["amount"]
    return totals


def top_category(totals):
    """Return (category, amount) with the highest spending, or None."""
    if not totals:
        return None
    return max(totals.items(), key=lambda item: item[1])


def budget_status(spent, budget):
    """Return (level, message). level is 'NONE', 'OK', 'WARNING' or 'OVER'."""
    if budget <= 0:
        return "NONE", "No monthly budget set."
    if spent > budget:
        return "OVER", f"ALERT: over budget by Rs. {spent - budget:.2f}!"
    used = spent / budget
    if used >= WARNING_FRACTION:
        return "WARNING", (f"Warning: {used * 100:.0f}% of the budget is used. "
                           f"Only Rs. {budget - spent:.2f} left.")
    return "OK", f"On track. Rs. {budget - spent:.2f} left in the budget."


# ---------- screens ----------
def add_expense():
    today = date.today()
    expense_date = utils.get_date(f"Date (YYYY-MM-DD, Enter for today {today}): ", default=today)
    print("Categories:")
    for number, name in enumerate(CATEGORIES, start=1):
        print(f"  {number}. {name}")
    category = CATEGORIES[utils.get_int("Choose category number: ", 1, len(CATEGORIES)) - 1]
    amount = utils.get_float("Amount (Rs.): ", 0.01)
    note = utils.get_text("Note (optional): ", allow_empty=True)
    rows = load_expenses()
    rows.append({"date": expense_date.isoformat(), "category": category,
                 "amount": amount, "note": note})
    save_expenses(rows)
    print("  Expense saved.")
    month_rows = filter_month(rows, month_of(expense_date.isoformat()))
    level, message = budget_status(total_of(month_rows), load_budget())
    if level in ("WARNING", "OVER"):
        print("  " + message)


def view_expenses():
    rows = sorted(load_expenses(), key=lambda row: row["date"])
    if not rows:
        print("  No expenses recorded yet.")
        return rows
    utils.header("ALL EXPENSES")
    print(f"{'#':<4}{'Date':<12}{'Category':<15}{'Amount':>10}  Note")
    utils.line()
    for number, row in enumerate(rows, start=1):
        print(f"{number:<4}{row['date']:<12}{row['category']:<15}{row['amount']:>10.2f}  {row['note']}")
    utils.line()
    print(f"Total: Rs. {total_of(rows):.2f}")
    return rows


def monthly_summary():
    rows = load_expenses()
    default_month = month_of(date.today().isoformat())
    month = default_month
    raw = input(f"Month (YYYY-MM, Enter for {default_month}): ").strip()
    if raw:
        if utils.parse_date(raw + "-01") is None:
            print("  Invalid month. Use the format YYYY-MM.")
            return
        month = raw
    month_rows = filter_month(rows, month)
    if not month_rows:
        print(f"  No expenses recorded for {month}.")
        return
    totals = category_totals(month_rows)
    spent = total_of(month_rows)
    utils.header(f"EXPENSE SUMMARY - {month}")
    for name, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True):
        share = amount / spent * 100
        print(f"  {name:<15}Rs. {amount:>9.2f}  ({share:.0f}%)")
    utils.line()
    print(f"  Total spent : Rs. {spent:.2f}  ({len(month_rows)} expenses)")
    best = top_category(totals)
    print(f"  Highest category: {best[0]} (Rs. {best[1]:.2f})")
    budget = load_budget()
    if budget > 0:
        print(f"  Monthly budget : Rs. {budget:.2f}")
    print("  " + budget_status(spent, budget)[1])


def set_budget():
    current = load_budget()
    if current > 0:
        print(f"  Current monthly budget: Rs. {current:.2f}")
    amount = utils.get_float("New monthly budget (Rs.): ", 1)
    save_budget(amount)
    print("  Budget saved.")


def delete_expense():
    rows = load_expenses()
    ordered = sorted(rows, key=lambda row: row["date"])
    if not ordered:
        print("  No expenses to delete.")
        return
    view_expenses()
    number = utils.get_int("Number of the expense to delete (0 to cancel): ", 0, len(ordered))
    if number == 0:
        return
    chosen = ordered[number - 1]
    rows = [row for row in rows if row is not chosen]
    save_expenses(rows)
    print("  Deleted.")


def menu():
    while True:
        choice = utils.show_menu("EXPENSES", [
            "Add an expense",
            "View all expenses",
            "Monthly summary & budget check",
            "Set monthly budget",
            "Delete an expense",
        ])
        if choice == 0:
            return
        if choice == 1:
            add_expense()
        elif choice == 2:
            view_expenses()
        elif choice == 3:
            monthly_summary()
        elif choice == 4:
            set_budget()
        elif choice == 5:
            delete_expense()
        utils.pause()
