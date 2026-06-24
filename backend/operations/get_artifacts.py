from backend.models.create_engine import engine
from sqlalchemy import text

def get_artifacts(run_id):
    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT id, artifact_path, artifact_type 
                    FROM artifacts 
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
