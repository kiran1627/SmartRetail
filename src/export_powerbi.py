# src/export_powerbi.py
import pandas as pd
import os

CLEAN_PATH = os.path.join("data", "processed", "cleaned_sales.csv")
MONTHLY_PATH = os.path.join("data", "processed", "monthly_sales.csv")
RFM_PATH = os.path.join("data", "processed", "rfm_scores.csv")
FORECAST_PATH = os.path.join("data", "processed", "sales_forecast.csv")
EXPORT_PATH = os.path.join("data", "processed", "powerbi_dataset.csv")

def export_powerbi_data():
    df_clean = pd.read_csv(CLEAN_PATH)
    df_monthly = pd.read_csv(MONTHLY_PATH)
    df_rfm = pd.read_csv(RFM_PATH)
    df_forecast = pd.read_csv(FORECAST_PATH)

    # Merge summary
    powerbi_data = df_clean.merge(df_rfm, on="Customer ID", how="left")

    os.makedirs(os.path.dirname(EXPORT_PATH), exist_ok=True)
    powerbi_data.to_csv(EXPORT_PATH, index=False)
    print("✅ powerbi_dataset.csv saved.")
    return powerbi_data
