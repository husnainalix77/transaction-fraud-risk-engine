import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

with open("sql/feature_engineering.sql", "r") as f:
    sql_text = f.read()

query = text(sql_text)

print("Running query — this may take a few minutes for 590,540 rows...")

with engine.connect() as conn:
    df = pd.read_sql(query, conn)

print(f"Query complete. Rows returned: {len(df)}")
print(f"Columns: {list(df.columns)}")

os.makedirs("data/processed", exist_ok=True)
output_path = "data/processed/engineered_features.csv"
df.to_csv(output_path, index=False)

print(f"Saved to {output_path}")