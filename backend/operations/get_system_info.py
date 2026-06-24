from backend.models.create_engine import engine
from sqlalchemy import text

def get_system_info(run_id):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT id, os, python_version, gpu 
                    FROM system_info 
                    WHERE run_id = :run_id;
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
