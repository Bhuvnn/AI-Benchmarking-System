# Operation to retrieve runs from the database
from backend.models.create_engine import engine
from sqlalchemy import text

def get_runs(project_id):
    try:
        with engine.begin() as conn:
            result=conn.execute(text(
                """ 
                SELECT id,version_name,status,created_at,ended_at 
                FROM runs 
                WHERE project_id = :project_id 
                ORDER BY created_at DESC;
                """
            ),
            {
                "project_id": project_id
            }
            )
            return result.mappings().all()
    except Exception as e:
        print(f"An Unknown Error occurred: {e}")
        raise