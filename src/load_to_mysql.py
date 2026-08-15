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

def downcast_dataframe(df)->list:
    """
    Reduce DataFrame memory usage by downcasting numeric columns
    to smaller compatible data types.

    Float64 columns are downcast to the smallest suitable float type,
    while int64 columns are downcast to the smallest suitable integer type.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame whose numeric columns will be downcast.

    Returns
    -------
    pandas.DataFrame
        The DataFrame with downcast numeric columns and reduced memory usage.
    """
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
        
    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer") 
        
    return df

def load_csv_to_mysql(csv_path, table_name, chunk_size=20000)-> None:
    """
    Load a CSV file into a MySQL table in chunks.

    The CSV file is read in batches to reduce memory usage. Each chunk
    is downcast to smaller numeric data types before being written to
    MySQL. The first chunk replaces any existing table, while subsequent
    chunks are appended to it.

    Parameters
    ----------
    csv_path : str
        Path to the CSV file to be loaded.
    table_name : str
        Name of the MySQL table where the data will be stored.
    chunk_size : int, default=20000
        Number of rows to read and insert into MySQL at a time.

    Returns
    -------
    None
        The function loads the data into MySQL and prints the loading
        progress and total number of rows inserted.
    """
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
              

