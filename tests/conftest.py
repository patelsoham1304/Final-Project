import sys
from pathlib import Path
import os
import pytest

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Force test DB
os.environ["TESTING"] = "1"

@pytest.fixture(autouse=True)
def isolated_db(monkeypatch, tmp_path):
    # Override DB_PATH for tests
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("database.db.DB_PATH", db_file)
    
    # Need to clear cache so get_connection uses the new path
    import database.db
    if hasattr(database.db.get_connection, "clear"):
        database.db.get_connection.clear()
    elif hasattr(database.db.get_connection, "cache_clear"):
        database.db.get_connection.cache_clear()
        
    from database.schema import init_db
    init_db()
    yield
