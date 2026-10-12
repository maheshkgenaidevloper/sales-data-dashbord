
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Sales Performance Dashboard")
st.caption("Python | Pandas | Plotly | Streamlit")

# Load the cleaned CSV if available
clean_file = Path("cleaned_sales_data.csv")
raw_file = Path("sample_sales_data.csv")
data_file = clean_file if clean_file.exists() else raw_file

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data["Order_Date"] = pd.to_datetime(data["Order_Date"])
    return data

df = load_data(str(data_file))

# Sidebar filters
st.sidebar.header("Dashboard Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique())
)

categories = st.sidebar.multiselect(
    "Select Category",
    sorted(df["Category"].dropna().unique()),
    default=sorted(df["Category"].dropna().unique())
)

segments = st.sidebar.multiselect(
    "Select Customer Segment",
    sorted(df["Segment"].dropna().unique()),
    default=sorted(df["Segment"].dropna().unique())
)

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(df["Order_Date"].min().date(),
           df["Order_Date"].max().date())
)

# Apply filters
filtered = df[
    df["Region"].isin(regions)
    & df["Category"].isin(categories)
    & df["Segment"].isin(segments)
].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start = pd.Timestamp(date_range[0])
    end = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)

    filtered = filtered[
        (filtered["Order_Date"] >= start)
        & (filtered["Order_Date"] < end)
    ]

if filtered.empty:
    st.warning("No records found. Change the filters.")
    st.stop()

# Calculate KPIs
sales = filtered["Sales"].sum()
profit = filtered["Profit"].sum()
orders = filtered["Order_ID"].nunique()
units = filtered["Quantity"].sum()
margin = profit / sales * 100 if sales else 0

# KPI cards
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Sales", f"₹{sales:,.0f}")
c2.metric("Total Profit", f"₹{profit:,.0f}")
c3.metric("Total Orders", f"{orders:,}")
c4.metric("Units Sold", f"{units:,}")
c5.metric("Profit Margin", f"{margin:.1f}%")

# Monthly trend
st.subheader("Monthly Sales Trend")

monthly = (
    filtered.assign(
        Month=filtered["Order_Date"].dt.to_period("M").astype(str)
    )
    .groupby("Month", as_index=False)
    .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
)

fig = px.line(
    monthly,
    x="Month",
    y=["Sales", "Profit"],
    markers=True,
    title="Monthly Sales and Profit"
)
st.plotly_chart(fig, use_container_width=True)

# Category and regional charts
left, right = st.columns(2)

with left:
    category_data = (
        filtered.groupby("Category", as_index=False)
        .agg(Sales=("Sales", "sum"))
    )
    fig = px.bar(
        category_data,
        x="Category",
        y="Sales",
        color="Category",
        title="Sales by Category"
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    region_data = (
        filtered.groupby("Region", as_index=False)
        .agg(Profit=("Profit", "sum"))
    )
    fig = px.bar(
        region_data,
        x="Region",
        y="Profit",
        color="Region",
        title="Profit by Region"
    )
    st.plotly_chart(fig, use_container_width=True)

# Payment analysis
st.subheader("Orders by Payment Mode")

payment_data = (
    filtered.groupby("Payment_Mode", as_index=False)
    .agg(Orders=("Order_ID", "nunique"))
)

fig = px.pie(
    payment_data,
    names="Payment_Mode",
    values="Orders",
    hole=0.4
)
st.plotly_chart(fig, use_container_width=True)

# Product table
st.subheader("Product Performance")

products = (
    filtered.groupby("Product", as_index=False)
    .agg(
        Sales=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum")
    )
    .sort_values("Sales", ascending=False)
)

st.dataframe(products, use_container_width=True)

# Export filtered records
st.download_button(
    "Download Filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_sales.csv",
    mime="text/csv"
)

st.success("Dashboard loaded successfully!")