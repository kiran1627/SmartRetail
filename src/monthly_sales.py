# src/monthly_sales.py
import pandas as pd
import os

MONTHLY_PATH = os.path.join("data", "processed", "monthly_sales.csv")

def generate_monthly_sales(df):
    monthly = df.groupby(
        ["Order Year", "Order Month", "Category"], as_index=False
    )["Sales"].sum()

    os.makedirs(os.path.dirname(MONTHLY_PATH), exist_ok=True)
    monthly.to_csv(MONTHLY_PATH, index=False)
    print("✅ monthly_sales.csv saved.")
    return monthly
