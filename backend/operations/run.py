from backend.models.create_engine import engine
from sqlalchemy import text

def get_project_id(project_name):
    print(f"🔍 Database: Searching for project '{project_name}' in 'projects' table...")
    with engine.begin() as conn:
        result=conn.execute(text(
            """SELECT id FROM projects WHERE project_name = :project_name;
            """
        ),
        {
            "project_name": project_name
        }
        )
    
    project_id = result.scalar()
    if project_id:
        print(f"🔍 Database: Found project '{project_name}' with ID {project_id}")
    else:
        print(f"🔍 Database: Project '{project_name}' not found.")
    return project_id

def runs_creation(project_id,runs_name):
    print(f"📦 Database: Inserting new run '{runs_name}' for project ID {project_id}...")
    with engine.begin() as conn:
        result=conn.execute(text(
            """INSERT INTO RUNS (project_id, version_name,status)
            VALUES (:project_id, :version_name, :status)
            RETURNING ID;
            """
        ),
        {
            "project_id": project_id,
            "version_name":runs_name,
            "status":"In Progress"
        }
        )
    run_id = result.scalar()
    print(f"📦 Database: Run '{runs_name}' created successfully with run ID {run_id}")
    return run_id
