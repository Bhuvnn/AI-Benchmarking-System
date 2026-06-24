from benchmark_sdk.add_project import add_project_to_database
from benchmark_sdk.add_parameters import extract_parameters,add_parameters_to_database
from benchmark_sdk.add_metrics import extract_metrics, add_metrics_to_database
from benchmark_sdk.add_artifacts import identify_artifact_type,add_artifacts_to_database
from benchmark_sdk.status_upadate import update_status
from benchmark_sdk.add_system_info import log_system_info
from benchmark_sdk.add_dataset_info import log_dataset_info

_run_id=None

def start(config):
    global _run_id
    print("🚀 Starting benchmark run registration...")
    if _run_id is not None:
        raise RuntimeError(
            "A benchmark run is already active. Call benchmark.finish(), benchmark.fail(), or benchmark.cancel() first."
        )
    try:
        _run_id=add_project_to_database(config)
        if _run_id is None:
            raise ValueError("Failed to create or retrieve run_id")
        
        log_system_info(_run_id)
        log_dataset_info(_run_id, config)
        
        print(f"📋 Extracting training parameters for run ID: {_run_id}")
        rows=extract_parameters(_run_id,config)
        print(f"💾 Saving {len(rows)} parameters to database...")
        add_parameters_to_database(rows)
        print("✅ Run setup and parameter logging completed successfully.")
    except Exception as e:
        print(f"❌ An unexpected Error occurred during start: {e}")
        raise

    return _run_id

def log_metrics(metrics):
    print(f"📊 Logging metrics for run ID: {_run_id}...")
    try:
        if _run_id is None:
            raise ValueError("No active run found. Call benchmark.start() first.")
        rows=extract_metrics(_run_id,metrics)
        print(f"💾 Saving {len(rows)} metrics to database...")
        add_metrics_to_database(rows)
        print("✅ Metrics logged successfully.")
    
    except Exception as e:
        print(f"❌ An unexpected Error occurred during log_metrics: {e}")
        raise

def log_artifact(file_path):
    if _run_id is None:
        raise ValueError("No active run found. Call benchmark.start() first.") 
    try:
        artifact_type=identify_artifact_type(file_path)
        add_artifacts_to_database(_run_id,file_path,artifact_type)
    except Exception as e:
        print(f"❌ An unexpected Error occurred during log_artifact: {e}")
        raise



def finish():
    global _run_id
    if _run_id==None:
        return
    update_status(_run_id,"Completed")
    _run_id = None

def fail():
    global _run_id
    if _run_id==None:
        return
    update_status(_run_id,"Failed")
    _run_id = None

def cancel():
    global _run_id
    if _run_id==None:
        return
    update_status(_run_id,"Cancelled")
    _run_id = None