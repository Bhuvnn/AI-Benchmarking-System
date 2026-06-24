from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from backend.operations.get_projects import get_projects
from backend.operations.get_runs import get_runs
from backend.operations.get_parameters import get_parameters
from backend.operations.get_metrics import get_metrics
from backend.operations.get_artifacts import get_artifacts
from backend.operations.get_dataset_info import get_dataset_info
from backend.operations.get_system_info import get_system_info 

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/projects")
def read_projects():
    try:
        projects = get_projects()
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
            )

@app.get("/projects/{project_id}/runs")
def read_runs(project_id: int):
    try:
        runs = get_runs(project_id)
        return {"runs": runs}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
            )
    
@app.get("/projects/{project_id}/runs/{run_id}/parameters")
def read_parameters(project_id: int, run_id: int):
    try:
        parameters = get_parameters(run_id)
        return {"parameters": parameters}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
            )

@app.get("/projects/{project_id}/runs/{run_id}/metrics")
def read_metrics(project_id: int, run_id: int):
    try:
        metrics = get_metrics(run_id)
        return {"metrics": metrics}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
            )

@app.get("/projects/{project_id}/runs/{run_id}/artifacts")
def read_artifacts(project_id: int, run_id: int):
    try:
        artifacts = get_artifacts(run_id)
        return {"artifacts": artifacts}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
            )

@app.get("/projects/{project_id}/runs/{run_id}/dataset_info")
def read_dataset_info(project_id: int, run_id: int):
    try:
        dataset_info = get_dataset_info(run_id)
        return {"dataset_info": dataset_info}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
            )

@app.get("/projects/{project_id}/runs/{run_id}/system_info")
def read_system_info(project_id: int, run_id: int):
    try:
        system_info = get_system_info(run_id)
        return {"system_info": system_info}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
            )
    
@app.get("/projects/{project_id}/compare")
def compare_runs(project_id: int):
    """Return all runs for a project with their metrics, parameters, system_info, and dataset_info."""
    try:
        runs = get_runs(project_id)
        comparison = []
        for run in runs:
            run_data = dict(run)
            run_data["metrics"] = [dict(m) for m in get_metrics(run["id"])]
            run_data["parameters"] = [dict(p) for p in get_parameters(run["id"])]
            si = get_system_info(run["id"])
            run_data["system_info"] = [dict(s) for s in si] if si else []
            di = get_dataset_info(run["id"])
            run_data["dataset_info"] = [dict(d) for d in di] if di else []
            comparison.append(run_data)
        return {"project_id": project_id, "runs": comparison}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
