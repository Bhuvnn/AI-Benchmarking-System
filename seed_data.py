"""
Seed script: Creates a new project 'chest_xray_classifier' with 4 runs (v1-v4)
each having metrics, parameters, dataset info, system info, and artifacts.
"""
from backend.models.create_engine import engine
from sqlalchemy import text

def seed():
    with engine.begin() as conn:
        # ── Create project ──
        pid = conn.execute(text(
            "INSERT INTO projects (project_name, status) VALUES (:name, 'active') RETURNING id"
        ), {"name": "chest_xray_classifier"}).scalar()
        print(f"Created project chest_xray_classifier (id={pid})")

        # ── Run definitions ──
        runs = [
            {
                "version": "v1",
                "status": "Completed",
                "params": {
                    "model": "ResNet-50",
                    "epochs": "50",
                    "batch_size": "32",
                    "learning_rate": "0.001",
                    "optimizer": "SGD",
                    "weight_decay": "0.0001",
                    "image_size": "224",
                    "dropout": "0.3",
                    "scheduler": "step",
                    "augmentation": "False",
                },
                "metrics": {
                    "accuracy": 0.82,
                    "precision": 0.79,
                    "recall": 0.76,
                    "f1_score": 0.77,
                    "auc_roc": 0.85,
                    "loss": 0.48,
                },
                "dataset": {
                    "name": "ChestX-ray14",
                    "version": "v1.0",
                    "train": 18000,
                    "val": 3200,
                    "classes": 14,
                },
                "system": {"os": "Ubuntu 22.04", "python": "3.10.12", "gpu": "NVIDIA RTX 3090"},
                "artifacts": [
                    ("runs/v1/best.pt", "checkpoint"),
                    ("runs/v1/results.csv", "csv"),
                ],
            },
            {
                "version": "v2",
                "status": "Completed",
                "params": {
                    "model": "ResNet-50",
                    "epochs": "80",
                    "batch_size": "32",
                    "learning_rate": "0.0005",
                    "optimizer": "Adam",
                    "weight_decay": "0.0003",
                    "image_size": "224",
                    "dropout": "0.4",
                    "scheduler": "cosine",
                    "augmentation": "True",
                },
                "metrics": {
                    "accuracy": 0.87,
                    "precision": 0.84,
                    "recall": 0.82,
                    "f1_score": 0.83,
                    "auc_roc": 0.90,
                    "loss": 0.35,
                },
                "dataset": {
                    "name": "ChestX-ray14",
                    "version": "v1.0",
                    "train": 18000,
                    "val": 3200,
                    "classes": 14,
                },
                "system": {"os": "Ubuntu 22.04", "python": "3.10.12", "gpu": "NVIDIA RTX 3090"},
                "artifacts": [
                    ("runs/v2/best.pt", "checkpoint"),
                    ("runs/v2/last.pt", "checkpoint"),
                    ("runs/v2/results.csv", "csv"),
                ],
            },
            {
                "version": "v3",
                "status": "Completed",
                "params": {
                    "model": "EfficientNet-B4",
                    "epochs": "100",
                    "batch_size": "16",
                    "learning_rate": "0.0003",
                    "optimizer": "AdamW",
                    "weight_decay": "0.0005",
                    "image_size": "380",
                    "dropout": "0.35",
                    "scheduler": "cosine",
                    "augmentation": "True",
                },
                "metrics": {
                    "accuracy": 0.91,
                    "precision": 0.89,
                    "recall": 0.88,
                    "f1_score": 0.88,
                    "auc_roc": 0.94,
                    "loss": 0.24,
                },
                "dataset": {
                    "name": "ChestX-ray14",
                    "version": "v2.0",
                    "train": 24000,
                    "val": 4500,
                    "classes": 14,
                },
                "system": {"os": "Ubuntu 22.04", "python": "3.11.5", "gpu": "NVIDIA A100 40GB"},
                "artifacts": [
                    ("runs/v3/best.pt", "checkpoint"),
                    ("runs/v3/last.pt", "checkpoint"),
                    ("runs/v3/results.csv", "csv"),
                    ("runs/v3/confusion_matrix.png", "image"),
                ],
            },
            {
                "version": "v4",
                "status": "Completed",
                "params": {
                    "model": "EfficientNet-B4",
                    "epochs": "120",
                    "batch_size": "16",
                    "learning_rate": "0.0001",
                    "optimizer": "AdamW",
                    "weight_decay": "0.0005",
                    "image_size": "380",
                    "dropout": "0.3",
                    "scheduler": "cosine",
                    "augmentation": "True",
                    "mixed_precision": "True",
                    "warmup_epochs": "5",
                },
                "metrics": {
                    "accuracy": 0.94,
                    "precision": 0.92,
                    "recall": 0.91,
                    "f1_score": 0.91,
                    "auc_roc": 0.96,
                    "loss": 0.17,
                },
                "dataset": {
                    "name": "ChestX-ray14",
                    "version": "v2.0",
                    "train": 24000,
                    "val": 4500,
                    "classes": 14,
                },
                "system": {"os": "Ubuntu 22.04", "python": "3.11.5", "gpu": "NVIDIA A100 40GB"},
                "artifacts": [
                    ("runs/v4/best.pt", "checkpoint"),
                    ("runs/v4/last.pt", "checkpoint"),
                    ("runs/v4/results.csv", "csv"),
                    ("runs/v4/confusion_matrix.png", "image"),
                    ("runs/v4/roc_curve.png", "image"),
                ],
            },
        ]

        for run in runs:
            # Insert run
            rid = conn.execute(text(
                "INSERT INTO runs (project_id, version_name, status) VALUES (:pid, :ver, :status) RETURNING id"
            ), {"pid": pid, "ver": run["version"], "status": run["status"]}).scalar()
            print(f"  Run {run['version']} (id={rid})")

            # Parameters
            for k, v in run["params"].items():
                conn.execute(text(
                    "INSERT INTO parameters (run_id, parameter_name, parameter_value) VALUES (:rid, :name, :val)"
                ), {"rid": rid, "name": k, "val": v})

            # Metrics
            for k, v in run["metrics"].items():
                conn.execute(text(
                    "INSERT INTO metrics (run_id, metric_name, metric_value) VALUES (:rid, :name, :val)"
                ), {"rid": rid, "name": k, "val": v})

            # Dataset info
            ds = run["dataset"]
            conn.execute(text(
                "INSERT INTO dataset_info (run_id, dataset_name, dataset_version, train_images, val_images, classes) "
                "VALUES (:rid, :name, :ver, :train, :val, :cls)"
            ), {"rid": rid, "name": ds["name"], "ver": ds["version"], "train": ds["train"], "val": ds["val"], "cls": ds["classes"]})

            # System info
            si = run["system"]
            conn.execute(text(
                "INSERT INTO system_info (run_id, os, python_version, gpu) VALUES (:rid, :os, :py, :gpu)"
            ), {"rid": rid, "os": si["os"], "py": si["python"], "gpu": si["gpu"]})

            # Artifacts
            for path, atype in run["artifacts"]:
                conn.execute(text(
                    "INSERT INTO artifacts (run_id, artifact_path, artifact_type) VALUES (:rid, :path, :type)"
                ), {"rid": rid, "path": path, "type": atype})

    print("\nDone! Project 'chest_xray_classifier' seeded with 4 runs.")

if __name__ == "__main__":
    seed()
