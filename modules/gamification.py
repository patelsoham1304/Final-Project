"""Gamification, learning streaks, and achievements system."""

from __future__ import annotations

import datetime
from database.db import (
    get_connection,
    get_current_roadmap,
    get_skills_for_career,
    get_student,
)
from modules.skill_assessment import get_assessments


def get_student_gamification_data(student_id: int) -> dict:
    """Calculate streak days, badges, and learning points (XP) for a student."""
    conn = get_connection()
    
    # Get all progress records to examine activity dates and completion
    rows = conn.execute(
        """
        SELECT skill_id, status, progress_percent, updated_at
        FROM progress
        WHERE student_id = ?
        ORDER BY updated_at DESC
        """,
        (student_id,),
    ).fetchall()

    assessments = get_assessments(student_id)
    assessed_count = len(assessments)
    completed_skills_count = sum(1 for r in rows if r["status"] == "completed" or r["progress_percent"] == 100)
    
    # Calculate unique active dates from progress & assessments
    active_dates = set()
    for r in rows:
        if r["updated_at"]:
            try:
                dt_str = str(r["updated_at"]).split()[0]
                active_dates.add(dt_str)
            except Exception:
                pass

    today = datetime.date.today()
    today_str = today.strftime("%Y-%m-%d")
    yesterday_str = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    # Current streak calculation:
    streak = 0
    check_date = today
    if today_str not in active_dates and yesterday_str in active_dates:
        check_date = today - datetime.timedelta(days=1)

    while check_date.strftime("%Y-%m-%d") in active_dates:
        streak += 1
        check_date -= datetime.timedelta(days=1)

    # Base streak fallback (if user is active today in session)
    if streak == 0 and completed_skills_count > 0:
        streak = 1

    # XP Calculation:
    # 50 XP per assessed skill, 150 XP per completed roadmap skill, 100 XP per streak day
    xp = (assessed_count * 50) + (completed_skills_count * 150) + (streak * 100)
    level = max(1, (xp // 300) + 1)
    next_level_xp = level * 300
    current_level_progress = int(((xp % 300) / 300) * 100)

    # Badges system
    badges = [
        {
            "id": "first_step",
            "name": "Quick Starter",
            "icon": "⚡",
            "desc": "Began learning path and assessed initial skills",
            "unlocked": assessed_count >= 1 or completed_skills_count >= 1,
        },
        {
            "id": "streak_master",
            "name": "Streak Warrior",
            "icon": "🔥",
            "desc": "Maintained an active learning streak",
            "unlocked": streak >= 1,
        },
        {
            "id": "skill_crusher",
            "name": "Skill Master",
            "icon": "🎯",
            "desc": "Mastered 3 or more technical skills",
            "unlocked": completed_skills_count >= 3 or assessed_count >= 3,
        },
        {
            "id": "career_focus",
            "name": "Career Focused",
            "icon": "💼",
            "desc": "Selected and locked an active career track",
            "unlocked": bool(get_current_roadmap(student_id)),
        },
        {
            "id": "super_scholar",
            "name": "Elite Scholar",
            "icon": "🏆",
            "desc": "Earned over 500 Learning XP",
            "unlocked": xp >= 500,
        },
    ]

    return {
        "streak": streak,
        "xp": xp,
        "level": level,
        "next_level_xp": next_level_xp,
        "level_progress": current_level_progress,
        "completed_count": completed_skills_count,
        "assessed_count": assessed_count,
        "badges": badges,
    }
