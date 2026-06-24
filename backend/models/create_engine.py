from sqlalchemy import create_engine
DATABASE_URL = "postgresql://postgres:thebhuvan007@localhost:5432/ai_benchmarking_system"

engine = create_engine(DATABASE_URL,echo=True)



 