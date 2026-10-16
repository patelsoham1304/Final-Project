"""Career catalog and ordered skill requirements."""

import sqlite3

from database.db import (
    get_careers,
    get_career,
    get_career_by_name,
    get_skills_for_career,
)


def list_careers() -> list[sqlite3.Row]:
    """Return careers that can be selected in the app."""
    return get_careers()


def get_career_requirements(career_id: int) -> list[dict]:
    """Return required skill records ordered by the career's sequence."""
    if isinstance(career_id, bool) or not isinstance(career_id, int) or career_id <= 0:
        raise ValueError("Career ID must be a positive integer.")
    if get_career(career_id) is None:
        raise ValueError("Career was not found.")
    return [dict(row) for row in get_skills_for_career(career_id)]


def find_career_by_name(career_name: str) -> sqlite3.Row | None:
    """Find a career by its exact saved name."""
    if not isinstance(career_name, str) or not career_name.strip():
        raise ValueError("Career name cannot be empty.")
    return get_career_by_name(career_name.strip())
