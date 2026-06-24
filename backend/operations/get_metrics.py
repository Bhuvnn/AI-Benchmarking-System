from backend.models.create_engine import engine
from sqlalchemy import text

def get_metrics(run_id):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT id, metric_name, metric_value 
                    FROM metrics 
                    WHERE run_id = :run_id 
                    ORDER BY id;
                    """
                ),
                {
                    "run_id": run_id
                }
            )
            return result.mappings().all()
    except Exception as e:
        print(f"An Unknown Error occurred: {e}")
        raise
