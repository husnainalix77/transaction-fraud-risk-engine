import pandas as pd
df = pd.read_csv("data/processed/engineered_features.csv")
print(df.shape)
print(df.isnull().sum())
print(df.head())