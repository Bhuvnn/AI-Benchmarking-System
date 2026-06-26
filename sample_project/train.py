from benchmark_sdk import benchmark

from sample_project.config import CONFIG
try:
    benchmark.start(CONFIG)
    
    metrics = {
        "accuracy": 0.85,
        "precision": 0.82,
        "recall": 0.79,
        "f1_score": 0.80,
        "auc_roc": 0.88,
        "loss": 0.45,
    }

    benchmark.log_metrics(metrics)
    benchmark.log_artifact("best.pt")
    benchmark.log_artifact("results.csv")
    benchmark.finish()

except KeyboardInterrupt:
    benchmark.cancel()
    print(f"Version: {CONFIG["project"]["version"]} from Project: {CONFIG["project"]["name"]} is Cancelled due to some Keyboard Interrupt")
    raise
except Exception as e:
    benchmark.fail()
    print(f"Version: {CONFIG["project"]["version"]} from Project: {CONFIG["project"]["name"]} is Failed")
    raise