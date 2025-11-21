# monthly.py
import streamlit as st
import pandas as pd
import os 
from datetime import datetime, timedelta

st.title("📅 Monthly Overview")


# ---------- CSV FILE SETUP ----------
csv_file = os.path.join("data", "add_expense.csv")

# Load data from CSV or create a new DataFrame
def load_data():
    try:
        df = pd.read_csv(csv_file)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")  # force datetime conversion
        df = df.dropna(subset=["Date"])  # remove invalid date rows
        return df
        # return pd.read_csv(csv_file, parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Description"])

def save_data(df):
    df.to_csv(csv_file, index=False)

df_data = load_data()
df_data = df_data.dropna(subset=["Date"]) 
# if not df_data.empty:
#     st.text("No transactions")
if df_data.empty or "Date" not in df_data:
    st.warning("No data available")
    st.stop()

# ----------- SELECT YEAR ------------
df_data["Date"] = pd.to_datetime(df_data["Date"], errors="coerce")

years_available = df_data["Date"].dt.year.unique()
selected_year = st.selectbox("📅 Select Year for Monthly Summary", sorted(years_available, reverse=True))

# Filter data for selected year
year_data = df_data[df_data["Date"].dt.year == selected_year]
year_data["Month"] = year_data["Date"].dt.month_name()

# ----------- MONTHLY DISPLAY CARDS ------------
st.subheader(f"Monthly Summary Cards for {selected_year}")

month_order = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

card_style = """
<style>
.card {
    background-color: #1e1e1e;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    margin: 10px 5px;
    text-align: center;
    border: 1px solid #333;
}
.card-title {
    font-weight: 600;
    font-size: 18px;
    margin-bottom: 10px;
    color: #4da3ff;
}
.card-value {
    font-size: 16px;
    margin: 2px 0;
    color: #e0e0e0;
}
</style>
"""

st.markdown(card_style, unsafe_allow_html=True)

for i in range(0, 12, 3):  # Show in 3-column layout
    cols = st.columns(3)
    for j in range(3):
        if i + j < 12:
            month = month_order[i + j]
            month_df = year_data[year_data["Month"] == month]
            budget = month_df[month_df["Type"] == "Budget"]["Amount"].sum()
            expense = month_df[month_df["Type"] == "Expense"]["Amount"].sum()
            net = budget - expense

            card_html = f"""
                <div class='card'>
                    <div class='card-title'>📅 {month}</div>
                    <div class='card-value'>💵 Budget: KSH {budget:,.2f}</div>
                    <div class='card-value'>💸 Expense: KSH {expense:,.2f}</div>
                    <div class='card-value'>💰 Balance: KSH {net:,.2f}</div>
                </div>
            """
            cols[j].markdown(card_html, unsafe_allow_html=True)
