from backend.models.create_engine import engine
from sqlalchemy import text

def create_runs_table():
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """ CREATE TABLE IF NOT EXISTS runs (
                    id SERIAL PRIMARY KEY,
                    project_id INTEGER NOT NULL,
                    version_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id),
                    UNIQUE (project_id, version_name)
                    )
                    """
                )
            )
        print("Runs Table Created")
    except Exception as e:
        print(f"Runs Table wasn't created: {e}")
        raise



