"""Parameterized SQLite access for the education-path application."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

import streamlit as st


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "education_path_app.db"
FALLBACK_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "education_path.db"


@st.cache_resource
def get_connection():
    """Return the cached SQLite connection used by the app and business layer."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    # Check if education_path_app.db exists, otherwise copy data from fallback if available
    if not DB_PATH.exists() and FALLBACK_DB_PATH.exists():
        try:
            import shutil
            shutil.copy2(FALLBACK_DB_PATH, DB_PATH)
        except Exception:
            pass

    connection = sqlite3.connect(str(DB_PATH), timeout=30.0, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute("PRAGMA journal_mode = WAL")
    except sqlite3.Error:
        pass
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction():
    """Commit a database unit of work, or roll it back when it fails."""
    connection = get_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise


def execute_query(query, params=(), commit=False):
    """Execute a parameterized query and return its cursor."""
    connection = get_connection()
    try:
        cursor = connection.execute(query, params)
        if commit:
            connection.commit()
        return cursor
    except sqlite3.Error:
        if commit:
            connection.rollback()
        raise


def execute_many(query, params_list, commit=False):
    """Execute a parameterized batch and return its cursor."""
    connection = get_connection()
    try:
        cursor = connection.executemany(query, params_list)
        if commit:
            connection.commit()
        return cursor
    except sqlite3.Error:
        if commit:
            connection.rollback()
        raise


def get_students():
    """Return all saved students ordered by name."""
    return execute_query("SELECT * FROM students ORDER BY name").fetchall()


def get_student(student_id):
    """Return a student by ID, or None when the ID does not exist."""
    return execute_query(
        "SELECT * FROM students WHERE id = ?", (student_id,)
    ).fetchone()


def get_student_by_email(email):
    """Return a student by email address, or None when not found."""
    if not isinstance(email, str) or not email.strip():
        return None
    return execute_query(
        "SELECT * FROM students WHERE lower(email) = lower(?)", (email.strip(),)
    ).fetchone()


def create_student(name, email=None, password_hash=None):
    """Create a student profile and return its database ID."""
    clean_name = name.strip() if isinstance(name, str) else ""
    clean_email = email.strip() if isinstance(email, str) else None
    clean_pwd_hash = password_hash.strip() if isinstance(password_hash, str) else None
    if not clean_name:
        raise ValueError("Student name cannot be empty.")
    cursor = execute_query(
        "INSERT INTO students (name, email, password_hash) VALUES (?, ?, ?)",
        (clean_name, clean_email or None, clean_pwd_hash or None),
        commit=True,
    )
    return cursor.lastrowid


def update_student(student_id, name, email=None, password_hash=None):
    """Update a saved student profile."""
    clean_name = name.strip() if isinstance(name, str) else ""
    clean_email = email.strip() if isinstance(email, str) else None
    clean_pwd_hash = password_hash.strip() if isinstance(password_hash, str) else None
    if not clean_name:
        raise ValueError("Student name cannot be empty.")
    if clean_pwd_hash:
        cursor = execute_query(
            """
            UPDATE students SET name = ?, email = ?, password_hash = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (clean_name, clean_email or None, clean_pwd_hash, student_id),
            commit=True,
        )
    else:
        cursor = execute_query(
            """
            UPDATE students SET name = ?, email = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (clean_name, clean_email or None, student_id),
            commit=True,
        )
    if cursor.rowcount == 0:
        raise ValueError("Student was not found.")


def delete_student(student_id):
    """Delete one saved student and its dependent roadmaps and progress."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    cursor = execute_query(
        "DELETE FROM students WHERE id = ?", (student_id,), commit=True
    )
    if cursor.rowcount == 0:
        raise ValueError("Student was not found.")


def get_careers():
    """Return all available careers ordered by name."""
    return execute_query("SELECT * FROM careers ORDER BY name").fetchall()


def get_career(career_id):
    """Return a career by ID, or None when the ID does not exist."""
    return execute_query(
        "SELECT * FROM careers WHERE id = ?", (career_id,)
    ).fetchone()


def get_career_by_name(career_name):
    """Return a career by its unique name."""
    return execute_query(
        "SELECT * FROM careers WHERE name = ?", (career_name,)
    ).fetchone()


def get_skills():
    """Return all skills ordered by name."""
    return execute_query("SELECT * FROM skills ORDER BY name").fetchall()


def get_skills_for_career(career_id):
    """Return a career's required skills in dependency order."""
    query = """
        SELECT skills.*, career_skills.sequence_order
        FROM skills
        JOIN career_skills ON career_skills.skill_id = skills.id
        WHERE career_skills.career_id = ?
        ORDER BY career_skills.sequence_order, skills.name
    """
    return execute_query(query, (career_id,)).fetchall()


def get_student_skills(student_id):
    """Return a student's completed skills using the progress table."""
    query = """
        SELECT student_id, skill_id, status, progress_percent, created_at, updated_at
        FROM progress
        WHERE student_id = ? AND status = 'completed'
        ORDER BY skill_id
    """
    return execute_query(query, (student_id,)).fetchall()


def save_student_skills(student_id, skill_ids):
    """Replace a student's known-skill assessment with completed skill records."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    if get_student(student_id) is None:
        raise ValueError("Student was not found.")
    if not isinstance(skill_ids, (list, tuple, set)):
        raise ValueError("Skill IDs must be supplied as a collection.")
    normalized_ids = []
    for skill_id in skill_ids:
        if isinstance(skill_id, bool) or not isinstance(skill_id, int) or skill_id <= 0:
            raise ValueError("Skill IDs must be positive integers.")
        if skill_id not in normalized_ids:
            normalized_ids.append(skill_id)
    with transaction() as connection:
        connection.execute(
            """
            UPDATE progress
            SET status = 'not_started', progress_percent = 0,
                updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ? AND status = 'completed'
            """,
            (student_id,),
        )
        for skill_id in normalized_ids:
            exists = connection.execute(
                "SELECT 1 FROM skills WHERE id = ?", (skill_id,)
            ).fetchone()
            if exists is None:
                raise ValueError(f"Skill ID {skill_id} was not found.")
            connection.execute(
                """
                INSERT INTO progress (student_id, skill_id, status, progress_percent)
                VALUES (?, ?, 'completed', 100)
                ON CONFLICT(student_id, skill_id) DO UPDATE SET
                    status = 'completed', progress_percent = 100,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (student_id, skill_id),
            )


def get_resources_for_skill(skill_id):
    """Return learning resources for one skill."""
    return execute_query(
        "SELECT * FROM resources WHERE skill_id = ? ORDER BY title", (skill_id,)
    ).fetchall()


def create_roadmap(student_id, career_id):
    """Create and return a roadmap for a valid student and career."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    if isinstance(career_id, bool) or not isinstance(career_id, int) or career_id <= 0:
        raise ValueError("Career ID must be a positive integer.")
    if get_student(student_id) is None:
        raise ValueError("Student was not found.")
    if get_career(career_id) is None:
        raise ValueError("Career was not found.")
    with transaction() as connection:
        cursor = connection.execute(
            "INSERT INTO roadmaps (student_id, career_id) VALUES (?, ?)",
            (student_id, career_id),
        )
        roadmap_id = cursor.lastrowid
        connection.execute(
            """
            UPDATE progress SET roadmap_id = ?, updated_at = CURRENT_TIMESTAMP
            WHERE student_id = ?
            """,
            (roadmap_id, student_id),
        )
    return roadmap_id


def get_current_roadmap(student_id):
    """Return the most recently created roadmap for a student."""
    query = """
        SELECT roadmaps.*, careers.name AS career_name,
               careers.description AS career_description
        FROM roadmaps
        JOIN careers ON careers.id = roadmaps.career_id
        WHERE roadmaps.student_id = ?
        ORDER BY roadmaps.created_at DESC, roadmaps.id DESC
        LIMIT 1
    """
    return execute_query(query, (student_id,)).fetchone()


def save_progress(student_id, skill_id, status, progress_percent=None):
    """Save a validated progress value for one student's skill."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    if isinstance(skill_id, bool) or not isinstance(skill_id, int) or skill_id <= 0:
        raise ValueError("Skill ID must be a positive integer.")
    if get_student(student_id) is None:
        raise ValueError("Student was not found.")
    if execute_query("SELECT 1 FROM skills WHERE id = ?", (skill_id,)).fetchone() is None:
        raise ValueError("Skill was not found.")
    if progress_percent is None:
        progress_percent = (
            100 if status == "completed" else 1 if status == "in_progress" else 0
        )
    if isinstance(progress_percent, bool) or not isinstance(progress_percent, int):
        raise ValueError("Progress must be a whole number from 0 to 100.")
    if not 0 <= progress_percent <= 100:
        raise ValueError("Progress must be between 0 and 100.")
    if not isinstance(status, str) or status not in {
        "not_started", "in_progress", "completed"
    }:
        raise ValueError("Status must be not_started, in_progress, or completed.")
    expected_status = (
        "completed"
        if progress_percent == 100
        else "not_started"
        if progress_percent == 0
        else "in_progress"
    )
    if status != expected_status:
        raise ValueError("Status must match the saved progress percentage.")

    roadmap = get_current_roadmap(student_id)
    roadmap_id = roadmap["id"] if roadmap else None
    query = """
        INSERT INTO progress
            (student_id, roadmap_id, skill_id, status, progress_percent)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(student_id, skill_id) DO UPDATE SET
            roadmap_id = excluded.roadmap_id,
            status = excluded.status,
            progress_percent = excluded.progress_percent,
            updated_at = CURRENT_TIMESTAMP
    """
    execute_query(
        query,
        (student_id, roadmap_id, skill_id, status, progress_percent),
        commit=True,
    )


def save_progress_batch(student_id, progress_values):
    """Validate and atomically save several skill progress percentages."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    if get_student(student_id) is None:
        raise ValueError("Student was not found.")
    if not isinstance(progress_values, dict):
        raise ValueError("Progress values must be supplied as a skill-ID mapping.")
    for skill_id, percent in progress_values.items():
        if isinstance(skill_id, bool) or not isinstance(skill_id, int) or skill_id <= 0:
            raise ValueError("Skill IDs must be positive integers.")
        if isinstance(percent, bool) or not isinstance(percent, int) or not 0 <= percent <= 100:
            raise ValueError("Progress must be a whole number from 0 to 100.")
        if execute_query("SELECT 1 FROM skills WHERE id = ?", (skill_id,)).fetchone() is None:
            raise ValueError(f"Skill ID {skill_id} was not found.")

    roadmap = get_current_roadmap(student_id)
    roadmap_id = roadmap["id"] if roadmap else None
    with transaction() as connection:
        for skill_id, percent in progress_values.items():
            status = (
                "completed"
                if percent == 100
                else "not_started"
                if percent == 0
                else "in_progress"
            )
            connection.execute(
                """
                INSERT INTO progress
                    (student_id, roadmap_id, skill_id, status, progress_percent)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(student_id, skill_id) DO UPDATE SET
                    roadmap_id = excluded.roadmap_id,
                    status = excluded.status,
                    progress_percent = excluded.progress_percent,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (student_id, roadmap_id, skill_id, status, percent),
            )


def get_progress(student_id, skill_id):
    """Return progress for one student's skill."""
    return execute_query(
        "SELECT * FROM progress WHERE student_id = ? AND skill_id = ?",
        (student_id, skill_id),
    ).fetchone()


def get_progress_for_student(student_id, roadmap_id=None):
    """Return skill progress joined with names and most-recent update times."""
    query = """
        SELECT progress.*, skills.name AS skill_name,
               skills.description AS skill_description
        FROM progress
        JOIN skills ON skills.id = progress.skill_id
        WHERE progress.student_id = ?
    """
    params = [student_id]
    if roadmap_id is not None:
        query += " AND progress.roadmap_id = ?"
        params.append(roadmap_id)
    query += " ORDER BY progress.updated_at DESC, skills.name"
    return execute_query(query, tuple(params)).fetchall()


def get_resume_profile(student_id):
    """Return saved resume content for a student, or None if not created."""
    return execute_query(
        "SELECT * FROM resume_profiles WHERE student_id = ?", (student_id,)
    ).fetchone()


def save_resume_profile(
    student_id,
    career_id,
    headline,
    summary,
    education,
    projects,
    certifications,
    portfolio_url,
    linkedin_url,
):
    """Create or update a student's resume content in one transaction."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    if get_student(student_id) is None:
        raise ValueError("Student was not found.")
    if career_id is not None:
        if (
            isinstance(career_id, bool)
            or not isinstance(career_id, int)
            or career_id <= 0
        ):
            raise ValueError("Career ID must be a positive integer.")
        if get_career(career_id) is None:
            raise ValueError("Career was not found.")

    values = {
        "headline": headline,
        "summary": summary,
        "education": education,
        "projects": projects,
        "certifications": certifications,
        "portfolio URL": portfolio_url,
        "LinkedIn URL": linkedin_url,
    }
    for label, value in values.items():
        if not isinstance(value, str):
            raise ValueError(f"{label} must be text.")
        if len(value) > 10000:
            raise ValueError(f"{label} is too long (maximum 10,000 characters).")

    query = """
        INSERT INTO resume_profiles (
            student_id, career_id, headline, summary, education, projects,
            certifications, portfolio_url, linkedin_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id) DO UPDATE SET
            career_id = excluded.career_id,
            headline = excluded.headline,
            summary = excluded.summary,
            education = excluded.education,
            projects = excluded.projects,
            certifications = excluded.certifications,
            portfolio_url = excluded.portfolio_url,
            linkedin_url = excluded.linkedin_url,
            updated_at = CURRENT_TIMESTAMP
    """
    execute_query(
        query,
        (
            student_id,
            career_id,
            headline.strip(),
            summary.strip(),
            education.strip(),
            projects.strip(),
            certifications.strip(),
            portfolio_url.strip(),
            linkedin_url.strip(),
        ),
        commit=True,
    )
