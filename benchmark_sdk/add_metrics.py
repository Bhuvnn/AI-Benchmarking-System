from backend.models.create_engine import engine
from sqlalchemy import text

def extract_metrics(run_id,metrics_dict):
    rows=[]
    print(f"📖 Extracting metrics from dictionary:")
    for key,item in metrics_dict.items():
        print(f"  - Metric: {key} = {item}")
        rows.append(
            {
                "run_id":run_id,
                "metric_name":key,
                "metric_value":item
            }
        )
    print(f"✅ Extracted {len(rows)} metrics.")
    return rows

def add_metrics_to_database(rows):
    if not rows:
        print("⚠️ No metrics to write to database.")
        return
    print(f"💾 Inserting {len(rows)} metric records into PostgreSQL 'metrics' table...")
    with engine.begin() as conn:
        conn.execute(text(
            """INSERT INTO metrics (run_id, metric_name, metric_value)
                VALUES (:run_id, :metric_name, :metric_value);
            """
        ),
        rows
        )
    print("✅ Metric rows successfully written to database.")

