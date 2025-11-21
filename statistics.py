import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import *
from config import *

st.title("📈 Advanced Statistics & Insights")

# Load data
df = load_cached_expense_data()

if df.empty:
    st.warning("⚠️ No expense data available. Please add some records.")
    st.info("💡 Go to 'Add Expense' to start tracking your finances!")
    st.stop()

# Filter for expenses only
expense_df = df[df["Type"] == "Expense"].copy()

if expense_df.empty:
    st.warning("⚠️ No expense records found. Only income recorded so far.")
    st.stop()

# ==================== KEY METRICS ====================
st.markdown("### 📊 Key Performance Indicators")

# Calculate KPIs
total_expense = expense_df["Amount"].sum()
avg_daily_expense = get_average_daily_spending(df)
top_category = get_top_spending_category(df)
most_expensive_day, max_day_amount = get_most_expensive_day(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💰 Total Expenses", format_currency(total_expense))

with col2:
    st.metric("📆 Avg Daily Spend", format_currency(avg_daily_expense))

with col3:
    st.metric("🏆 Top Category", top_category)

with col4:
    if most_expensive_day:
        st.metric("📅 Highest Spend Day", most_expensive_day.strftime("%d %b"))
        st.caption(format_currency(max_day_amount))

st.markdown("---")

# ==================== SPENDING INSIGHTS ====================
st.markdown("### 💡 Smart Insights")

insights = get_spending_insights(df)
if insights:
    for insight in insights:
        if insight["type"] == "warning":
            st.warning(insight["message"])
        elif insight["type"] == "success":
            st.success(insight["message"])
        else:
            st.info(insight["message"])
else:
    st.info("📊 Keep tracking your expenses to get personalized insights!")

st.markdown("---")

# ==================== DAILY EXPENSE TREND ====================
st.markdown("### 📊 Daily Expense Trend (Last 30 Days)")

daily_expenses = get_daily_expense_trend(df, days=30)
if not daily_expenses.empty:
    fig_line = px.line(
        daily_expenses, 
        x="Date", 
        y="Amount", 
        markers=True,
        title="Daily Expense Trend"
    )
    fig_line.update_traces(line_color='#FF6B6B', marker=dict(size=8))
    fig_line.update_layout(
        xaxis_title="Date",
        yaxis_title=f"Amount ({CURRENCY_SYMBOL})",
        hovermode='x unified'
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Show statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📈 Highest", format_currency(daily_expenses["Amount"].max()))
    with col2:
        st.metric("📉 Lowest", format_currency(daily_expenses["Amount"].min()))
    with col3:
        st.metric("📊 Average", format_currency(daily_expenses["Amount"].mean()))
else:
    st.info("No expense data available for the last 30 days")

st.markdown("---")

# ==================== CATEGORY-WISE ANALYSIS ====================
st.markdown("### 📌 Category-wise Deep Dive")

category_stats = get_category_statistics(df)
if not category_stats.empty:
    # Bar chart
    fig_bar = px.bar(
        category_stats,
        x="Category",
        y="Total",
        title="Total Spending by Category",
        color="Total",
        color_continuous_scale="Reds"
    )
    fig_bar.update_layout(
        xaxis_title="Category",
        yaxis_title=f"Total Amount ({CURRENCY_SYMBOL})",
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detailed statistics table
    st.markdown("#### 📋 Detailed Category Statistics")
    
    # Format the dataframe for display
    display_df = category_stats.copy()
    display_df["Total"] = display_df["Total"].apply(lambda x: format_currency(x))
    display_df["Average"] = display_df["Average"].apply(lambda x: format_currency(x))
    display_df["Min"] = display_df["Min"].apply(lambda x: format_currency(x))
    display_df["Max"] = display_df["Max"].apply(lambda x: format_currency(x))
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("No category data available")

st.markdown("---")

# ==================== WEEKDAY SPENDING PATTERN ====================
st.markdown("### 📅 Spending Pattern by Day of Week")

weekday_df = get_weekday_spending(df)
if not weekday_df.empty:
    fig_pie = px.pie(
        weekday_df,
        names="weekday",
        values="Amount",
        title="Spending Distribution by Weekday",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Find highest spending day
    max_weekday = weekday_df.loc[weekday_df["Amount"].idxmax(), "weekday"]
    max_weekday_amount = weekday_df["Amount"].max()
    
    st.info(f"💡 You spend most on **{max_weekday}s** ({format_currency(max_weekday_amount)} on average)")
else:
    st.info("Not enough data to analyze weekday patterns")

st.markdown("---")

# ==================== CUMULATIVE SPENDING ====================
st.markdown("### 📈 Cumulative Spending Growth")

cumulative_df = get_cumulative_spending(df)
if not cumulative_df.empty:
    fig_cumulative = px.area(
        cumulative_df,
        x="Date",
        y="cumulative",
        title="Cumulative Expense Growth Over Time",
        color_discrete_sequence=['#FF6B6B']
    )
    fig_cumulative.update_layout(
        xaxis_title="Date",
        yaxis_title=f"Cumulative Amount ({CURRENCY_SYMBOL})",
        hovermode='x unified'
    )
    st.plotly_chart(fig_cumulative, use_container_width=True)
    
    # Calculate burn rate
    if len(cumulative_df) > 1:
        days_tracked = (cumulative_df["Date"].max() - cumulative_df["Date"].min()).days + 1
        total_spent = cumulative_df["cumulative"].max()
        daily_burn_rate = total_spent / days_tracked if days_tracked > 0 else 0
        
        st.metric("🔥 Daily Burn Rate", format_currency(daily_burn_rate))
        st.caption(f"Based on {days_tracked} days of data")
else:
    st.info("Not enough data for cumulative analysis")

st.markdown("---")

# ==================== MONTHLY COMPARISON ====================
st.markdown("### 📊 Monthly Expense Comparison")

# Group by month
expense_df["YearMonth"] = expense_df["Date"].dt.to_period('M')
monthly_expenses = expense_df.groupby("YearMonth")["Amount"].sum().reset_index()
monthly_expenses["YearMonth"] = monthly_expenses["YearMonth"].astype(str)

if not monthly_expenses.empty:
    fig_monthly = px.bar(
        monthly_expenses,
        x="YearMonth",
        y="Amount",
        title="Monthly Expense Comparison",
        color="Amount",
        color_continuous_scale="Sunset"
    )
    fig_monthly.update_layout(
        xaxis_title="Month",
        yaxis_title=f"Amount ({CURRENCY_SYMBOL})",
        showlegend=False
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Month-over-month growth
    if len(monthly_expenses) >= 2:
        latest_month = monthly_expenses.iloc[-1]["Amount"]
        previous_month = monthly_expenses.iloc[-2]["Amount"]
        mom_change = ((latest_month - previous_month) / previous_month * 100) if previous_month > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Month", format_currency(latest_month))
        with col2:
            st.metric("Month-over-Month Change", f"{mom_change:+.1f}%", 
                     delta_color="inverse" if mom_change > 0 else "normal")
else:
    st.info("Not enough data for monthly comparison")

# ==================== SAVINGS RECOMMENDATION ====================
st.markdown("---")
st.markdown("### 💰 Savings Recommendations")

# Calculate income and expenses
total_income = df[df["Type"] == "Income"]["Amount"].sum()
total_expenses = df[df["Type"] == "Expense"]["Amount"].sum()
net_savings = total_income - total_expenses

if total_income > 0:
    savings_rate = (net_savings / total_income) * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        create_metric_card("Total Income", total_income)
    with col2:
        create_metric_card("Total Expenses", total_expenses)
    with col3:
        st.metric("Savings Rate", f"{savings_rate:.1f}%")
    
    # Recommendations
    if savings_rate < 10:
        st.error("🚨 Your savings rate is below 10%. Consider cutting expenses!")
    elif savings_rate < 20:
        st.warning("⚠️ Your savings rate is below 20%. Try to save more!")
    elif savings_rate < 30:
        st.success("✅ Good job! Your savings rate is healthy.")
    else:
        st.success("🎉 Excellent! You're saving over 30% of your income!")
    
    # Top 3 categories to cut
    st.markdown("#### 🎯 Top Categories to Optimize")
    category_sum = expense_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    top_3 = category_sum.head(3)
    
    for i, (category, amount) in enumerate(top_3.items(), 1):
        percent = (amount / total_expenses) * 100
        potential_saving = amount * 0.2  # 20% reduction
        st.write(f"{i}. **{category}**: {format_currency(amount)} ({percent:.1f}% of expenses)")
        st.caption(f"   💡 Reducing by 20% could save you {format_currency(potential_saving)}")

# Footer
st.markdown("---")
st.caption("💡 Tip: Check this page regularly to track your spending patterns and improve your financial health!")
