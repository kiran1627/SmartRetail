# src/rfm_segmentation.py
import pandas as pd
import os

RFM_PATH = os.path.join("data", "processed", "rfm_scores.csv")

def generate_rfm_scores(df):
    latest_date = df["Order Date"].max()
    rfm = df.groupby("Customer ID").agg({
        "Order Date": lambda x: (latest_date - x.max()).days,  # Recency
        "Order ID": "nunique",  # Frequency
        "Sales": "sum"          # Monetary
    }).reset_index()

    rfm.columns = ["Customer ID", "Recency", "Frequency", "Monetary"]
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5,4,3,2,1]).astype(int)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1,2,3,4,5]).astype(int)
    rfm["RFM_Score"] = rfm["R_Score"] + rfm["F_Score"] + rfm["M_Score"]

    os.makedirs(os.path.dirname(RFM_PATH), exist_ok=True)
    rfm.to_csv(RFM_PATH, index=False)
    print("✅ rfm_scores.csv saved.")
    return rfm
