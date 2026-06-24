from backend.models.create_engine import engine
from sqlalchemy import text

def create_system_info_table():
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """ CREATE TABLE IF NOT EXISTS system_info (
                    id SERIAL PRIMARY KEY,
                    run_id INTEGER NOT NULL,
                    os TEXT NOT NULL,
                    python_version TEXT NOT NULL,
                    gpu TEXT,
                    FOREIGN KEY (run_id) REFERENCES runs(id)
                    )
                    """
                )
            )
        print("System Info Table Created successfully!")
    except Exception as e:
        print(f"System Info Table wasn't created: {e}")
        raise
