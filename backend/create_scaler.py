# create_scaler.py
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

CSV_FILE = "historical_stock_data.csv"

if not os.path.exists(CSV_FILE):
    print(f"❌ CSV file not found: {CSV_FILE}")
    exit(1)

# Load CSV normally (keep first row as header)
df = pd.read_csv(CSV_FILE)

# Drop the first two rows (Ticker row and empty Date row)
df = df.drop([1, 2], axis=0)  # pandas uses 0-based index

# Ensure 'Close' column exists
if 'Close' not in df.columns:
    print("❌ CSV must have a 'Close' column.")
    exit(1)

# Convert 'Close' to numeric
prices = pd.to_numeric(df['Close'], errors='coerce').dropna().values.reshape(-1, 1)

if len(prices) == 0:
    print("❌ No valid numeric 'Close' data found.")
    exit(1)

# Fit scaler and save
scaler = MinMaxScaler()
scaler.fit(prices)
joblib.dump(scaler, "scaler.pkl")
print("✅ Scaler saved successfully as 'scaler.pkl'.")
