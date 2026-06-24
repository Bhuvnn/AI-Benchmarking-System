from backend.models.create_engine import engine
from sqlalchemy import text
def project_creation(project_name):
    print(f"📦 Database: Inserting new project '{project_name}' into 'projects' table...")
    with engine.begin() as conn:
        result=conn.execute(text(
            """INSERT INTO projects (project_name,status)
            VALUES (:project_name, :status)
            RETURNING id;
            """
        ),
        {
            "project_name": project_name,
            "status": "active"
        }
        )
    
    project_id = result.scalar()
    print(f"📦 Database: Project '{project_name}' created successfully with ID: {project_id}")
    return project_id
