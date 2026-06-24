from backend.models.create_engine import engine
from sqlalchemy import text

def identify_artifact_type(file):
    if "." not in file:
        return "file"
    extension=file.split(".")[-1].lower()

    artifact_types={
        "checkpoint": ["pt", "pth", "ckpt"],
        "csv": ["csv"],
        "spreadsheet": ["xlsx", "xls"],
        "json": ["json"],
        "config": ["yaml", "yml"],
        "image": ["png", "jpg", "jpeg", "webp"],
        "text": ["txt", "log"],
        "document": ["pdf","docx","doc"]
    }

    for key,item in artifact_types.items():
        if extension in item:
            return key
    
    return "file"

def add_artifacts_to_database(run_id,artifact_path,artifact_type):
    try:
        with engine.begin() as conn:
            conn.execute(text(
                """INSERT INTO artifacts (run_id, artifact_path, artifact_type)
                    VALUES (:run_id, :artifact_path, :artifact_type);
                """
            ),
            {
                "run_id":run_id,
                "artifact_path": artifact_path,
                "artifact_type": artifact_type
            }
            )
        print("✅ Artifacts rows successfully written to database.")
    
    except Exception as e:
        print(f"Some unexpected Error occured {e}")
        raise