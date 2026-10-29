"""
utils.py - Small input/printing helpers used by every module.

Every function that asks the user for something keeps asking until the
answer is valid, so the program never crashes on wrong input.
"""
import math
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d"


def line(char="-", width=64):
    """Print a separator line."""
    print(char * width)


def header(title):
    """Print a boxed title."""
    print()
    line("=")
    print(f"  {title}")
    line("=")


def pause():
    input("\nPress Enter to continue...")


def get_text(prompt, allow_empty=False):
    """Ask for text. Repeats until something is typed (unless allow_empty)."""
    while True:
        value = input(prompt).strip()
        if value or allow_empty:
            return value
        print("  Input cannot be empty. Please try again.")


def get_int(prompt, min_value=None, max_value=None):
    """Ask for a whole number inside an optional range."""
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("  Please enter a whole number (for example 5).")
            continue
        if min_value is not None and value < min_value:
            print(f"  The number must be at least {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"  The number must be at most {max_value}.")
            continue
        return value


def get_float(prompt, min_value=None, max_value=None):
    """Ask for a decimal number inside an optional range."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
        except ValueError:
            print("  Please enter a number (for example 7.5).")
            continue
        if not math.isfinite(value):
            print("  That is not a valid number.")
            continue
        if min_value is not None and value < min_value:
            print(f"  The number must be at least {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"  The number must be at most {max_value}.")
            continue
        return value


def parse_date(text):
    """Turn 'YYYY-MM-DD' into a date object. Returns None if invalid."""
    try:
        return datetime.strptime(text.strip(), DATE_FORMAT).date()
    except (ValueError, AttributeError):
        return None


def get_date(prompt, default=None):
    """
    Ask for a date in YYYY-MM-DD format.
    If `default` (a date) is given, pressing Enter selects it.
    """
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        parsed = parse_date(raw)
        if parsed is not None:
            return parsed
        print("  Invalid date. Use the format YYYY-MM-DD (for example 2026-11-30).")


def confirm(prompt):
    """Ask a yes/no question. Returns True for yes."""
    while True:
        answer = input(f"{prompt} (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("  Please type y or n.")


def show_menu(title, options, back_label="Back"):
    """
    Print a numbered menu and return the chosen number.
    0 always means 'back / exit'.
    """
    header(title)
    for number, label in enumerate(options, start=1):
        print(f"  {number}. {label}")
    print(f"  0. {back_label}")
    line()
    return get_int("Enter your choice: ", 0, len(options))
