from backend.models.create_projects import create_projects_table
from backend.models.create_runs import create_runs_table
from backend.models.create_parameters import create_parameters_table
from backend.models.create_metrics import create_metrics_table
from backend.models.create_artifacts import create_artifacts_table
from backend.models.create_system_info import create_system_info_table
from backend.models.create_dataset_info import create_dataset_info_table

def initialize_database():
    print("🛠️ Database: Starting schema initialization...")
    create_projects_table()
    create_runs_table()
    create_parameters_table()
    create_metrics_table()
    create_artifacts_table()
    create_system_info_table()
    create_dataset_info_table()
    print("✅ Database: Schema initialization complete.")