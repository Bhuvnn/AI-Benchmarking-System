from backend.models.create_engine import engine
from sqlalchemy import text

def create_artifacts_table():
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """ CREATE TABLE IF NOT EXISTS artifacts (
                    id SERIAL PRIMARY KEY,
                    run_id INTEGER NOT NULL,
                    artifact_path TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES runs(id)
                    )
                    """
                )
            )
        print("Artifacts Table Created")
    except Exception as e:
        print(f"Artifacts Table wasn't created: {e}")
        raise
