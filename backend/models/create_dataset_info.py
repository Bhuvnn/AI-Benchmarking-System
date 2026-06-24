from backend.models.create_engine import engine
from sqlalchemy import text

def create_dataset_info_table():
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    """ CREATE TABLE IF NOT EXISTS dataset_info (
                    id SERIAL PRIMARY KEY,
                    run_id INTEGER NOT NULL,
                    dataset_name TEXT NOT NULL,
                    dataset_version TEXT NOT NULL,
                    train_images INTEGER,
                    val_images INTEGER,
                    classes INTEGER,
                    FOREIGN KEY (run_id) REFERENCES runs(id)
                    )
                    """
                )
            )
        print("Dataset Info Table Created successfully!")
    except Exception as e:
        print(f"Dataset Info Table wasn't created: {e}")
        raise
