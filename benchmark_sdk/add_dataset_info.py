from backend.models.create_engine import engine
from sqlalchemy import text

def log_dataset_info(run_id, config):
    dataset = config.get("dataset")
    if not dataset:
        print("⚠️ No dataset configuration found in config.")
        return
    
    print(f"📖 Extracting dataset details for run ID: {run_id}")
    dataset_name = dataset.get("name")
    dataset_version = dataset.get("version")
    train_images = dataset.get("train_images")
    val_images = dataset.get("val_images")
    classes = dataset.get("classes")
    
    print(f"  - Dataset Name: {dataset_name}")
    print(f"  - Dataset Version: {dataset_version}")
    print(f"  - Train Images: {train_images}")
    print(f"  - Val Images: {val_images}")
    print(f"  - Classes: {classes}")

    print("💾 Saving dataset info to database...")
    with engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO dataset_info (run_id, dataset_name, dataset_version, train_images, val_images, classes)
                   VALUES (:run_id, :dataset_name, :dataset_version, :train_images, :val_images, :classes);
                """
            ),
            {
                "run_id": run_id,
                "dataset_name": dataset_name,
                "dataset_version": dataset_version,
                "train_images": train_images,
                "val_images": val_images,
                "classes": classes
            }
        )
    print("✅ Dataset info successfully written to database.")
