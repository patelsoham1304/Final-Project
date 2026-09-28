import sqlite3
import pytest
from database.db import (
    create_student, get_student, update_student,
    save_student_skills, get_student_skills,
    save_progress, get_progress, get_connection
)
from database.seed import seed_db

def test_student_crud():
    sid = create_student("Alice", "alice@example.com")
    assert sid is not None
    
    st = get_student(sid)
    assert st['name'] == "Alice"
    
    update_student(sid, "Alice Updated", "alice2@example.com")
    st = get_student(sid)
    assert st['name'] == "Alice Updated"

def test_foreign_key_constraint():
    with pytest.raises(sqlite3.IntegrityError):
        # Attempt to save skills for a non-existent student
        save_student_skills(999, [1, 2])

def test_idempotent_seed():
    seed_db()
    # Running again should not error due to INSERT OR IGNORE
    seed_db()
    
    from database.db import get_careers
    assert len(get_careers()) == 1

def test_progress():
    seed_db()
    sid = create_student("Bob", "bob@example.com")
    
    save_progress(sid, 1, "completed")
    prog = get_progress(sid, 1)
    assert prog['status'] == "completed"
    
    save_progress(sid, 1, "in_progress")
    prog = get_progress(sid, 1)
    assert prog['status'] == "in_progress"
