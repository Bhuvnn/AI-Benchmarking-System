"""
YOLOv8 Object Detection — Multi-Version Training Lifecycle
==========================================================
Simulates a complete, realistic training lifecycle for a YOLOv8 detection model
across 5 versions (v1→v5), each with:
  - Different hyperparameter configurations
  - Progressively improving (and occasionally dropping) metrics
  - Realistic YOLO detection metrics: mAP50, mAP50-95, Precision, Recall, F1, box_loss, cls_loss, dfl_loss
  - Artifact logging (weights + plots)
  - Proper run lifecycle: start → log_metrics → log_artifacts → finish / fail
"""

import sys
import time
import importlib

# ── SDK import ──
from benchmark_sdk import benchmark

# ─────────────────────────────────────────────────────────────
# VERSION CONFIGS  (one dict per training run)
# Each version intentionally tweaks different hyperparameters
# to simulate a real iterative optimisation workflow.
# ─────────────────────────────────────────────────────────────

VERSIONS = [

    # ── v1: Baseline — small model, high LR, no augmentation tricks ──
    {
        "config": {
            "project": {"name": "yolo_detection", "version": "v1"},
            "dataset": {
                "name": "COCO-Vehicle-Detection",
                "version": "v1.0",
                "train_images": 45200,
                "val_images": 5120,
                "classes": 8,
            },
            "training": {
                "model":            "yolov8n",          # nano — fastest, lowest accuracy
                "epochs":           50,
                "batch_size":       16,
                "image_size":       640,
                "learning_rate":    0.01,
                "lr_final":         0.001,
                "optimizer":        "SGD",
                "momentum":         0.937,
                "weight_decay":     0.0005,
                "warmup_epochs":    3,
                "scheduler":        "cosine",
                "augment":          "basic",
                "mosaic":           True,
                "mixup":            False,
                "copy_paste":       False,
                "device":           "cuda",
                "num_workers":      8,
                "seed":             42,
                "mixed_precision":  True,
                "patience":         20,
                "save_best_only":   True,
            },
        },
        "metrics": {
            "mAP50":        0.412,
            "mAP50_95":     0.241,
            "precision":    0.538,
            "recall":       0.489,
            "f1_score":     0.512,
            "box_loss":     1.842,
            "cls_loss":     1.224,
            "dfl_loss":     1.103,
        },
        "artifacts": ["runs/detect/v1/weights/best.pt", "runs/detect/v1/results.csv",
                      "runs/detect/v1/confusion_matrix.png"],
        "status": "completed",
    },

    # ── v2: Upgrade model size + lower LR + add mixup ──
    {
        "config": {
            "project": {"name": "yolo_detection", "version": "v2"},
            "dataset": {
                "name": "COCO-Vehicle-Detection",
                "version": "v1.0",
                "train_images": 45200,
                "val_images": 5120,
                "classes": 8,
            },
            "training": {
                "model":            "yolov8s",          # small — better capacity
                "epochs":           80,
                "batch_size":       16,
                "image_size":       640,
                "learning_rate":    0.005,
                "lr_final":         0.0005,
                "optimizer":        "SGD",
                "momentum":         0.937,
                "weight_decay":     0.0005,
                "warmup_epochs":    5,
                "scheduler":        "cosine",
                "augment":          "medium",
                "mosaic":           True,
                "mixup":            True,
                "copy_paste":       False,
                "device":           "cuda",
                "num_workers":      8,
                "seed":             42,
                "mixed_precision":  True,
                "patience":         25,
                "save_best_only":   True,
            },
        },
        "metrics": {
            "mAP50":        0.563,
            "mAP50_95":     0.338,
            "precision":    0.641,
            "recall":       0.581,
            "f1_score":     0.609,
            "box_loss":     1.516,
            "cls_loss":     0.987,
            "dfl_loss":     0.981,
        },
        "artifacts": ["runs/detect/v2/weights/best.pt", "runs/detect/v2/results.csv",
                      "runs/detect/v2/confusion_matrix.png", "runs/detect/v2/PR_curve.png"],
        "status": "completed",
    },

    # ── v3: Larger image size + copy-paste + AdamW experiment (worse!) ──
    {
        "config": {
            "project": {"name": "yolo_detection", "version": "v3"},
            "dataset": {
                "name": "COCO-Vehicle-Detection",
                "version": "v1.1",          # dataset updated with more annotations
                "train_images": 52800,
                "val_images": 6200,
                "classes": 8,
            },
            "training": {
                "model":            "yolov8s",
                "epochs":           80,
                "batch_size":       8,              # smaller batch for 1280px
                "image_size":       1280,           # higher res — more detail
                "learning_rate":    0.001,          # AdamW needs lower LR
                "lr_final":         0.0001,
                "optimizer":        "AdamW",
                "weight_decay":     0.001,
                "warmup_epochs":    5,
                "scheduler":        "cosine",
                "augment":          "heavy",
                "mosaic":           True,
                "mixup":            True,
                "copy_paste":       True,
                "device":           "cuda",
                "num_workers":      8,
                "seed":             123,
                "mixed_precision":  True,
                "patience":         25,
                "save_best_only":   True,
            },
        },
        "metrics": {
            # Slightly worse — AdamW + huge batch caused instability
            "mAP50":        0.531,
            "mAP50_95":     0.318,
            "precision":    0.612,
            "recall":       0.553,
            "f1_score":     0.581,
            "box_loss":     1.634,
            "cls_loss":     1.045,
            "dfl_loss":     1.018,
        },
        "artifacts": ["runs/detect/v3/weights/best.pt", "runs/detect/v3/results.csv",
                      "runs/detect/v3/confusion_matrix.png"],
        "status": "completed",
    },

    # ── v4: Back to SGD + medium model + fine-tuned schedule — big jump ──
    {
        "config": {
            "project": {"name": "yolo_detection", "version": "v4"},
            "dataset": {
                "name": "COCO-Vehicle-Detection",
                "version": "v1.1",
                "train_images": 52800,
                "val_images": 6200,
                "classes": 8,
            },
            "training": {
                "model":            "yolov8m",          # medium — best so far
                "epochs":           120,
                "batch_size":       16,
                "image_size":       640,
                "learning_rate":    0.01,
                "lr_final":         0.0001,
                "optimizer":        "SGD",
                "momentum":         0.937,
                "weight_decay":     0.0005,
                "warmup_epochs":    5,
                "scheduler":        "one_cycle",
                "augment":          "heavy",
                "mosaic":           True,
                "mixup":            True,
                "copy_paste":       True,
                "label_smoothing":  0.1,
                "device":           "cuda",
                "num_workers":      8,
                "seed":             42,
                "mixed_precision":  True,
                "patience":         30,
                "save_best_only":   True,
            },
        },
        "metrics": {
            "mAP50":        0.724,
            "mAP50_95":     0.481,
            "precision":    0.783,
            "recall":       0.721,
            "f1_score":     0.751,
            "box_loss":     1.187,
            "cls_loss":     0.731,
            "dfl_loss":     0.844,
        },
        "artifacts": ["runs/detect/v4/weights/best.pt", "runs/detect/v4/weights/last.pt",
                      "runs/detect/v4/results.csv", "runs/detect/v4/confusion_matrix.png",
                      "runs/detect/v4/PR_curve.png", "runs/detect/v4/F1_curve.png"],
        "status": "completed",
    },

    # ── v5: Production — fine-tune v4 checkpoint + TTA + larger dataset ──
    {
        "config": {
            "project": {"name": "yolo_detection", "version": "v5"},
            "dataset": {
                "name": "COCO-Vehicle-Detection",
                "version": "v2.0",          # full re-labelled dataset
                "train_images": 78400,
                "val_images": 9800,
                "classes": 8,
            },
            "training": {
                "model":            "yolov8m",
                "epochs":           60,             # fine-tune only
                "batch_size":       16,
                "image_size":       640,
                "learning_rate":    0.001,          # lower LR for fine-tuning
                "lr_final":         0.00001,
                "optimizer":        "SGD",
                "momentum":         0.937,
                "weight_decay":     0.0005,
                "warmup_epochs":    2,
                "scheduler":        "cosine",
                "augment":          "heavy",
                "mosaic":           True,
                "mixup":            True,
                "copy_paste":       True,
                "label_smoothing":  0.05,
                "pretrained":       "yolo_detection_v4_best.pt",
                "tta":              True,           # test-time augmentation
                "device":           "cuda",
                "num_workers":      8,
                "seed":             42,
                "mixed_precision":  True,
                "patience":         15,
                "save_best_only":   True,
            },
        },
        "metrics": {
            "mAP50":        0.847,
            "mAP50_95":     0.592,
            "precision":    0.871,
            "recall":       0.823,
            "f1_score":     0.846,
            "box_loss":     0.923,
            "cls_loss":     0.541,
            "dfl_loss":     0.712,
        },
        "artifacts": ["runs/detect/v5/weights/best.pt", "runs/detect/v5/weights/last.pt",
                      "runs/detect/v5/results.csv", "runs/detect/v5/confusion_matrix.png",
                      "runs/detect/v5/PR_curve.png", "runs/detect/v5/F1_curve.png",
                      "runs/detect/v5/labels_correlogram.jpg", "runs/detect/v5/val_batch0_pred.jpg"],
        "status": "completed",
    },
]


# ─────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────

def run_version(ver: dict):
    cfg     = ver["config"]
    version = cfg["project"]["version"]
    print(f"\n{'='*60}")
    print(f"  Training  {cfg['project']['name']}  /  {version}")
    print(f"  Model     {cfg['training']['model']}")
    print(f"  Dataset   {cfg['dataset']['name']}  ({cfg['dataset']['train_images']:,} train images)")
    print(f"{'='*60}")

    try:
        benchmark.start(cfg)
        benchmark.log_metrics(ver["metrics"])
        for art in ver["artifacts"]:
            benchmark.log_artifact(art)
        benchmark.finish()
        print(f"✅  {version} — COMPLETED   mAP50={ver['metrics']['mAP50']:.3f}")

    except KeyboardInterrupt:
        benchmark.cancel()
        print(f"⚠️   {version} — CANCELLED by user")
        raise

    except Exception as e:
        benchmark.fail()
        print(f"❌  {version} — FAILED: {e}")
        raise


def main():
    print("\n🚀  YOLO Detection — Full Versioning Lifecycle")
    print(f"    Registering {len(VERSIONS)} training runs...\n")

    for i, ver in enumerate(VERSIONS):
        run_version(ver)
        # Small pause between runs so DB transactions settle
        if i < len(VERSIONS) - 1:
            time.sleep(0.5)

    print(f"\n🎉  All {len(VERSIONS)} versions registered successfully!")
    print("    Open the dashboard to explore Analytics & Compare.")


if __name__ == "__main__":
    main()
