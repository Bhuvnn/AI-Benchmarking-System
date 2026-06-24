import sys
import platform
from backend.models.create_engine import engine
from sqlalchemy import text

def get_gpu_info():
    # Try using torch if installed
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except ImportError:
        pass
    
    # Try using subprocess to query nvidia-smi
    try:
        import subprocess
        out = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True)
        gpus = [line.strip() for line in out.strip().split("\n") if line.strip()]
        if gpus:
            return ", ".join(gpus)
    except Exception:
        pass
    return "CPU"

def collect_system_info():
    os_info = f"{platform.system()} {platform.release()}"
    py_version = platform.python_version()
    gpu_info = get_gpu_info()
    return {
        "os": os_info,
        "python_version": py_version,
        "gpu": gpu_info
    }

def log_system_info(run_id):
    print(f"🖥️ Gathering system info for run ID {run_id}...")
    info = collect_system_info()
    print(f"  - OS: {info['os']}")
    print(f"  - Python Version: {info['python_version']}")
    print(f"  - GPU: {info['gpu']}")
    
    print("💾 Saving system info to database...")
    with engine.begin() as conn:
        conn.execute(
            text(
                """INSERT INTO system_info (run_id, os, python_version, gpu)
                   VALUES (:run_id, :os, :python_version, :gpu);
                """
            ),
            {
                "run_id": run_id,
                "os": info["os"],
                "python_version": info["python_version"],
                "gpu": info["gpu"]
            }
        )
    print("✅ System info successfully written to database.")
