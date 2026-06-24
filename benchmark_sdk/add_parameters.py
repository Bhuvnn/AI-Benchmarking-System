from backend.models.create_engine import engine
from sqlalchemy import text



def extract_parameters(run_id,config):
    rows=[]
    print(f"📖 Extracting parameters from config['training']:")
    for key,value in config["training"].items():
        print(f"  - Parameter: {key} = {value}")
        rows.append(
            {
                "run_id":run_id,
                "parameter_name":key,
                "parameter_value":str(value)
            }
        )
    print(f"✅ Extracted {len(rows)} parameters.")
    return rows


def add_parameters_to_database(rows):
    if not rows:
        print("⚠️ No parameters to write to database.")
        return
    print(f"💾 Inserting {len(rows)} parameter records into PostgreSQL 'parameters' table...")
    with engine.begin() as conn:
        conn.execute(text(
            """INSERT INTO parameters (run_id, parameter_name, parameter_value)
                VALUES (:run_id, :parameter_name, :parameter_value);
            """
        ),
        rows
        )
    print("✅ Parameter rows successfully written to database.")
