from backend.models.create_engine import engine
from sqlalchemy import text

def create_parameters_table():
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """ CREATE TABLE IF NOT EXISTS parameters (
                    id SERIAL PRIMARY KEY,
                    run_id INTEGER NOT NULL,
                    parameter_name TEXT NOT NULL,
                    parameter_value TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES runs(id) 
                    )
                    """
                )
            )
        print("Parameters Table Created")
    except Exception as e:
        print(f"Parameters Table wasn't created: {e}")
        raise



