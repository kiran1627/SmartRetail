# src/sales_forecast.py
import pandas as pd
from prophet import Prophet
import os

FORECAST_PATH = os.path.join("data", "processed", "sales_forecast.csv")

def generate_sales_forecast(monthly_df):
    df_forecast = monthly_df.copy()
    df_forecast["ds"] = pd.to_datetime(df_forecast["Order Year"].astype(str) + " " + df_forecast["Order Month"])
    df_forecast = df_forecast.groupby("ds", as_index=False)["Sales"].sum().rename(columns={"Sales": "y"})

    model = Prophet()
    model.fit(df_forecast)
    future = model.make_future_dataframe(periods=3, freq="M")
    forecast = model.predict(future)

    forecast_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    forecast_df.to_csv(FORECAST_PATH, index=False)
    print("✅ sales_forecast.csv saved.")
    return forecast_df
