"""Student-profile operations."""

import sqlite3

from database.db import create_student, get_student, get_students, update_student


def create_student_profile(name: str, email: str | None = None) -> int:
    """Validate and save a student profile."""
    return create_student(name, email)


def get_student_profile(student_id: int) -> sqlite3.Row:
    """Load one saved student profile by database ID."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    student = get_student(student_id)
    if student is None:
        raise ValueError("Student was not found.")
    return student


def list_student_profiles() -> list[sqlite3.Row]:
    """List the profiles available for the single-active-profile selector."""
    return get_students()


def update_student_profile(
    student_id: int, name: str, email: str | None = None
) -> None:
    """Update a saved student profile."""
    if isinstance(student_id, bool) or not isinstance(student_id, int) or student_id <= 0:
        raise ValueError("Student ID must be a positive integer.")
    update_student(student_id, name, email)
