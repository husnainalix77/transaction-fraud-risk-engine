import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

def downcast_dataframe(df):
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer") 
    return df

def load_csv_to_mysql(csv_path, table_name, chunk_size=20000):
    
    first_chunk = True
    total_rows = 0
    
    for chunk in pd.read_csv(csv_path, chunksize=chunk_size):
        chunk = downcast_dataframe(chunk)
        chunk.to_sql(
            table_name,
            engine,
            if_exists="replace" if first_chunk else "append",
            index=False    
        ) 
        
        total_rows += len(chunk)
        print(f"{table_name} : loaded {total_rows} rows so far...")
        first_chunk = False
        
    print(f"Done. {table_name} total rows loaded: {total_rows}")

if __name__ == "__main__":
    load_csv_to_mysql("data/raw/train_transaction.csv", "raw_transactions")
    load_csv_to_mysql("data/raw/train_identity.csv", "raw_identity")    
              

