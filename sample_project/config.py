CONFIG = {
    "project": {
        "name": "ai_punjab",
        "version": "v2"
    },

    "dataset": {
        "name": "Road Defect Dataset",
        "version": "v1",
        "train_images": 28642,
        "val_images": 3284,
        "classes": 14
    },

    "training": {
        "epochs": 100,
        "batch_size": 16,
        "learning_rate": 0.001,
        "optimizer": "AdamW",
        "weight_decay": 0.0005,
        "momentum": 0.937,
        "image_size": 640,
        "num_workers": 8,
        "device": "cuda",
        "seed": 42,
        "mixed_precision": True,
        "patience": 20,
        "warmup_epochs": 3,
        "scheduler": "cosine",
        "save_best_only": True
    }
}
