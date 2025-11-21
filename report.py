# report.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os 

st.title("📈 Reports & Analytics")


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


tab1, tab2 = st.tabs(["📊 Visual Insights","Yealy sumary section"])

# Show message if no data available
if df_data.empty:
    st.warning("No transactions available. Add some transactions first.")
    st.stop()
    

# ---------- TAB 1: VISUAL INSIGHTS ----------
with tab1:
    
    st.subheader("📊 Graphical Insights")
        # --- Monthly Filter ---
    with st.expander("📅 Filter by Month & Year", expanded=True):
        months = {1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"}

        col1, col2 = st.columns(2)
        selected_year = col1.selectbox("Select Year", sorted(df_data["Date"].dt.year.unique(), reverse=True))
        selected_month = col2.selectbox("Select Month", list(months.values()))

        month_number = list(months.values()).index(selected_month) + 1
        filtered_df = df_data[(df_data["Date"].dt.year == selected_year) & 
                            (df_data["Date"].dt.month == month_number)]
        
        # --- Monthly Summary ---
    st.subheader(f"📌 Summary ")
    st.markdown(f"👋 Hello! Here's the household summary for **{selected_month} {selected_year}**.")


    budget_month = filtered_df[filtered_df["Type"] == "Budget"]["Amount"].sum()
    expense_month = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
    net_month = budget_month - expense_month

    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Budget", f"KSH {budget_month:,.2f}")
    col2.metric("📭 Expenses", f"KSH {expense_month:,.2f}")
    net_color = "normal" if net_month >= 0 else "inverse"
    col3.metric("💰 Balance", f"KSH {net_month:,.2f}", delta_color=net_color)

    st.download_button(
        label="📁 Export This Month's Data",
        data=filtered_df.to_csv(index=False),
        file_name=f"expenses_{selected_month}_{selected_year}.csv",
        mime="text/csv"
    )


    if filtered_df.empty:
        st.warning("No data available for this month.")
    else:
        # PIE CHART

        pie_data = filtered_df[filtered_df["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()
        fig_pie = px.pie(pie_data, names="Category", values="Amount", title="Expenses by Category")
        st.plotly_chart(fig_pie, use_container_width=True)

        

        # LINE CHART
        line_data = filtered_df.groupby("Date")["Amount"].sum().reset_index()
        fig_line = px.line(line_data, x="Date", y="Amount", title="Cash Flow Over Time")
        st.plotly_chart(fig_line, use_container_width=True)

        # BAR CHART
        bar_data = filtered_df.groupby(["Category", "Type"])["Amount"].sum().reset_index()
        fig_bar = px.bar(bar_data, x="Category", y="Amount", color="Type", barmode="group", title="Budget vs Expenses by Category")
        st.plotly_chart(fig_bar, use_container_width=True)



with tab2:
    st.subheader("📅 Yearly Summary")

    years_available = df_data["Date"].dt.year.dropna().unique().tolist()
    selected_year = st.selectbox("Select Year", sorted(years_available, reverse=True),key="year-summary")

    year_df = df_data[df_data["Date"].dt.year == selected_year]

    if not year_df.empty:
        year_budget = year_df[year_df["Type"] == "Budget"]["Amount"].sum()
        year_expense = year_df[year_df["Type"] == "Expense"]["Amount"].sum()
        net_yearly = year_budget - year_expense

        st.markdown(f"""
        <div style="display: flex; justify-content: space-around; margin-bottom: 2rem;">
            <div><h4>💵 Total Budget</h4><p style="font-size:18px;">KSH {year_budget:,.2f}</p></div>
            <div><h4>💸 Total Expense</h4><p style="font-size:18px;">KSH {year_expense:,.2f}</p></div>
            <div><h4>💰 Net Balance</h4><p style="font-size:18px;">KSH {net_yearly:,.2f}</p></div>
        </div>
        """, unsafe_allow_html=True)

        # Monthly bar chart for the selected year
        monthly_summary = year_df.groupby([year_df["Date"].dt.strftime('%b'), "Type"])["Amount"].sum().reset_index()
        monthly_summary["Month"] = pd.Categorical(monthly_summary["Date"], categories=[
            'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], ordered=True)
        monthly_summary = monthly_summary.sort_values("Month")

        bar_chart = px.bar(monthly_summary, x="Month", y="Amount", color="Type",
                        barmode="group", title=f"📊 Monthly Budget vs Expenses - {selected_year}")
        st.plotly_chart(bar_chart, use_container_width=True)
    else:
        st.info("No data available for the selected year.")





