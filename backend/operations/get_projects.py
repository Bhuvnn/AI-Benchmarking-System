# Operation to retrieve projects from the database
from backend.models.create_engine import engine
from sqlalchemy import text

def get_projects():
    try:
        with engine.begin() as conn:
            result=conn.execute(text(
                """ 
                SELECT id, project_name, status 
                FROM projects 
                ORDER BY id
                """
            ))
            return result.mappings().all()
    except Exception as e:
        print(f"An Unknown Error occurred: {e}")
        raise
    