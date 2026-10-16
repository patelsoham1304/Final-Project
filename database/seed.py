"""Idempotent career, ordered-skill, and resource catalog."""

from database.db import get_connection
from database.schema import init_db


CAREER_CATALOG = {
    "Data Analyst": {
        "description": "Find useful patterns in data and communicate evidence-based insights.",
        "skills": [
            "SQL",
            "Excel",
            "Statistics",
            "Python",
            "Pandas",
            "Data Visualization",
            "Data Analysis Project",
        ],
    },
    "Frontend Developer": {
        "description": "Build accessible, responsive interfaces for web applications.",
        "skills": [
            "HTML",
            "CSS",
            "JavaScript",
            "Git",
            "Responsive Design",
            "React",
            "Frontend Project",
        ],
    },
    "Backend Developer": {
        "description": "Design reliable application logic, APIs, and data storage.",
        "skills": [
            "Python",
            "Git",
            "SQL",
            "HTTP and REST APIs",
            "Backend Development",
            "Software Testing",
            "Backend Project",
        ],
    },
    "Data Scientist": {
        "description": "Use statistics and programming to model data and answer complex questions.",
        "skills": [
            "Python",
            "Statistics",
            "SQL",
            "NumPy",
            "Pandas",
            "Data Visualization",
            "Machine Learning Fundamentals",
            "Data Science Project",
        ],
    },
    "UI/UX Designer": {
        "description": "Research user needs and design clear, accessible digital experiences.",
        "skills": [
            "Design Principles",
            "User Research",
            "Wireframing",
            "Figma",
            "Prototyping",
            "Accessibility",
            "UX Portfolio Project",
        ],
    },
    "Cybersecurity Analyst": {
        "description": "Help protect systems by understanding threats, controls, and security signals.",
        "skills": [
            "Networking Fundamentals",
            "Linux Command Line",
            "Python",
            "Web Security Fundamentals",
            "OWASP Top 10",
            "Security Monitoring",
            "Cybersecurity Lab Project",
        ],
    },
}

SKILL_DETAILS = {
    "SQL": ("Query relational data and combine records.", "course", "https://sqlbolt.com/"),
    "Excel": ("Organize, clean, and summarize spreadsheet data.", "docs", "https://support.microsoft.com/excel"),
    "Statistics": ("Describe data and reason about uncertainty.", "course", "https://www.khanacademy.org/math/statistics-probability"),
    "Python": ("Use Python to write scripts and applications.", "docs", "https://docs.python.org/3/tutorial/"),
    "Pandas": ("Clean, transform, and analyze tabular data.", "docs", "https://pandas.pydata.org/docs/getting_started/intro_tutorials/"),
    "Data Visualization": ("Communicate findings with clear charts.", "article", "https://www.data-to-viz.com/"),
    "Data Analysis Project": ("Apply an end-to-end workflow to a dataset.", "article", "https://www.kaggle.com/datasets"),
    "HTML": ("Structure accessible content for the web.", "docs", "https://developer.mozilla.org/en-US/docs/Learn/HTML"),
    "CSS": ("Style web pages with reusable layout and visual rules.", "docs", "https://developer.mozilla.org/en-US/docs/Learn/CSS"),
    "JavaScript": ("Add interactive behavior to web applications.", "docs", "https://developer.mozilla.org/en-US/docs/Learn/JavaScript"),
    "Git": ("Track and collaborate on source-code changes.", "docs", "https://git-scm.com/doc"),
    "Responsive Design": ("Adapt page layouts to different screens and devices.", "docs", "https://developer.mozilla.org/en-US/docs/Learn/CSS/CSS_layout/Responsive_Design"),
    "React": ("Build component-based user interfaces.", "docs", "https://react.dev/learn"),
    "Frontend Project": ("Combine interface, accessibility, and responsive design in a portfolio project.", "article", "https://developer.mozilla.org/en-US/docs/Learn"),
    "HTTP and REST APIs": ("Understand HTTP requests and design resource-oriented APIs.", "docs", "https://developer.mozilla.org/en-US/docs/Web/HTTP"),
    "Backend Development": ("Organize server-side logic, validation, and data access.", "article", "https://roadmap.sh/backend"),
    "Software Testing": ("Write and run tests that check expected behavior.", "docs", "https://docs.python.org/3/library/unittest.html"),
    "Backend Project": ("Build and document a small data-backed application.", "article", "https://roadmap.sh/backend"),
    "NumPy": ("Work with numerical arrays and vectorized operations.", "docs", "https://numpy.org/doc/stable/user/absolute_beginners.html"),
    "Machine Learning Fundamentals": ("Learn basic model concepts and evaluation methods.", "course", "https://developers.google.com/machine-learning/crash-course"),
    "Data Science Project": ("Combine data preparation, analysis, and clear reporting.", "article", "https://www.kaggle.com/learn"),
    "Design Principles": ("Apply hierarchy, contrast, consistency, and visual balance.", "article", "https://www.nngroup.com/articles/principles-visual-design/"),
    "User Research": ("Learn to identify user needs through research methods.", "article", "https://www.nngroup.com/articles/ux-research-cheat-sheet/"),
    "Wireframing": ("Plan page structure before committing to visual detail.", "article", "https://www.figma.com/resource-library/what-is-wireframing/"),
    "Figma": ("Create interface layouts and collaborative design files.", "docs", "https://help.figma.com/hc/en-us"),
    "Prototyping": ("Communicate and test an interaction flow before development.", "article", "https://www.figma.com/resource-library/what-is-prototyping/"),
    "Accessibility": ("Design and build interfaces usable by people with different needs.", "docs", "https://www.w3.org/WAI/fundamentals/"),
    "UX Portfolio Project": ("Present a research-led design case study and its outcomes.", "article", "https://www.nngroup.com/articles/ux-portfolio/"),
    "Networking Fundamentals": ("Understand IP addressing, DNS, routing, and common protocols.", "course", "https://skillsforall.com/"),
    "Linux Command Line": ("Navigate files and run common commands in a Linux shell.", "course", "https://linuxjourney.com/"),
    "Web Security Fundamentals": ("Recognize common web risks and defensive practices.", "course", "https://portswigger.net/web-security"),
    "OWASP Top 10": ("Understand widely recognized web application security risks.", "docs", "https://owasp.org/www-project-top-ten/"),
    "Security Monitoring": ("Interpret logs and identify signals that may indicate security events.", "article", "https://www.cisa.gov/resources-tools"),
    "Cybersecurity Lab Project": ("Document a safe, authorized security learning exercise.", "course", "https://tryhackme.com/path/outline/beginner"),
}


def seed_db():
    """Create the schema and idempotently seed all supported career paths."""
    init_db()
    connection = get_connection()

    for career_name, career_data in CAREER_CATALOG.items():
        description = career_data["description"]
        connection.execute(
            "INSERT OR IGNORE INTO careers (name, description) VALUES (?, ?)",
            (career_name, description),
        )
        career_id = connection.execute(
            "SELECT id FROM careers WHERE name = ?", (career_name,)
        ).fetchone()["id"]
        connection.execute(
            """
            UPDATE careers SET description = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ? AND COALESCE(description, '') <> ?
            """,
            (description, career_id, description),
        )

        for skill_name in career_data["skills"]:
            description, _, _ = SKILL_DETAILS[skill_name]
            connection.execute(
                "INSERT OR IGNORE INTO skills (name, description) VALUES (?, ?)",
                (skill_name, description),
            )

        existing_mapping = connection.execute(
            """
            SELECT skills.name, career_skills.sequence_order
            FROM career_skills
            JOIN skills ON skills.id = career_skills.skill_id
            WHERE career_skills.career_id = ?
            ORDER BY career_skills.sequence_order, skills.name
            """,
            (career_id,),
        ).fetchall()
        expected_mapping = list(enumerate(career_data["skills"], start=1))
        saved_mapping = [
            (row["sequence_order"], row["name"]) for row in existing_mapping
        ]
        if saved_mapping != expected_mapping:
            connection.execute(
                "DELETE FROM career_skills WHERE career_id = ?", (career_id,)
            )

        for position, skill_name in enumerate(career_data["skills"], start=1):
            skill_id = connection.execute(
                "SELECT id FROM skills WHERE name = ?", (skill_name,)
            ).fetchone()["id"]
            connection.execute(
                """
                INSERT OR IGNORE INTO career_skills
                    (career_id, skill_id, sequence_order)
                VALUES (?, ?, ?)
                """,
                (career_id, skill_id, position),
            )
            title = f"{skill_name} learning resource"
            _, resource_type, url = SKILL_DETAILS[skill_name]
            connection.execute(
                """
                INSERT INTO resources
                    (skill_id, title, type, url, is_free)
                SELECT ?, ?, ?, ?, 1
                WHERE NOT EXISTS (
                    SELECT 1 FROM resources WHERE skill_id = ?
                )
                """,
                (skill_id, title, resource_type, url, skill_id),
            )

    connection.commit()


if __name__ == "__main__":
    seed_db()
