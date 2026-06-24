# AI Benchmarking System Architecture

## Overview

This project is split into three main layers:

1. `sample_project` is the example consumer application.
2. `benchmark_sdk` is the SDK entry point used by the consumer.
3. `backend` contains database models and operations that persist projects and runs.

The current codebase is centered around one core flow: given a project name, version, and training config, the SDK initializes the database, checks whether the project already exists, creates it if needed, creates a run/version record for that project, and then stores training parameters for that run.

### Current State

As of now, the project is a functional backend-enabled system with project registration, parameter logging, and metrics ingestion working end-to-end.

What is working:

- A sample consumer can call the SDK entry point through `sample_project/train.py`.
- The SDK initializes the database, looks up a project by name, creates it if missing, and creates a run/version record.
- Training parameters are extracted from the config and inserted into the `parameters` table.
- Metrics are extracted from the consumer script and inserted into the `metrics` table after the run is created.
- PostgreSQL-backed table helpers exist for `projects`, `runs`, `metrics`, `parameters`, `system_info`, and `dataset_info`.
- Comprehensive console prints/logs are generated indicating progress and database operations.

What is partially wired:

- The SDK has placeholder modules for parser and tracker functionality, but they are not yet implemented.
- `benchmark_sdk/ingest.py` exists, but the current runtime path does not use it yet.

What is not present yet:

- A richer API or service layer beyond the current direct SQL operations.

In short, the project registration, run creation, parameter logging, and metrics ingestion are now fully implemented and wired together, while the tracker and parser abstractions remain as future extensions.

## High-Level Structure

```text
sample_project
  -> benchmark_sdk.benchmark.start(config)
      -> backend.models.initialize.initialize_database()
      -> backend.operations.create_runs.get_project_id(project_name)
      -> backend.operations.create_project.project_creation(project_name)
      -> backend.operations.create_runs.runs_creation(project_id, version_name)
      -> benchmark_sdk.add_system_info.log_system_info(run_id)
      -> benchmark_sdk.add_dataset_info.log_dataset_info(run_id, config)
      -> benchmark_sdk.add_parameters.extract_parameters(run_id, config)
      -> benchmark_sdk.add_parameters.add_parameters_to_database(rows)
          -> backend.models.create_engine.engine
  -> benchmark_sdk.benchmark.log_metrics(metrics)
      -> benchmark_sdk.add_metrics.extract_metrics(run_id, metrics)
      -> benchmark_sdk.add_metrics.add_metrics_to_database(rows)
          -> backend.models.create_engine.engine

backend.models
  -> defines PostgreSQL connection and table creation helpers

backend.operations
  -> defines the database write/read actions used by the SDK
```

## Repository Modules

### `sample_project`

#### `sample_project/config.py`

Defines the runtime config passed into the SDK.

Current shape:

```python
CONFIG = {
    "project": {
        "name": "ai_India",
        "version": "v1"
    }
}
```

#### `sample_project/train.py`

This is the consumer entry point. It imports the SDK, starts the benchmark registration flow, and logs training metrics.

Call flow:

```python
from benchmark_sdk import benchmark
from sample_project.config import CONFIG

benchmark.start(CONFIG)

metrics = {
    "mAP": 0.92,
    "recall": 0.75,
    "Precision": 0.77
}
benchmark.log_metrics(metrics)
```

### `benchmark_sdk`

#### `benchmark_sdk/__init__.py`

Exports the `benchmark` module so the consumer can import:

```python
from benchmark_sdk import benchmark
```

#### `benchmark_sdk/benchmark.py`

This is the main SDK orchestration module.

Functions:

```python
def start(config):
def log_metrics(metrics):
```

Responsibilities:

1. Call `add_project_to_database(config)` to initialize the schema, check/create project, and create a run.
2. Store the returned `run_id` globally.
3. Extract parameters from `config["training"]` and insert them into the database.
4. Provide `log_metrics(metrics)` to allow consumers to post-run log performance metrics linked to the active `run_id`.

Detailed flow:

```python
run_id = add_project_to_database(config)
rows = extract_parameters(run_id, config)
add_parameters_to_database(rows)
# ... Later ...
metrics_rows = extract_metrics(run_id, metrics)
add_metrics_to_database(metrics_rows)
```

#### `benchmark_sdk/parser.py`

Present in the repository, but currently no implementation is visible in the codebase.

#### `benchmark_sdk/ingest.py`

Present in the repository, but currently no implementation is visible in the codebase.

#### `benchmark_sdk/tracker.py`

Present in the repository, but currently no implementation is visible in the codebase.

#### `benchmark_sdk/add_project.py`

This module contains the project and run orchestration logic used by `benchmark.start()`.

Function:

```python
def add_project_to_database(config):
```

Behavior:

1. Reads `config["project"]`.
2. Calls `initialize_database()` to ensure tables exist.
3. Looks up the project using `get_project_id(project["name"])`.
4. Creates the project if it does not exist.
5. Creates a run/version record using `runs_creation(project_id, project["version"])`.
6. Prints status logs and returns the inserted run/version ID.

#### `benchmark_sdk/add_parameters.py`

This module transforms training config into database rows and inserts them.

Functions:

```python
def extract_parameters(run_id, config):
def add_parameters_to_database(rows):
```

Behavior:

- `extract_parameters()` loops through `config["training"]`.
- Each training entry becomes a row containing `run_id`, `parameter_name`, and `parameter_value`.
- `add_parameters_to_database()` inserts the rows into the `parameters` table using SQLAlchemy text commands with list inputs.

#### `benchmark_sdk/add_metrics.py`

This module transforms training metrics into database rows and inserts them.

Functions:

```python
def extract_metrics(run_id, metrics_dict):
def add_metrics_to_database(rows):
```

Behavior:

- `extract_metrics()` loops through the input metrics dictionary.
- Each metrics entry becomes a row containing `run_id`, `metric_name`, and `metric_value`.
- `add_metrics_to_database()` inserts the rows into the `metrics` table.

#### `benchmark_sdk/add_dataset_info.py`

This module extracts dataset configuration parameters and writes them to the database.

Functions:

```python
def log_dataset_info(run_id, config):
```

Behavior:

- Extracts the `dataset` dictionary from `config`.
- Reads `name`, `version`, `train_images`, `val_images`, and `classes`.
- Writes this dataset record to the `dataset_info` table linked to the current `run_id`.

## Backend Layer

### `backend/models/create_engine.py`

Defines the SQLAlchemy engine used by all backend database operations.

Current engine configuration:

```python
DATABASE_URL = "postgresql://postgres:thebhuvan007@localhost:5432/ai_benchmarking_system"
engine = create_engine(DATABASE_URL, echo=True)
```

Role in architecture:

- Centralized database connection object.
- Shared by all table creation helpers and CRUD-like operations.

### `backend/models/projects.py`

Defines the `projects` table schema and a helper to create the table if it does not exist.

Function:

```python
def create_projects_table():
```

Schema:

- `id SERIAL PRIMARY KEY`
- `project_name TEXT NOT NULL`
- `status TEXT NOT NULL DEFAULT 'active'`

### `backend/models/runs.py`

Defines the `runs` table schema.

Function:

```python
def create_runs_table():
```

Schema:

- `id SERIAL PRIMARY KEY`
- `project_id INTEGER NOT NULL`
- `version_name TEXT NOT NULL`
- `status TEXT NOT NULL`
- `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- Foreign key: `project_id` references `projects(id)`
- Unique constraint: `(project_id, version_name)`

### `backend/models/metrics.py`

Defines the `metrics` table schema.

Function:

```python
def create_metrics_table():
```

Schema:

- `id SERIAL PRIMARY KEY`
- `run_id INTEGER NOT NULL`
- `metric_name TEXT NOT NULL`
- `metric_value DOUBLE PRECISION NOT NULL`
- Foreign key: `run_id` references `runs(id)`

### `backend/models/parameters.py`

Defines the `parameters` table schema.

Function:

```python
def create_parameters_table():
```

Schema:

- `id SERIAL PRIMARY KEY`
- `run_id INTEGER NOT NULL`
- `parameter_name TEXT NOT NULL`
- `parameter_value TEXT NOT NULL`
- Foreign key: `run_id` references `runs(id)`

### `backend/models/create_system_info.py`

Defines the `system_info` table schema.

Function:

```python
def create_system_info_table():
```

Schema:

- `id SERIAL PRIMARY KEY`
- `run_id INTEGER NOT NULL`
- `os TEXT NOT NULL`
- `python_version TEXT NOT NULL`
- `gpu TEXT`
- Foreign key: `run_id` references `runs(id)`

### `backend/models/create_dataset_info.py`

Defines the `dataset_info` table schema.

Function:

```python
def create_dataset_info_table():
```

Schema:

- `id SERIAL PRIMARY KEY`
- `run_id INTEGER NOT NULL`
- `dataset_name TEXT NOT NULL`
- `dataset_version TEXT NOT NULL`
- `train_images INTEGER`
- `val_images INTEGER`
- `classes INTEGER`
- Foreign key: `run_id` references `runs(id)`

### `backend/models/initialize.py`

This module centralizes database setup.

Function:

```python
def initialize_database():
```

Behavior:

1. Creates the `projects` table.
2. Creates the `runs` table.
3. Creates the `parameters` table.
4. Creates the `metrics` table.
5. Creates the `artifacts` table.
6. Creates the `system_info` table.
7. Creates the `dataset_info` table.

This is the primary bootstrap hook used by the SDK before data writes begin.

## Backend Operations

### `backend/operations/create_project.py`

Contains the write operation used to create a new project row.

Function:

```python
def project_creation(project_name):
```

Behavior:

1. Opens a transaction with `engine.begin()`.
2. Inserts a row into `projects`.
3. Uses `RETURNING id` to fetch the new primary key.
4. Returns the inserted project ID with `result.scalar()`.

SQL intent:

```sql
INSERT INTO projects (project_name, status)
VALUES (:project_name, :status)
RETURNING id;
```

### `backend/operations/create_runs.py`

Contains the lookup and write operations for project versions/runs.

#### `get_project_id(project_name)`

Behavior:

1. Opens a transaction with `engine.begin()`.
2. Queries `projects` by `project_name`.
3. Returns the matching project ID, or `None` if not found.

SQL intent:

```sql
SELECT id FROM projects WHERE project_name = :project_name;
```

#### `runs_creation(project_id, runs_name)`

Behavior:

1. Opens a transaction with `engine.begin()`.
2. Inserts a row into `runs`.
3. Stores the run/version name and initial status ("In Progress").
4. Returns the inserted run ID with `result.scalar()`.

SQL intent:

```sql
INSERT INTO RUNS (project_id, version_name, status)
VALUES (:project_id, :version_name, :status)
RETURNING ID;
```

### `backend/operations/get_projects.py`
Retrieves all projects.
SQL:
```sql
SELECT id, project_name, status AS project_status FROM projects ORDER BY ID;
```

### `backend/operations/get_runs.py`
Retrieves all runs for a specific project.
SQL:
```sql
SELECT id, version_name, status, created_at, ended_at FROM runs WHERE project_id = :project_id ORDER BY created_at DESC;
```

### `backend/operations/get_parameters.py`
Retrieves all parameters for a specific run.
SQL:
```sql
SELECT id, parameter_name, parameter_value FROM parameters WHERE run_id = :run_id ORDER BY id;
```

### `backend/operations/get_metrics.py`
Retrieves all metrics for a specific run.
SQL:
```sql
SELECT id, metric_name, metric_value FROM metrics WHERE run_id = :run_id ORDER BY id;
```

### `backend/operations/get_artifacts.py`
Retrieves all artifacts for a specific run.
SQL:
```sql
SELECT id, artifact_path, artifact_type FROM artifacts WHERE run_id = :run_id ORDER BY id;
```

### `backend/operations/get_system_info.py`
Retrieves system info for a specific run.
SQL:
```sql
SELECT id, os, python_version, gpu FROM system_info WHERE run_id = :run_id;
```

### `backend/operations/get_dataset_info.py`
Retrieves dataset info for a specific run.
SQL:
```sql
SELECT id, dataset_name, dataset_version, train_images, val_images, classes FROM dataset_info WHERE run_id = :run_id;
```

## End-To-End Flow

Here is the complete runtime sequence for the current implementation.

1. `sample_project/train.py` imports `benchmark_sdk.benchmark`.
2. `sample_project/train.py` loads `CONFIG` from `sample_project/config.py`.
3. `benchmark.start(CONFIG)` is called.
4. `add_project_to_database(config)` is called.
5. `initialize_database()` creates or confirms the schema.
6. `get_project_id(project_name)` checks whether the project exists in `projects`.
7. If the project is missing, `project_creation(project_name)` inserts it and returns its ID.
8. `runs_creation(project_id, version_name)` inserts a new row into `runs` and returns the new `run_id`.
9. The run ID is returned to `benchmark.start()`, which sets the global `_run_id`.
10. `log_system_info(_run_id)` collects OS, Python version, and GPU info, and inserts a row into `system_info`.
11. `log_dataset_info(_run_id, config)` extracts the dataset configuration (name, version, train/val images, classes count) and inserts a row into `dataset_info`.
12. `extract_parameters(_run_id, config)` converts training config into parameter rows.
13. `add_parameters_to_database(rows)` inserts those parameter rows into `parameters`.
13. Later, the user calls `benchmark.log_metrics(metrics)` with a dictionary of metrics.
14. `extract_metrics(_run_id, metrics)` converts the metrics into database rows.
15. `add_metrics_to_database(metrics_rows)` inserts them into the `metrics` table.

## Database Relationships

The schema models a simple hierarchy:

```text
projects
  - id
  - project_name
  - status
      |
      | 1-to-many
      v
runs
  - id
  - project_id
  - version_name
  - status
  - created_at
      |
      | 1-to-many (to metrics, parameters, system_info, and dataset_info)
      v
metrics
  - id
  - run_id
  - metric_name
  - metric_value

parameters
  - id
  - run_id
  - parameter_name
  - parameter_value

system_info
  - id
  - run_id
  - os
  - python_version
  - gpu

dataset_info
  - id
  - run_id
  - dataset_name
  - dataset_version
  - train_images
  - val_images
  - classes
```

## Current Wiring Summary

### Active, used today

- `sample_project/train.py`
- `sample_project/config.py`
- `benchmark_sdk/benchmark.py`
- `benchmark_sdk/add_project.py`
- `benchmark_sdk/add_parameters.py`
- `benchmark_sdk/add_metrics.py`
- `benchmark_sdk/add_system_info.py`
- `benchmark_sdk/add_dataset_info.py`
- `backend/operations/create_project.py`
- `backend/operations/create_runs.py`
- `backend/operations/get_projects.py`
- `backend/operations/get_runs.py`
- `backend/operations/get_parameters.py`
- `backend/operations/get_metrics.py`
- `backend/operations/get_artifacts.py`
- `backend/operations/get_system_info.py`
- `backend/operations/get_dataset_info.py`
- `backend/models/create_engine.py`
- `backend/models/initialize.py`
- `backend/models/create_runs.py`
- `backend/models/create_metrics.py`
- `backend/models/create_parameters.py`
- `backend/models/create_system_info.py`
- `backend/models/create_dataset_info.py`

### Present but not yet wired into the runtime flow

- `benchmark_sdk/parser.py`
- `benchmark_sdk/ingest.py`
- `benchmark_sdk/tracker.py`

## Observations

1. The system now supports project/run registration, parameter registration, and metrics logging.
2. Table creation helper imports have no side effects, and all tables are cleanly created during `initialize_database()`.
3. The code assumes the database already exists and the PostgreSQL credentials are valid.
4. `runs_creation()` uses a unique `(project_id, version_name)` constraint to prevent duplicate versions per project.

## Suggested Next Architecture Additions

If you want this system to become a complete benchmark platform, the next likely layers are:

1. A tracker class/context manager that automatically records system metrics (CPU, RAM, GPU) during a run.
2. A parser that transforms model outputs or logs into structured rows.
3. A richer API or service layer (e.g., FastAPI web service) to interface with the database.
