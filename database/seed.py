from database.db import get_connection
from database.schema import init_db

def seed_db():
    init_db()
    conn = get_connection()
    
    # Careers
    conn.execute("INSERT OR IGNORE INTO careers (id, name, description) VALUES (1, 'Data Analyst', 'Analyzes data')")
    
    # Skills
    skills = [
        (1, 'SQL', 'Database querying'),
        (2, 'Python', 'Programming language'),
        (3, 'Data Visualization', 'Creating charts')
    ]
    conn.executemany("INSERT OR IGNORE INTO skills (id, name, description) VALUES (?, ?, ?)", skills)
    
    # Career Skills
    career_skills = [
        (1, 1, 1),
        (1, 2, 2),
        (1, 3, 3)
    ]
    conn.executemany("INSERT OR IGNORE INTO career_skills (career_id, skill_id, sequence_order) VALUES (?, ?, ?)", career_skills)
    
    # Resources
    resources = [
        (1, 1, 'Course', 'https://example.com/sql', 'SQL Basics'),
        (2, 2, 'Book', 'https://example.com/python', 'Python Guide'),
        (3, 3, 'Video', 'https://example.com/dataviz', 'Intro to Viz')
    ]
    conn.executemany("INSERT OR IGNORE INTO resources (id, skill_id, type, url, description) VALUES (?, ?, ?, ?, ?)", resources)
    
    conn.commit()

if __name__ == "__main__":
    seed_db()
