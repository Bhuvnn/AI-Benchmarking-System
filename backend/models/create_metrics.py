from backend.models.create_engine import engine
from sqlalchemy import text

def create_metrics_table():
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """ CREATE TABLE IF NOT EXISTS metrics (
                    id SERIAL PRIMARY KEY,
                    run_id INTEGER NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value DOUBLE PRECISION NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES runs(id) 
                    )
                    """
                )
            )
        print("Metrics Table Created")
    except Exception as e:
        print(f"Metrics Table wasn't created: {e}")
        raise
