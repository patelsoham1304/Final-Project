import sqlite3
import pytest
from database.db import (
    create_student, get_student, update_student, delete_student,
    save_student_skills, get_student_skills,
    save_progress, get_progress, get_connection, get_current_roadmap,
    get_skills_for_career, get_careers, create_roadmap, save_progress_batch,
    get_career_by_name, get_resources_for_skill
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
    with pytest.raises(ValueError, match="Student was not found"):
        save_student_skills(999, [1, 2])

def test_idempotent_seed():
    seed_db()
    career_count = len(get_careers())
    seed_db()
    assert len(get_careers()) == career_count == 6

def test_progress():
    seed_db()
    sid = create_student("Bob", "bob@example.com")
    
    save_progress(sid, 1, "completed")
    prog = get_progress(sid, 1)
    assert prog['status'] == "completed"
    
    save_progress(sid, 1, "in_progress")
    prog = get_progress(sid, 1)
    assert prog['status'] == "in_progress"

def test_required_schema_and_ordered_seed():
    seed_db()
    connection = get_connection()
    tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    assert tables == {
        "students", "careers", "skills", "career_skills",
        "roadmaps", "progress", "resources", "resume_profiles",
    }
    assert {career["name"] for career in get_careers()} == {
        "Data Analyst",
        "Frontend Developer",
        "Backend Developer",
        "Data Scientist",
        "UI/UX Designer",
        "Cybersecurity Analyst",
    }
    career = get_career_by_name("Data Analyst")
    skills = get_skills_for_career(career["id"])
    assert career["name"] == "Data Analyst"
    assert [skill["sequence_order"] for skill in skills] == list(range(1, 8))
    assert [skill["name"] for skill in skills] == [
        "SQL", "Excel", "Statistics", "Python", "Pandas",
        "Data Visualization", "Data Analysis Project",
    ]
    for career in get_careers():
        requirements = get_skills_for_career(career["id"])
        assert requirements
        assert [skill["sequence_order"] for skill in requirements] == list(
            range(1, len(requirements) + 1)
        )
        assert all(get_resources_for_skill(skill["id"]) for skill in requirements)

def test_progress_rejects_invalid_values():
    seed_db()
    student_id = create_student("Cara")
    with pytest.raises(ValueError, match="between 0 and 100"):
        save_progress(student_id, 1, "in_progress", 101)

def test_student_and_career_ids_are_validated():
    seed_db()
    career_id = get_careers()[0]["id"]
    with pytest.raises(ValueError, match="Student was not found"):
        create_roadmap(999, career_id)

def test_foreign_keys_enabled_and_student_delete_cascades():
    seed_db()
    connection = get_connection()
    assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1

    student_id = create_student("Student to delete")
    career = get_career_by_name("Data Analyst")
    create_roadmap(student_id, career["id"])
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            """
            INSERT INTO progress (student_id, skill_id, status, progress_percent)
            VALUES (?, 1, 'completed', 100)
            """,
            (999,),
        )
    connection.rollback()

    delete_student(student_id)
    assert get_student(student_id) is None
    assert connection.execute(
        "SELECT COUNT(*) FROM roadmaps WHERE student_id = ?", (student_id,)
    ).fetchone()[0] == 0

def test_migrates_existing_student_skills_and_resource_progress(monkeypatch, tmp_path):
    import database.db as database
    from database.seed import seed_db

    legacy_path = tmp_path / "legacy.db"
    monkeypatch.setattr(database, "DB_PATH", legacy_path)
    database.get_connection.clear()
    connection = database.get_connection()
    connection.executescript(
        """
        CREATE TABLE students (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE careers (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE skills (
            id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE career_skills (
            career_id INTEGER NOT NULL, skill_id INTEGER NOT NULL,
            sequence_order INTEGER NOT NULL, PRIMARY KEY (career_id, skill_id),
            FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );
        CREATE TABLE student_skills (
            student_id INTEGER NOT NULL, skill_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending', PRIMARY KEY (student_id, skill_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );
        CREATE TABLE resources (
            id INTEGER PRIMARY KEY, skill_id INTEGER NOT NULL,
            type TEXT NOT NULL, url TEXT NOT NULL, description TEXT,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );
        CREATE TABLE progress (
            id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL,
            resource_id INTEGER NOT NULL, status TEXT DEFAULT 'started',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (student_id, resource_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (resource_id) REFERENCES resources(id) ON DELETE CASCADE
        );
        INSERT INTO students (id, name, email)
            VALUES (1, 'Legacy student', 'legacy@example.test');
        INSERT INTO careers (id, name, description)
            VALUES (1, 'Data Analyst', 'Old description');
        INSERT INTO skills (id, name) VALUES (1, 'SQL');
        INSERT INTO skills (id, name) VALUES (2, 'Excel');
        INSERT INTO career_skills VALUES (1, 1, 1);
        INSERT INTO student_skills VALUES (1, 1, 'pending');
        INSERT INTO resources VALUES (1, 2, 'Book', 'https://example.test', 'Old book');
        INSERT INTO progress (id, student_id, resource_id, status)
            VALUES (1, 1, 1, 'started');
        """
    )
    connection.commit()

    seed_db()

    assert create_student("Profile without email") > 1
    assert get_progress(1, 1)["status"] == "completed"
    assert get_progress(1, 2)["status"] == "in_progress"
    tables = {
        row["name"]
        for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    assert tables == {
        "students", "careers", "skills", "career_skills",
        "roadmaps", "progress", "resources", "resume_profiles",
    }

def test_student_to_roadmap_progress_workflow():
    from modules.progress import calculate_overall_progress
    from modules.recommendation import get_next_recommended_skill
    from modules.roadmap import generate_roadmap

    seed_db()
    student_id = create_student("Workflow student")
    career = get_career_by_name("Data Analyst")
    skill_rows = get_skills_for_career(career["id"])
    skill_ids = {skill["name"]: skill["id"] for skill in skill_rows}
    save_student_skills(student_id, [skill_ids["SQL"]])
    roadmap_id = create_roadmap(student_id, career["id"])
    assert get_current_roadmap(student_id)["id"] == roadmap_id

    required = {skill["name"]: 1 for skill in skill_rows}
    current = {"SQL": 1}
    ordered_names = [skill["name"] for skill in skill_rows]
    steps = generate_roadmap(required, current, ordered_names)
    assert get_next_recommended_skill(
        [
            {"skill": step["skill"], "gap": 1}
            for step in steps
        ]
    )["skill"] == "Excel"

    save_progress(student_id, skill_ids["Excel"], "in_progress", 50)
    save_progress_batch(
        student_id,
        {skill_ids["SQL"]: 100, skill_ids["Excel"]: 100},
    )
    actual_progress = get_student_skills(student_id)
    assert len(actual_progress) == 2
    assert calculate_overall_progress(
        [
            {
                "status": "completed"
                if skill["id"] in {skill_ids["SQL"], skill_ids["Excel"]}
                else "not_started"
            }
            for skill in skill_rows
        ]
    ) == 29.0
