"""
Automated tests. Run from the project folder with:
    python -m unittest discover -s tests -v
Tests use a temporary folder, so your real data/ files are never touched.
"""
import os
import sys
import tempfile
import unittest
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import (assignments, attendance, expenses, marks, priority,
                 sample_data, storage, subjects, utils)


class TempDataCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._old = storage.DATA_DIR
        storage.DATA_DIR = self._tmp.name

    def tearDown(self):
        storage.DATA_DIR = self._old
        self._tmp.cleanup()


class TestAttendance(unittest.TestCase):
    def test_percentage(self):
        self.assertEqual(attendance.percentage(18, 20), 90)
        self.assertEqual(attendance.percentage(0, 0), 0)

    def test_classes_needed(self):
        self.assertEqual(attendance.classes_needed(15, 24), 12)  # 27/36 = 75%
        a, t = 15, 24
        x = attendance.classes_needed(a, t)
        self.assertGreaterEqual((a + x) / (t + x), 0.75)
        self.assertLess((a + x - 1) / (t + x - 1), 0.75)
        self.assertEqual(attendance.classes_needed(20, 20), 0)

    def test_classes_can_skip(self):
        a, t = 25, 26
        m = attendance.classes_can_skip(a, t)
        self.assertGreaterEqual(a / (t + m), 0.75)
        self.assertLess(a / (t + m + 1), 0.75)
        self.assertEqual(attendance.classes_can_skip(10, 20), 0)

    def test_status(self):
        self.assertEqual(attendance.status(60), "LOW")
        self.assertEqual(attendance.status(77), "BORDERLINE")
        self.assertEqual(attendance.status(90), "OK")

    def test_mark_class(self):
        records = []
        attendance.mark_class(records, "Physics", True)
        attendance.mark_class(records, "Physics", False)
        self.assertEqual(records, [{"subject": "Physics", "attended": 1, "total": 2}])


class TestMarks(unittest.TestCase):
    def test_grade(self):
        self.assertEqual([marks.grade(p) for p in (90, 75, 60, 45, 10)],
                         ["A", "B", "C", "D", "F"])

    def test_averages_and_analysis(self):
        rows = [
            {"subject": "A", "exam": "q1", "scored": 5, "maximum": 10},
            {"subject": "A", "exam": "q2", "scored": 15, "maximum": 20},
            {"subject": "B", "exam": "q1", "scored": 3, "maximum": 10},
        ]
        avg = marks.subject_averages(rows)
        self.assertAlmostEqual(avg["A"], 62.5)
        self.assertAlmostEqual(avg["B"], 30)
        best, worst = marks.best_and_worst(avg)
        self.assertEqual((best[0], worst[0]), ("A", "B"))
        self.assertEqual(marks.weak_subjects(avg), ["B"])
        self.assertEqual(marks.best_and_worst({}), (None, None))


class TestAssignments(unittest.TestCase):
    def test_days_left(self):
        today = date(2026, 11, 1)
        self.assertEqual(assignments.days_left("2026-11-04", today), 3)
        self.assertEqual(assignments.days_left("2026-10-30", today), -2)
        self.assertIsNone(assignments.days_left("not a date", today))

    def test_urgency_label(self):
        self.assertIn("OVERDUE", assignments.urgency_label(-2))
        self.assertEqual(assignments.urgency_label(0), "Due TODAY")

    def test_clashes(self):
        rows = [
            {"title": "A", "subject": "x", "deadline": "2026-11-05", "status": "Pending"},
            {"title": "B", "subject": "y", "deadline": "2026-11-05", "status": "Pending"},
            {"title": "C", "subject": "y", "deadline": "2026-11-06", "status": "Pending"},
            {"title": "D", "subject": "y", "deadline": "2026-11-06", "status": "Done"},
        ]
        self.assertEqual(assignments.find_deadline_clashes(rows),
                         {"2026-11-05": ["A", "B"]})


class TestExpenses(unittest.TestCase):
    ROWS = [
        {"date": "2026-10-01", "category": "Food", "amount": 100.0, "note": ""},
        {"date": "2026-10-02", "category": "Food", "amount": 50.0, "note": ""},
        {"date": "2026-10-03", "category": "Books", "amount": 200.0, "note": ""},
        {"date": "2026-09-30", "category": "Travel", "amount": 999.0, "note": ""},
    ]

    def test_filter_and_totals(self):
        october = expenses.filter_month(self.ROWS, "2026-10")
        self.assertEqual(len(october), 3)
        totals = expenses.category_totals(october)
        self.assertEqual(totals, {"Food": 150.0, "Books": 200.0})
        self.assertEqual(expenses.top_category(totals), ("Books", 200.0))
        self.assertIsNone(expenses.top_category({}))

    def test_budget_status(self):
        self.assertEqual(expenses.budget_status(10, 0)[0], "NONE")
        self.assertEqual(expenses.budget_status(500, 1000)[0], "OK")
        self.assertEqual(expenses.budget_status(850, 1000)[0], "WARNING")
        self.assertEqual(expenses.budget_status(1200, 1000)[0], "OVER")


class TestPriority(unittest.TestCase):
    def test_rules(self):
        self.assertEqual(priority.attendance_score(80), 0)
        self.assertEqual(priority.attendance_score(50), 100)
        self.assertEqual(priority.marks_score(70), 0)
        self.assertEqual(priority.marks_score(20), 100)
        self.assertEqual(priority.urgency_points(-1), 100)
        self.assertEqual(priority.urgency_points(2), 60)
        self.assertEqual(priority.urgency_points(30), 10)
        self.assertEqual(priority.assignment_score([5, 20]), 40)   # 30 + 10
        self.assertEqual(priority.assignment_score([-1, -2]), 100)  # capped at 100
        self.assertEqual([priority.priority_level(s) for s in (70, 40, 5)],
                         ["HIGH", "MEDIUM", "LOW"])

    def test_ranking(self):
        today = date(2026, 11, 1)
        att = [{"subject": "Weak", "attended": 10, "total": 20},
               {"subject": "Strong", "attended": 19, "total": 20}]
        mk = [{"subject": "Weak", "exam": "q", "scored": 3, "maximum": 10},
              {"subject": "Strong", "exam": "q", "scored": 9, "maximum": 10}]
        asg = [{"title": "T", "subject": "Weak", "deadline": "2026-10-30", "status": "Pending"}]
        ranking = priority.build_priority(["Strong", "Weak", "Empty"], att, mk, asg, today)
        self.assertEqual(ranking[0]["subject"], "Weak")
        self.assertEqual(ranking[0]["level"], "HIGH")
        self.assertEqual(ranking[-1]["level"], "LOW")

    def test_rank_tasks_order(self):
        today = date(2026, 11, 1)
        rows = [{"title": "late", "subject": "x", "deadline": "2026-11-10", "status": "Pending"},
                {"title": "soon", "subject": "x", "deadline": "2026-11-02", "status": "Pending"},
                {"title": "done", "subject": "x", "deadline": "2026-10-01", "status": "Done"}]
        ordered = [row["title"] for _, row in priority.rank_tasks(rows, today)]
        self.assertEqual(ordered, ["soon", "late"])


class TestStorageAndSubjects(TempDataCase):
    def test_round_trip(self):
        rows = [{"subject": "A, B", "attended": "3", "total": "4"}]
        storage.save("attendance", rows)
        self.assertEqual(storage.load("attendance"), rows)

    def test_missing_file_gives_empty_list(self):
        self.assertEqual(storage.load("marks"), [])

    def test_settings(self):
        self.assertEqual(storage.get_setting("x", "d"), "d")
        storage.set_setting("x", 5)
        storage.set_setting("x", 7)
        self.assertEqual(storage.get_setting("x"), "7")

    def test_subject_add_duplicate_delete(self):
        self.assertTrue(subjects.add_subject("Physics")[0])
        self.assertFalse(subjects.add_subject("physics")[0])
        self.assertFalse(subjects.add_subject("   ")[0])
        storage.save("attendance", [{"subject": "Physics", "attended": "1", "total": "2"}])
        self.assertTrue(subjects.delete_subject("PHYSICS")[0])
        self.assertEqual(subjects.load_subjects(), [])
        self.assertEqual(storage.load("attendance"), [])
        self.assertFalse(subjects.delete_subject("Nothing")[0])

    def test_damaged_rows_are_ignored(self):
        storage.save("attendance", [{"subject": "A", "attended": "x", "total": "4"}])
        self.assertEqual(attendance.load_attendance(), [])

    def test_sample_data_loads(self):
        sample_data.load_sample_data(date(2026, 11, 15))
        self.assertEqual(len(subjects.load_subjects()), 4)
        self.assertEqual(expenses.load_budget(), 1000.0)
        self.assertEqual(len(assignments.load_assignments()), 5)


class TestUtils(unittest.TestCase):
    def test_parse_date(self):
        self.assertEqual(utils.parse_date("2026-11-30"), date(2026, 11, 30))
        self.assertIsNone(utils.parse_date("30-11-2026"))
        self.assertIsNone(utils.parse_date("2026-13-01"))


if __name__ == "__main__":
    unittest.main()
