"""SQLite schema creation and migration helpers."""

from database.db import get_connection


def _table_exists(connection, table_name):
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def _migrate_legacy_core_tables(connection):
    """Rebuild older core tables with text timestamps and optional email."""
    layouts = {
        "students": """
            CREATE TABLE students_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                email TEXT UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "careers": """
            CREATE TABLE careers_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "skills": """
            CREATE TABLE skills_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """,
    }
    needs_migration = False
    for table_name in layouts:
        if not _table_exists(connection, table_name):
            continue
        columns = {
            row["name"]: row
            for row in connection.execute(f"PRAGMA table_info({table_name})")
        }
        timestamps_are_text = all(
            column in columns and columns[column]["type"].upper() == "TEXT"
            for column in ("created_at", "updated_at")
        )
        email_is_optional = (
            table_name != "students"
            or "email" not in columns
            or columns["email"]["notnull"] == 0
        )
        needs_migration = needs_migration or not (
            timestamps_are_text and email_is_optional
        )

    if not needs_migration:
        return

    connection.commit()
    connection.execute("PRAGMA foreign_keys = OFF")
    try:
        for table_name, create_statement in layouts.items():
            if not _table_exists(connection, table_name):
                continue
            columns = {
                row["name"]
                for row in connection.execute(f"PRAGMA table_info({table_name})")
            }
            email_value = "email" if "email" in columns else "NULL"
            description_value = (
                "COALESCE(description, '')" if "description" in columns else "''"
            )
            connection.execute(f"DROP TABLE IF EXISTS {table_name}_new")
            connection.execute(create_statement)
            connection.execute(
                f"""
                INSERT INTO {table_name}_new
                    (id, name, { 'email, ' if table_name == 'students' else '' }
                     { 'description, ' if table_name != 'students' else '' }
                     created_at, updated_at)
                SELECT id, name,
                       {email_value + ',' if table_name == 'students' else ''}
                       {description_value + ',' if table_name != 'students' else ''}
                       COALESCE(created_at, CURRENT_TIMESTAMP),
                       COALESCE(updated_at, created_at, CURRENT_TIMESTAMP)
                FROM {table_name}
                """
            )
            connection.execute(f"DROP TABLE {table_name}")
            connection.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.execute("PRAGMA foreign_keys = ON")


def _migrate_legacy_progress(connection):
    if not _table_exists(connection, "progress"):
        return False

    columns = {
        row["name"] for row in connection.execute("PRAGMA table_info(progress)")
    }
    if "resource_id" in columns and "skill_id" not in columns:
        if _table_exists(connection, "_legacy_progress"):
            connection.execute("DROP TABLE _legacy_progress")
        connection.execute("ALTER TABLE progress RENAME TO _legacy_progress")
        return True
    return False


def _migrate_legacy_resources(connection):
    if not _table_exists(connection, "resources"):
        return False

    columns = {
        row["name"]: row
        for row in connection.execute("PRAGMA table_info(resources)")
    }
    if (
        not {"title", "is_free", "created_at", "updated_at"}.issubset(columns)
        or columns["created_at"]["type"].upper() != "TEXT"
        or columns["updated_at"]["type"].upper() != "TEXT"
    ):
        if _table_exists(connection, "_legacy_resources"):
            connection.execute("DROP TABLE _legacy_resources")
        connection.execute("ALTER TABLE resources RENAME TO _legacy_resources")
        return True
    return False


def _migrate_legacy_career_skills(connection):
    if not _table_exists(connection, "career_skills"):
        return False

    columns = {
        row["name"]: row
        for row in connection.execute("PRAGMA table_info(career_skills)")
    }
    foreign_key_tables = {
        row["table"] for row in connection.execute("PRAGMA foreign_key_list(career_skills)")
    }
    timestamp_columns_are_text = all(
        column in columns and columns[column]["type"].upper() == "TEXT"
        for column in ("created_at", "updated_at")
    )
    if (
        not timestamp_columns_are_text
        or foreign_key_tables != {"careers", "skills"}
    ):
        if _table_exists(connection, "_legacy_career_skills"):
            connection.execute("DROP TABLE _legacy_career_skills")
        connection.execute(
            "ALTER TABLE career_skills RENAME TO _legacy_career_skills"
        )
        return True
    return False


def init_db():
    """Create all application tables and migrate the previous progress schema."""
    connection = get_connection()
    _migrate_legacy_core_tables(connection)
    migrated_progress = _migrate_legacy_progress(connection)
    migrated_resources = _migrate_legacy_resources(connection)
    migrated_career_skills = _migrate_legacy_career_skills(connection)
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK (length(trim(name)) > 0),
            email TEXT UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS careers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS career_skills (
            career_id INTEGER NOT NULL,
            skill_id INTEGER NOT NULL,
            sequence_order INTEGER NOT NULL CHECK (sequence_order > 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (career_id, skill_id),
            UNIQUE (career_id, sequence_order),
            FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE CASCADE,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS roadmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            career_id INTEGER NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            roadmap_id INTEGER,
            skill_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'not_started'
                CHECK (status IN ('not_started', 'in_progress', 'completed')),
            progress_percent INTEGER NOT NULL DEFAULT 0
                CHECK (progress_percent BETWEEN 0 AND 100),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (student_id, skill_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (roadmap_id) REFERENCES roadmaps(id) ON DELETE SET NULL,
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('video', 'article', 'course', 'docs')),
            url TEXT NOT NULL,
            is_free INTEGER NOT NULL DEFAULT 1 CHECK (is_free IN (0, 1)),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (skill_id, title),
            FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS resume_profiles (
            student_id INTEGER PRIMARY KEY,
            career_id INTEGER,
            headline TEXT NOT NULL DEFAULT '',
            summary TEXT NOT NULL DEFAULT '',
            education TEXT NOT NULL DEFAULT '',
            projects TEXT NOT NULL DEFAULT '',
            certifications TEXT NOT NULL DEFAULT '',
            portfolio_url TEXT NOT NULL DEFAULT '',
            linkedin_url TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (career_id) REFERENCES careers(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_progress_student
            ON progress(student_id, updated_at);
        CREATE INDEX IF NOT EXISTS idx_roadmaps_student
            ON roadmaps(student_id, created_at);
        """
    )

    if migrated_career_skills and _table_exists(connection, "_legacy_career_skills"):
        connection.execute(
            """
            INSERT OR IGNORE INTO career_skills
                (career_id, skill_id, sequence_order)
            SELECT career_id, skill_id, sequence_order
            FROM _legacy_career_skills
            ORDER BY career_id, sequence_order, skill_id
            """
        )
        connection.execute("DROP TABLE _legacy_career_skills")
    connection.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_career_skills_order
        ON career_skills(career_id, sequence_order)
        """
    )

    if migrated_resources and _table_exists(connection, "_legacy_resources"):
        connection.execute(
            """
            INSERT OR IGNORE INTO resources
                (id, skill_id, title, type, url, is_free)
            SELECT id, skill_id, COALESCE(NULLIF(description, ''), type || ' resource'),
                   CASE lower(type)
                       WHEN 'video' THEN 'video'
                       WHEN 'article' THEN 'article'
                       WHEN 'course' THEN 'course'
                       WHEN 'docs' THEN 'docs'
                       ELSE 'article'
                   END,
                   url, 1
            FROM _legacy_resources
            """
        )
    if _table_exists(connection, "student_skills"):
        connection.execute(
            """
            INSERT OR IGNORE INTO progress
                (student_id, skill_id, status, progress_percent)
            SELECT student_id, skill_id, 'completed', 100
            FROM student_skills
            """
        )
        connection.execute("DROP TABLE student_skills")

    if migrated_progress and _table_exists(connection, "_legacy_progress"):
        legacy_resource_table = (
            "_legacy_resources"
            if _table_exists(connection, "_legacy_resources")
            else "resources"
        )
        connection.execute(
            f"""
            INSERT OR IGNORE INTO progress
                (student_id, skill_id, status, progress_percent, updated_at)
            SELECT old.student_id, resource.skill_id,
                   CASE WHEN lower(old.status) IN ('completed', 'complete')
                        THEN 'completed' ELSE 'in_progress' END,
                   CASE WHEN lower(old.status) IN ('completed', 'complete')
                        THEN 100 ELSE 0 END,
                   COALESCE(old.updated_at, CURRENT_TIMESTAMP)
            FROM _legacy_progress AS old
            JOIN {legacy_resource_table} AS resource
                ON resource.id = old.resource_id
            """
        )
        connection.execute("DROP TABLE _legacy_progress")

    if migrated_resources and _table_exists(connection, "_legacy_resources"):
        connection.execute("DROP TABLE _legacy_resources")

    connection.commit()
