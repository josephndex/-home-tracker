import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import plotly.express as px
import matplotlib.pyplot as plt
from pandas.errors import EmptyDataError
from config import DEVELOPER_NAME


# ---------- CSV FILE SETUP ----------

st.title("🏠 Madam Becky House Management Tracker")

st.markdown(f"👋 Welcome! Here's the household summary for **{datetime.today():%B %Y}**.")

col1,col2,col3 = st.columns([2,1,1])
with col1:
    st.markdown(
        "<div style='text-align:center;color:green;font-size:17px'>"
        "<i>"
        "Track household budget, kitchen expenses, and house needs all in one place."
        "</i>"
        "</div>",
        unsafe_allow_html=True)

with col2: 
    if st.button("➕ Add Expenses ",type="tertiary",use_container_width=True):
        st.switch_page("add_expense.py")

with col3:
    if st.button("📊 Check Reports",type="tertiary", use_container_width=True):
        st.switch_page("report.py")

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
    except (FileNotFoundError, EmptyDataError):
        return pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Description"])

# def save_data(df):
#     df.to_csv(csv_file, index=False)
df_data = load_data()

if df_data.empty:
    st.info("ℹ️ No transactions yet. Start by adding one.")
    # Display image only if it exists
    if os.path.exists("images/tracker.gif"):
        st.image("images/tracker.gif")
else:
    # ---------- SUMMARY METRICS ----------
    total_budget = df_data[df_data["Type"] == "Budget"]["Amount"].sum()
    total_expenses = df_data[df_data["Type"] == "Expense"]["Amount"].sum()
    balance_remaining = total_budget - total_expenses
    budget_ratio = balance_remaining / total_budget if total_budget != 0 else 0


    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Monthly Budget", f"KSH {total_budget:,.2f}")
    col2.metric("📭 Total Expenses", f"KSH {total_expenses:,.2f}")
    col3.metric("💰 Balance Remaining", f"KSH {balance_remaining:,.2f}")


    if budget_ratio < 0.2:
        st.warning("⚠️ Budget is running low! Over 80% has been spent. Please review expenses.")
    else:
        st.success("🎉 Great job! Budget management is on track this month.")

    col1,col2 = st.columns(2)
    # with col1:   
    #     st.markdown("##### 📄 Recent Transactions")
        
    #     st.dataframe(df_data.head(5))  # Replace with your recent transactions data
    with col1:   
        st.markdown("##### 📄 Recent Transactions")
        recent_df = df_data.copy()
        recent_df["Date"] = recent_df["Date"].dt.strftime("%d-%m-%Y")
        st.dataframe(recent_df.head(5), hide_index=True)
    with col2:
        pie_data = df_data[df_data["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()
        pie_data["Amount"] = pd.to_numeric(pie_data["Amount"], errors="coerce")

        fig_pie = px.pie(pie_data, names="Category", values="Amount", title="💰 Expenses by Category",hole=0.4)
        fig_pie.update_layout(
            width=250,  
            height=250, 
            margin=dict(t=40, b=0, l=0, r=0) ,
            # title = dict(
            #     text = "Expenses by Category",
            #     font= dict(size=20,family='Arial',color="black"),
            #     x = 0.5,
            #     xanchor ='center'
            # )
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    # st.markdown("---")
    # st.markdown("#### 📊 Expense Distribution")

    # LINE CHART
    line_data = df_data.groupby("Date")["Amount"].sum().reset_index()
    fig_line = px.line(line_data, x="Date", y="Amount")
    fig_line.update_layout(
        title=dict(
            text="Cash Flow Over Time",
            font=dict(size=20,family='Arial'),
            x = 0.5,
            xanchor='center'
        )
    )
    st.plotly_chart(fig_line, use_container_width=True)



# Footer
st.markdown("---")
st.markdown("Need help? Check out the [📘 Guidelines](guidelines.py) Page", unsafe_allow_html=True)
st.caption(f"© 2025 {DEVELOPER_NAME}")
