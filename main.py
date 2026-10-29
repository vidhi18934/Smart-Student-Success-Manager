"""
Smart Student Success Manager
Course: Computational Thinking and Programming (2026CSAE100)

A menu-driven Python program that keeps a student's attendance, marks,
assignments and expenses in one place, and analyses them to say which
subject needs attention first.

Run with:   python main.py
"""
from src import (assignments, attendance, expenses, marks, priority,
                 sample_data, subjects, utils)


def load_demo():
    print("This will REPLACE all current data with demo data.")
    if utils.confirm("Continue?"):
        sample_data.load_sample_data()
        print("  Demo data loaded. Try the Priority Dashboard (option 6).")


def main():
    print("\nWelcome to the Smart Student Success Manager!")
    while True:
        choice = utils.show_menu("MAIN MENU", [
            "Subjects",
            "Attendance",
            "Marks",
            "Assignments & Deadlines",
            "Expenses",
            "Priority Dashboard (what should I focus on?)",
            "Load demo data",
        ], back_label="Exit")
        if choice == 0:
            print("\nGoodbye! All your data is saved in the data/ folder.")
            return
        if choice == 1:
            subjects.menu()
        elif choice == 2:
            attendance.menu()
        elif choice == 3:
            marks.menu()
        elif choice == 4:
            assignments.menu()
        elif choice == 5:
            expenses.menu()
        elif choice == 6:
            priority.show_dashboard()
            utils.pause()
        elif choice == 7:
            load_demo()
            utils.pause()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nProgram closed. Your data is saved.")
