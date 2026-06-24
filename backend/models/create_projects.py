from backend.models.create_engine import engine
from sqlalchemy import text

def create_projects_table():
    try:
        with engine.begin() as conn:
            conn.execute(text("""CREATE TABLE IF NOT EXISTS projects (
                            id SERIAL PRIMARY KEY,
                            project_name TEXT NOT NULL,
                            status TEXT NOT NULL DEFAULT 'active');""")
                            ) 
        print("Project Table Created Successfully!")
    except Exception as e:
        print(f"Failed to create projects table: {e}")
        raise

 
    