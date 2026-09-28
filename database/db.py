import sqlite3
from pathlib import Path
import functools

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "education_path.db"

# Ponytail: try importing streamlit, if not in a streamlit run or it fails, fallback to simple lru_cache
try:
    import streamlit as st
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    if get_script_run_ctx() is not None:
        cache_decorator = st.cache_resource
    else:
        cache_decorator = functools.lru_cache(maxsize=1)
except ImportError:
    cache_decorator = functools.lru_cache(maxsize=1)

@cache_decorator
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def execute_query(query, params=(), commit=False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    if commit:
        conn.commit()
    return cur

def execute_many(query, params_list, commit=False):
    conn = get_connection()
    cur = conn.cursor()
    cur.executemany(query, params_list)
    if commit:
        conn.commit()
    return cur

# Students
def get_student(student_id):
    return execute_query("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()

def create_student(name, email):
    cur = execute_query("INSERT INTO students (name, email) VALUES (?, ?)", (name, email), commit=True)
    return cur.lastrowid

def update_student(student_id, name, email):
    execute_query("UPDATE students SET name = ?, email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (name, email, student_id), commit=True)

# Careers
def get_careers():
    return execute_query("SELECT * FROM careers").fetchall()

def get_career(career_id):
    return execute_query("SELECT * FROM careers WHERE id = ?", (career_id,)).fetchone()

# Skills
def get_skills():
    return execute_query("SELECT * FROM skills").fetchall()

def get_skills_for_career(career_id):
    query = """
        SELECT s.*, cs.sequence_order 
        FROM skills s 
        JOIN career_skills cs ON s.id = cs.skill_id 
        WHERE cs.career_id = ? 
        ORDER BY cs.sequence_order
    """
    return execute_query(query, (career_id,)).fetchall()

# Student Skills
def get_student_skills(student_id):
    return execute_query("SELECT * FROM student_skills WHERE student_id = ?", (student_id,)).fetchall()

def save_student_skills(student_id, skill_ids):
    # Ponytail: Delete existing to overwrite, simpler than merge
    conn = get_connection()
    conn.execute("DELETE FROM student_skills WHERE student_id = ?", (student_id,))
    conn.executemany("INSERT INTO student_skills (student_id, skill_id) VALUES (?, ?)", [(student_id, sid) for sid in skill_ids])
    conn.commit()

# Resources
def get_resources_for_skill(skill_id):
    return execute_query("SELECT * FROM resources WHERE skill_id = ?", (skill_id,)).fetchall()

# Progress
def get_progress(student_id, resource_id):
    return execute_query("SELECT * FROM progress WHERE student_id = ? AND resource_id = ?", (student_id, resource_id)).fetchone()

def save_progress(student_id, resource_id, status):
    query = """
        INSERT INTO progress (student_id, resource_id, status) VALUES (?, ?, ?)
        ON CONFLICT(student_id, resource_id) DO UPDATE SET status = excluded.status, updated_at = CURRENT_TIMESTAMP
    """
    execute_query(query, (student_id, resource_id, status), commit=True)
