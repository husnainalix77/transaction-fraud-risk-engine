import pandas as pd

transaction_df = pd.read_csv("data/raw/train_transaction.csv")
identity_df = pd.read_csv("data/raw/train_identity.csv")

print("=== train_transaction.csv ===")
print(f"Rows: {transaction_df.shape[0]}")
print(f"Columns: {transaction_df.shape[1]}")
print(transaction_df.head(3))

print("\n=== train_identity.csv ===")
print(f"Rows: {identity_df.shape[0]}")
print(f"Columns: {identity_df.shape[1]}")
print(identity_df.head(3))
