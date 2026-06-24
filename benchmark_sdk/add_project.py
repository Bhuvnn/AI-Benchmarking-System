from backend.operations.project import project_creation
from backend.operations.run import get_project_id,runs_creation
from backend.models.initialize import initialize_database


def add_project_to_database(config):
    project=config["project"]
    try:
        print("🛠️ Initializing database tables (if they do not exist)...")
        initialize_database() 
        print(f"🔍 Looking up project '{project['name']}'...")
        project_id=get_project_id(project["name"])
        if project_id is None:
            print(f"➕ Project '{project['name']}' doesn't exist. Creating a new project...")
            project_id=project_creation(project["name"])
        else:
            print(f"📂 Found existing project '{project['name']}' with ID {project_id}")

        print(f"➕ Creating a new run version '{project['version']}'...")
        runs=runs_creation(project_id,project["version"])
        if runs:
            print(f"✨ A new run version '{project['version']}' created with ID: {runs}")
        
    except Exception as e:
        print(f"❌ An unexpected error occurred in add_project_to_database: {e}")
        raise

    return runs