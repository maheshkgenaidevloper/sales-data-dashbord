
import pandas as pd

# 1. Load the CSV file
df = pd.read_csv("sample_sales_data.csv")

# 2. Convert the date column
df["Order_Date"] = pd.to_datetime(
    df["Order_Date"], errors="coerce"
)

# 3. Convert numerical columns
numeric_columns = [
    "Sales", "Quantity", "Discount", "Profit"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 4. Remove duplicate orders
df = df.drop_duplicates(subset=["Order_ID"])

# 5. Remove records missing essential values
df = df.dropna(
    subset=["Order_ID", "Order_Date", "Sales", "Profit"]
)

# 6. Create useful analysis columns
df["Year"] = df["Order_Date"].dt.year
df["Month"] = df["Order_Date"].dt.month
df["YearMonth"] = df["Order_Date"].dt.to_period("M").astype(str)

df["Profit_Margin"] = (
    df["Profit"] / df["Sales"].replace(0, float("nan"))
)

# 7. Save cleaned data
df.to_csv("cleaned_sales_data.csv", index=False)

# 8. Display summary
print("Dataset shape:", df.shape)
print("\nFirst five records:")
print(df.head())

print("\nTotal sales:", df["Sales"].sum())
print("Total profit:", df["Profit"].sum())
print("Total orders:", df["Order_ID"].nunique())

print("\nData cleaning completed!")