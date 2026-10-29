"""
subjects.py - The list of subjects shared by attendance, marks and
assignments.
"""
from src import storage, utils


def load_subjects():
    """Return the list of subject names."""
    return [row["name"] for row in storage.load("subjects")]


def save_subjects(names):
    storage.save("subjects", [{"name": name} for name in names])


def find_subject(names, name):
    """Case-insensitive search. Returns the stored spelling or None."""
    for existing in names:
        if existing.lower() == name.strip().lower():
            return existing
    return None


def add_subject(name):
    """Add a subject. Returns (success, message)."""
    name = name.strip()
    if not name:
        return False, "Subject name cannot be empty."
    names = load_subjects()
    if find_subject(names, name):
        return False, f"'{name}' already exists."
    names.append(name)
    save_subjects(names)
    return True, f"Subject '{name}' added."


def delete_subject(name):
    """Delete a subject and every record that belongs to it."""
    names = load_subjects()
    stored = find_subject(names, name)
    if stored is None:
        return False, "Subject not found."
    save_subjects([n for n in names if n != stored])
    for key in ("attendance", "marks", "assignments"):
        rows = storage.load(key)
        storage.save(key, [r for r in rows if r["subject"] != stored])
    return True, f"Subject '{stored}' and its records were deleted."


def choose_subject(prompt="Choose a subject"):
    """Show the subjects as a numbered list and return the chosen name."""
    names = load_subjects()
    if not names:
        print("  No subjects yet. Please add subjects first (Main menu > 1).")
        return None
    print(f"\n{prompt}:")
    for number, name in enumerate(names, start=1):
        print(f"  {number}. {name}")
    print("  0. Cancel")
    choice = utils.get_int("Enter number: ", 0, len(names))
    if choice == 0:
        return None
    return names[choice - 1]


def list_subjects():
    names = load_subjects()
    if not names:
        print("  No subjects added yet.")
        return
    print("\nYour subjects:")
    for number, name in enumerate(names, start=1):
        print(f"  {number}. {name}")


def menu():
    while True:
        choice = utils.show_menu("SUBJECTS", ["Add a subject", "View subjects", "Delete a subject"])
        if choice == 0:
            return
        if choice == 1:
            _, message = add_subject(utils.get_text("Subject name: "))
            print("  " + message)
        elif choice == 2:
            list_subjects()
        elif choice == 3:
            name = choose_subject("Which subject should be deleted")
            if name and utils.confirm(f"Delete '{name}' and ALL its records?"):
                print("  " + delete_subject(name)[1])
        utils.pause()
