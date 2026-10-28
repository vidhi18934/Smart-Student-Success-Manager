# Smart Student Success Manager

A menu-driven Python program for the course **Computational Thinking and Programming (2026CSAE100)**.
It keeps a student's **attendance, marks, assignments and expenses** in one place and analyses them to
answer one question: *"What should I focus on first?"*

## Features
| Module | What it does | Computational feature |
|---|---|---|
| Subjects | Add / view / delete subjects | - |
| Attendance | Record classes, set totals, report | % calculation, LOW alert (< 75%), classes needed / can skip |
| Marks | Add / view / delete marks | Percentages, grades, subject averages, strongest / weakest subject |
| Assignments | Add, view, mark done, delete | Days left, overdue detection, deadline clash detection |
| Expenses | Add, view, monthly summary, budget | Category totals, top category, budget warnings |
| Priority Dashboard | Combines everything | Rule-based scoring and ranking + recommendations |

Priority score (0-100) = 0.4 x attendance part + 0.3 x marks part + 0.3 x assignment part
(HIGH >= 60, MEDIUM >= 30, otherwise LOW). The rules are in `src/priority.py`.

## How to run
Needs Python 3.8+ and nothing else (only the standard library: `csv`, `datetime`, `os`, `math`).

    python main.py

Choose **7. Load demo data** in the main menu to fill the program with sample data, then open
**6. Priority Dashboard**.

## Run the tests
    python -m unittest discover -s tests -v

## Folder structure
    main.py            main menu
    src/
      utils.py         safe input helpers (numbers, dates, yes/no, menus)
      storage.py       reads/writes the CSV files
      subjects.py      subject list
      attendance.py    attendance module
      marks.py         marks module
      assignments.py   assignments module
      expenses.py      expenses module
      priority.py      priority scoring + dashboard
      sample_data.py   demo data
    data/              CSV files (created automatically)
    tests/test_all.py  unit tests

## Python concepts used
Variables, conditionals, loops, functions, lists, dictionaries, tuples, f-strings,
exception handling (try/except), file handling (CSV), modules/imports, sorting with key=lambda.

## Team
Team
|Member |	Module|
|Vidhi |	`priority.py`, `main.py`, `storage.py`|
|Mokshika |	`attendance.py` (+ `subjects.py`)|
|Anshika |	`marks.py`|
|Palak |	`assignments.py`|
|Riya |	`expenses.py`|


