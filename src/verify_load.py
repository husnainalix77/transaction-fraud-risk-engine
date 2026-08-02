import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

def check_row_counts(csv_path, table_name):
    csv_row_count = sum(1 for _ in open(csv_path, encoding="utf-8")) - 1

    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        mysql_row_count = result.scalar()

    print(f"\n--- Row Count Check: {table_name} ---")
    print(f"CSV rows: {csv_row_count}")
    print(f"MySQL rows: {mysql_row_count}")
    print("MATCH" if csv_row_count == mysql_row_count else "MISMATCH")

    return csv_row_count == mysql_row_count

def check_columns(csv_path, table_name):
    csv_columns = list(pd.read_csv(csv_path, nrows=0).columns)

    with engine.connect() as conn:
        result = conn.execute(text(f"SHOW COLUMNS FROM {table_name}"))
        mysql_columns = [row[0] for row in result]

    missing_in_mysql = set(csv_columns) - set(mysql_columns)
    extra_in_mysql = set(mysql_columns) - set(csv_columns)

    print(f"\n--- Column Check: {table_name} ---")
    print(f"CSV column count: {len(csv_columns)}")
    print(f"MySQL column count: {len(mysql_columns)}")

    if missing_in_mysql:
        print(f"Missing in MySQL: {missing_in_mysql}")
    if extra_in_mysql:
        print(f"Extra in MySQL: {extra_in_mysql}")
    if not missing_in_mysql and not extra_in_mysql:
        print("MATCH — all columns present")

    return not missing_in_mysql and not extra_in_mysql

def check_null_counts(csv_path, table_name, sample_cols=None):
    df = pd.read_csv(csv_path)
    csv_nulls = df.isnull().sum()

    if sample_cols:
        csv_nulls = csv_nulls[sample_cols]

    print(f"\n--- Null Count Check: {table_name} ---")
    mismatches = []

    with engine.connect() as conn:
        for col in csv_nulls.index:
            result = conn.execute(text(
                f"SELECT COUNT(*) FROM {table_name} WHERE `{col}` IS NULL"
            ))
            mysql_null_count = result.scalar()
            csv_null_count = csv_nulls[col]

            if mysql_null_count != csv_null_count:
                mismatches.append((col, csv_null_count, mysql_null_count))

    if mismatches:
        print(f"MISMATCHES FOUND ({len(mismatches)} columns):")
        for col, csv_n, mysql_n in mismatches:
            print(f"  {col}: CSV={csv_n}, MySQL={mysql_n}")
    else:
        print("MATCH — all checked columns have identical null counts")

    return len(mismatches) == 0

def spot_check_values(csv_path, table_name, id_column, sample_size=10):
    df = pd.read_csv(csv_path)
    sample_ids = df[id_column].sample(sample_size, random_state=42).tolist()

    print(f"\n--- Value Spot Check: {table_name} ---")
    mismatched_rows = []

    with engine.connect() as conn:
        for row_id in sample_ids:
            csv_row = df[df[id_column] == row_id].iloc[0]

            result = conn.execute(text(
                f"SELECT * FROM {table_name} WHERE `{id_column}` = {row_id}"
            ))
            mysql_row = result.mappings().first()

            if mysql_row is None:
                mismatched_rows.append((row_id, "MISSING IN MYSQL"))
                continue

            row_mismatches = []
            for col in df.columns:
                csv_val = csv_row[col]
                mysql_val = mysql_row[col]

                if pd.isna(csv_val) and mysql_val is None:
                    continue
                if pd.isna(csv_val) or mysql_val is None:
                    row_mismatches.append(col)
                    continue
                if str(csv_val) != str(mysql_val):
                    row_mismatches.append(col)

            if row_mismatches:
                mismatched_rows.append((row_id, row_mismatches))

    if mismatched_rows:
        print(f"MISMATCHES FOUND in {len(mismatched_rows)} rows:")
        for row_id, issue in mismatched_rows:
            print(f"  {id_column}={row_id}: {issue}")
    else:
        print(f"MATCH — all {sample_size} sampled rows identical across all columns")

    return len(mismatched_rows) == 0

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFYING: raw_transactions")
    print("=" * 60)
    check_row_counts("data/raw/train_transaction.csv", "raw_transactions")
    check_columns("data/raw/train_transaction.csv", "raw_transactions")
    check_null_counts(
        "data/raw/train_transaction.csv",
        "raw_transactions",
        sample_cols=["TransactionID", "isFraud", "TransactionAmt", "card1", "card2",
                     "card3", "card4", "card5", "card6", "addr1", "addr2",
                     "dist1", "dist2", "P_emaildomain", "R_emaildomain"]
    )
    spot_check_values("data/raw/train_transaction.csv", "raw_transactions", "TransactionID")
    print("=" * 60)
    print("VERIFYING: raw_identity")
    print("=" * 60)
    check_row_counts("data/raw/train_identity.csv", "raw_identity")
    check_columns("data/raw/train_identity.csv", "raw_identity")
    check_null_counts(
        "data/raw/train_identity.csv",
        "raw_identity",
        sample_cols=["TransactionID", "id_01", "id_02", "id_03", "id_04", "id_05",
                     "DeviceType", "DeviceInfo"]
    )
    spot_check_values("data/raw/train_identity.csv", "raw_identity", "TransactionID")