# src/data_cleaning.py
import pandas as pd
import os

RAW_PATH = os.path.join("data", "raw", "train.csv")
CLEANED_PATH = os.path.join("data", "processed", "cleaned_sales.csv")

def clean_sales_data():
    df = pd.read_csv(RAW_PATH)

    # Basic cleanup
    df = df.dropna(subset=["Sales"])
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

    # 🔹 Add a dummy profit calculation (for BI insights)
    # Adjust this logic based on your dataset structure.
    df["Profit"] = df["Sales"] * 0.15  # assume 15% margin for now

    os.makedirs(os.path.dirname(CLEANED_PATH), exist_ok=True)
    df.to_csv(CLEANED_PATH, index=False)
    print("✅ Cleaned sales data saved with Profit column.")
    return df
