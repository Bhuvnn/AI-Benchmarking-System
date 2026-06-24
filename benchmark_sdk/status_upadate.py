from backend.models.create_engine import engine
from sqlalchemy import text

def update_status(run_id,status):
    try:
        with engine.begin() as conn:
            conn.execute(text(
                """ UPDATE runs 
                    SET status =:status,
                    ended_at = CURRENT_TIMESTAMP
                    WHERE id = :run_id;
                """
            ),
            {
                "status": status,
                "run_id": run_id
            })
    except Exception as e:
        print(f"An Unexpected Error occured: {e}")
        raise

