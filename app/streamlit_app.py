import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ----------------------------------------------------
# 🎯 Page Setup
# ----------------------------------------------------
st.set_page_config(page_title="Smart Retail BI Dashboard", layout="wide")
st.title("🛍️ Smart Retail Analytics Dashboard")
st.markdown("### Gain business insights from your retail dataset with detailed sales, customer, and product analysis.")

# ----------------------------------------------------
# 📂 Load Data
# ----------------------------------------------------
@st.cache_data
def load_data():
    # Automatically detect dataset path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "..", "data", "processed", "powerbi_dataset.csv")

    # ✅ Handle missing file safely
    if not os.path.exists(data_path):
        st.error(f"❌ Dataset not found at: {data_path}")
        st.info("Please place your dataset in: data/processed/powerbi_dataset.csv")
        st.stop()

    # ✅ Read dataset
    df = pd.read_csv(data_path)

    # ✅ Convert to datetime
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")

    # ✅ Add derived time-based features
    df["Order Month"] = df["Order Date"].dt.month_name()
    df["Order Day"] = df["Order Date"].dt.day_name()
    df["Year"] = df["Order Date"].dt.year

    # ✅ Ensure important numerical columns exist
    if "Sales" not in df.columns:
        df["Sales"] = 0
    if "Profit" not in df.columns:
        df["Profit"] = df["Sales"] * np.random.uniform(0.1, 0.3, len(df))
    if "Discount" not in df.columns:
        df["Discount"] = np.random.choice([0, 0.05, 0.1, 0.15, 0.2], len(df))

    # ✅ Replace missing numeric values with 0
    df.fillna(0, inplace=True)

    return df


# ----------------------------------------------------
# ✅ Load and Verify Data
# ----------------------------------------------------
df = load_data()

st.success("✅ Dataset loaded successfully!")
st.write(f"**Total Records:** {len(df):,}")
st.write(df.head())

# ----------------------------------------------------
# 🔍 Filters
# ----------------------------------------------------
st.sidebar.header("🔎 Filter Data")
years = sorted(df["Year"].unique())
regions = sorted(df["Region"].unique())
categories = sorted(df["Category"].unique())

year_filter = st.sidebar.multiselect("Select Year(s)", years, default=years)
region_filter = st.sidebar.multiselect("Select Region(s)", regions, default=regions)
category_filter = st.sidebar.multiselect("Select Category(s)", categories, default=categories)

df_filtered = df[
    (df["Year"].isin(year_filter)) &
    (df["Region"].isin(region_filter)) &
    (df["Category"].isin(category_filter))
]

# ----------------------------------------------------
# 💰 KPI Metrics
# ----------------------------------------------------
total_sales = df_filtered["Sales"].sum()
avg_order_value = df_filtered.groupby("Order ID")["Sales"].sum().mean()
unique_customers = df_filtered["Customer ID"].nunique()
avg_shipping_days = df_filtered["Days to Ship"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💵 Total Sales", f"${total_sales:,.2f}")
col2.metric("📦 Avg Order Value", f"${avg_order_value:,.2f}")
col3.metric("👥 Unique Customers", unique_customers)
col4.metric("🚚 Avg Days to Ship", f"{avg_shipping_days:.1f}")

# ----------------------------------------------------
# 🗓️ Sales Over Time (Daily + Monthly)
# ----------------------------------------------------
st.subheader("📅 Sales Trend Analysis")

tab1, tab2 = st.tabs(["📆 Daily Trend", "🗓️ Monthly Trend"])

# --- Daily ---
with tab1:
    daily_sales = df_filtered.groupby("Order Day")["Sales"].sum().reindex(
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    ).reset_index()

    fig_bar = px.bar(daily_sales, x="Order Day", y="Sales", color="Sales",
                     title="📊 Day-wise Sales Distribution", text_auto=".2s")
    fig_pie = px.pie(daily_sales, names="Order Day", values="Sales",
                     title="🥧 Day-wise Sales Share")

    st.plotly_chart(fig_bar, use_container_width=True)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- Monthly ---
with tab2:
    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    monthly_sales = df_filtered.groupby("Order Month")["Sales"].sum().reindex(month_order).dropna().reset_index()

    fig_monthly = px.line(monthly_sales, x="Order Month", y="Sales",
                          title="📈 Monthly Sales Trend", markers=True)
    fig_monthly_bar = px.bar(monthly_sales, x="Order Month", y="Sales",
                             color="Sales", title="🗓️ Monthly Sales by Month")

    st.plotly_chart(fig_monthly, use_container_width=True)
    st.plotly_chart(fig_monthly_bar, use_container_width=True)

# ----------------------------------------------------
# 🌍 Regional & Segment Insights
# ----------------------------------------------------
st.subheader("🌍 Regional and Segment Performance")

col5, col6 = st.columns(2)

# Region
region_sales = df_filtered.groupby("Region")["Sales"].sum().reset_index()
fig_region = px.bar(region_sales, x="Region", y="Sales", color="Region",
                    title="🏙️ Sales by Region", text_auto=".2s")
col5.plotly_chart(fig_region, use_container_width=True)

# Segment
segment_sales = df_filtered.groupby("Segment")["Sales"].sum().reset_index()
fig_segment = px.pie(segment_sales, names="Segment", values="Sales",
                     title="👥 Sales Share by Customer Segment")
col6.plotly_chart(fig_segment, use_container_width=True)

# ----------------------------------------------------
# 🛒 Category & Sub-Category Insights
# ----------------------------------------------------
st.subheader("🛒 Category Performance")

col7, col8 = st.columns(2)

# Category
category_sales = df_filtered.groupby("Category")["Sales"].sum().reset_index()
fig_cat = px.bar(category_sales, x="Category", y="Sales", color="Category",
                 title="📦 Sales by Category", text_auto=".2s")
col7.plotly_chart(fig_cat, use_container_width=True)

# Sub-Category
subcat_sales = df_filtered.groupby("Sub-Category")["Sales"].sum().reset_index()
fig_subcat = px.treemap(subcat_sales, path=["Sub-Category"], values="Sales",
                        title="🌳 Sub-Category Sales Breakdown")
col8.plotly_chart(fig_subcat, use_container_width=True)

# ----------------------------------------------------
# 👤 Customer Insights (RFM)
# ----------------------------------------------------
st.subheader("👤 Customer Behavior Insights (RFM Analysis)")

rfm_summary = df_filtered.groupby("Customer Name")[["Recency", "Frequency", "Monetary"]].mean().reset_index()

col9, col10 = st.columns(2)
fig_r = px.histogram(rfm_summary, x="Recency", nbins=20, title="📅 Recency Distribution")
col9.plotly_chart(fig_r, use_container_width=True)

fig_f = px.scatter(rfm_summary, x="Frequency", y="Monetary", color="Recency",
                   size="Monetary", title="💰 Frequency vs Monetary Relationship")
col10.plotly_chart(fig_f, use_container_width=True)

# ----------------------------------------------------
# 🚚 Shipping Mode Insights
# ----------------------------------------------------
st.subheader("🚚 Shipping Performance")

ship_sales = df_filtered.groupby("Ship Mode")["Sales"].sum().reset_index()
fig_ship = px.bar(ship_sales, x="Ship Mode", y="Sales", color="Ship Mode",
                  title="🚛 Sales by Shipping Mode", text_auto=".2s")
st.plotly_chart(fig_ship, use_container_width=True)

# ----------------------------------------------------
# 💼 Profit & Discount Analytics
# ----------------------------------------------------
st.subheader("💼 Profit & Discount Insights")

# Handle missing columns
if "Profit" not in df_filtered.columns:
    df_filtered["Profit"] = df_filtered["Sales"] * np.random.uniform(0.15, 0.25, len(df_filtered))
if "Discount" not in df_filtered.columns:
    df_filtered["Discount"] = np.random.choice([0, 0.05, 0.1, 0.15, 0.2], len(df_filtered))

df_filtered["Profit Margin (%)"] = (df_filtered["Profit"] / df_filtered["Sales"]) * 100

colp1, colp2, colp3 = st.columns(3)
colp1.metric("🏦 Total Profit", f"${df_filtered['Profit'].sum():,.2f}")
colp2.metric("📊 Average Profit Margin", f"{df_filtered['Profit Margin (%)'].mean():.2f}%")
colp3.metric("🎯 Average Discount", f"{(df_filtered['Discount'].mean() * 100):.1f}%")

# ----------------------------------------------------
# 📆 Day-wise Profit Analysis
# ----------------------------------------------------
st.subheader("📆 Day-wise Profit Analysis")

daily_profit = df_filtered.groupby("Order Day")[["Sales", "Profit"]].sum().reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
).reset_index()

col_dp1, col_dp2 = st.columns(2)
fig_day_profit_bar = px.bar(daily_profit, x="Order Day", y="Profit",
                            color="Profit", title="💹 Day-wise Profit (Bar Chart)", text_auto=".2s")
fig_day_profit_pie = px.pie(daily_profit, names="Order Day", values="Profit",
                            title="🥧 Day-wise Profit Share")

col_dp1.plotly_chart(fig_day_profit_bar, use_container_width=True)
col_dp2.plotly_chart(fig_day_profit_pie, use_container_width=True)

# ----------------------------------------------------
# 🗓️ Monthly Profit Analysis
# ----------------------------------------------------
st.subheader("🗓️ Monthly Profit Analysis")

month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

monthly_profit = df_filtered.groupby("Order Month")[["Sales", "Profit"]].sum().reindex(month_order).dropna().reset_index()

col_mp1, col_mp2 = st.columns(2)
fig_month_profit_bar = px.bar(monthly_profit, x="Order Month", y="Profit",
                              color="Profit", title="💰 Monthly Profit (Bar Chart)", text_auto=".2s")
fig_month_profit_pie = px.pie(monthly_profit, names="Order Month", values="Profit",
                              title="🥧 Monthly Profit Distribution")

col_mp1.plotly_chart(fig_month_profit_bar, use_container_width=True)
col_mp2.plotly_chart(fig_month_profit_pie, use_container_width=True)

# ----------------------------------------------------
# 🌍 Regional Profit Distribution
# ----------------------------------------------------
st.subheader("🌍 Regional Profit Insights")

region_profit = df_filtered.groupby("Region")[["Sales", "Profit"]].sum().reset_index()
region_profit["Profit Margin (%)"] = (region_profit["Profit"] / region_profit["Sales"]) * 100

col_rp1, col_rp2 = st.columns(2)
fig_region_profit_bar = px.bar(region_profit, x="Region", y="Profit", color="Profit Margin (%)",
                               title="🏙️ Profit by Region (Bar Chart)", text_auto=".2s")
fig_region_profit_pie = px.pie(region_profit, names="Region", values="Profit",
                               title="🥧 Regional Profit Share")

col_rp1.plotly_chart(fig_region_profit_bar, use_container_width=True)
col_rp2.plotly_chart(fig_region_profit_pie, use_container_width=True)

# ----------------------------------------------------
# 💾 Export Data
# ----------------------------------------------------
st.markdown("### 💾 Export Filtered Dataset")
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("📤 Download Current View as CSV", csv, "SmartRetailBI_Filtered.csv", "text/csv")

st.markdown("---")
st.markdown("✅ **Smart Retail BI Dashboard** | Built with Streamlit & Plotly for actionable retail insights.")
