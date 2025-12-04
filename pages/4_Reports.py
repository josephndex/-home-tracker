"""
Reports Page - Generate comprehensive financial reports
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, CURRENCY_SYMBOL
from auth import require_authentication, get_current_user, log_page_visit
from utils import load_transactions, format_currency, get_date_range_data

# Require authentication
require_authentication()
log_page_visit("4_Reports.py")

user = get_current_user()
user_id = user.get('id') if user else None

st.title("📊 Financial Reports")

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
    padding: 1rem; border-radius: 12px; border-left: 4px solid #f43f5e; margin-bottom: 1rem;'>
    <p style='color: #e2e8f0; margin: 0;'>
        Generate detailed reports to understand your spending patterns and financial health.
    </p>
</div>
""", unsafe_allow_html=True)

# Load data
df_data = load_transactions()

# Date range selector
col1, col2, col3 = st.columns(3)

with col1:
    report_type = st.selectbox(
        "📅 Report Period",
        ["This Month", "Last Month", "This Year", "Last 3 Months", "Last 6 Months", "Custom Range"]
    )

# Calculate date range based on selection
today = datetime.now()

if report_type == "This Month":
    start_date = today.replace(day=1)
    end_date = today
elif report_type == "Last Month":
    last_month = today.replace(day=1) - timedelta(days=1)
    start_date = last_month.replace(day=1)
    end_date = last_month
elif report_type == "This Year":
    start_date = today.replace(month=1, day=1)
    end_date = today
elif report_type == "Last 3 Months":
    start_date = today - timedelta(days=90)
    end_date = today
elif report_type == "Last 6 Months":
    start_date = today - timedelta(days=180)
    end_date = today
else:  # Custom Range
    with col2:
        start_date = st.date_input("Start Date", value=today.replace(day=1))
    with col3:
        end_date = st.date_input("End Date", value=today)
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())

# Filter data
if not df_data.empty:
    filtered_df = df_data[
        (df_data["Date"] >= start_date) & 
        (df_data["Date"] <= end_date)
    ].copy()
else:
    filtered_df = pd.DataFrame()

st.markdown("---")

# Tabs for different reports
tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "📈 Trends", "🥧 Categories", "📋 Detailed"])

with tab1:
    st.markdown("### 📊 Financial Summary")
    
    if not filtered_df.empty:
        # Income vs Expense
        total_income = filtered_df[filtered_df["Type"] == "Income"]["Amount"].sum()
        total_expense = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
        net_savings = total_income - total_expense
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Income", format_currency(total_income))
        
        with col2:
            st.metric("💸 Total Expenses", format_currency(total_expense))
        
        with col3:
            st.metric(
                "🎯 Net Savings",
                format_currency(net_savings),
                delta=f"{(net_savings/total_income*100) if total_income > 0 else 0:.1f}%"
            )
        
        with col4:
            transaction_count = len(filtered_df)
            st.metric("📝 Transactions", f"{transaction_count:,}")
        
        st.markdown("---")
        
        # Income vs Expense Chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Income vs Expenses")
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=['Income', 'Expenses'],
                y=[total_income, total_expense],
                marker_color=['#10b981', '#ef4444'],
                text=[format_currency(total_income), format_currency(total_expense)],
                textposition='outside'
            ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                margin=dict(t=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Savings Rate")
            
            if total_income > 0:
                savings_rate = (net_savings / total_income) * 100
                
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=savings_rate,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Savings Rate", 'font': {'color': '#e2e8f0'}},
                    delta={'reference': 20, 'relative': False, 'suffix': '%'},
                    number={'suffix': '%', 'font': {'color': '#e2e8f0'}},
                    gauge={
                        'axis': {'range': [-50, 100], 'tickwidth': 1, 'tickcolor': "#e2e8f0"},
                        'bar': {'color': "#f43f5e"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [-50, 0], 'color': '#ef4444'},
                            {'range': [0, 20], 'color': '#14b8a6'},
                            {'range': [20, 40], 'color': '#eab308'},
                            {'range': [40, 100], 'color': '#10b981'}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 4},
                            'thickness': 0.75,
                            'value': savings_rate
                        }
                    }
                ))
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0')
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No income recorded in this period.")
        
        # Daily averages
        st.markdown("---")
        st.markdown("### 📈 Daily Averages")
        
        days_in_period = (end_date - start_date).days + 1
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_daily_expense = total_expense / days_in_period if days_in_period > 0 else 0
            st.metric("💸 Daily Expense", format_currency(avg_daily_expense))
        
        with col2:
            avg_daily_income = total_income / days_in_period if days_in_period > 0 else 0
            st.metric("💰 Daily Income", format_currency(avg_daily_income))
        
        with col3:
            avg_daily_savings = net_savings / days_in_period if days_in_period > 0 else 0
            st.metric("🎯 Daily Savings", format_currency(avg_daily_savings))
        
    else:
        st.info("No transactions found for the selected period.")

with tab2:
    st.markdown("### 📈 Spending Trends")
    
    if not filtered_df.empty:
        # Daily spending trend
        st.markdown("#### Daily Spending Pattern")
        
        expenses_df = filtered_df[filtered_df["Type"] == "Expense"].copy()
        
        if not expenses_df.empty:
            daily_spending = expenses_df.groupby(expenses_df["Date"].dt.date)["Amount"].sum().reset_index()
            daily_spending.columns = ["Date", "Amount"]
            
            fig = px.line(
                daily_spending,
                x="Date",
                y="Amount",
                title="Daily Spending",
                markers=True
            )
            
            fig.update_traces(
                line_color='#14b8a6',
                marker_color='#f43f5e'
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title="Date",
                yaxis_title=f"Amount ({CURRENCY_SYMBOL})"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Weekly pattern
            st.markdown("#### Weekly Pattern")
            
            expenses_df["DayOfWeek"] = expenses_df["Date"].dt.day_name()
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            weekly_spending = expenses_df.groupby("DayOfWeek")["Amount"].mean().reindex(day_order)
            
            fig = px.bar(
                x=weekly_spending.index,
                y=weekly_spending.values,
                color=weekly_spending.values,
                color_continuous_scale="RdYlGn_r"
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title="Day of Week",
                yaxis_title=f"Average Spending ({CURRENCY_SYMBOL})",
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses recorded in this period.")
    else:
        st.info("No transactions found for the selected period.")

with tab3:
    st.markdown("### 🥧 Category Analysis")
    
    if not filtered_df.empty:
        expenses_df = filtered_df[filtered_df["Type"] == "Expense"].copy()
        
        if not expenses_df.empty:
            # Category breakdown
            category_spending = expenses_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Spending by Category")
                
                fig = px.pie(
                    values=category_spending.values,
                    names=category_spending.index,
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Top Spending Categories")
                
                top_categories = category_spending.head(10)
                
                fig = px.bar(
                    y=top_categories.index,
                    x=top_categories.values,
                    orientation='h',
                    color=top_categories.values,
                    color_continuous_scale="Oranges"
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title=f"Amount ({CURRENCY_SYMBOL})",
                    yaxis_title="",
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Category table
            st.markdown("#### Detailed Category Breakdown")
            
            category_df = pd.DataFrame({
                "Category": category_spending.index,
                "Amount": category_spending.values,
                "Percentage": (category_spending.values / category_spending.sum() * 100)
            })
            
            category_df["Amount"] = category_df["Amount"].apply(lambda x: format_currency(x))
            category_df["Percentage"] = category_df["Percentage"].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(category_df, use_container_width=True, hide_index=True)
        else:
            st.info("No expenses recorded in this period.")
    else:
        st.info("No transactions found for the selected period.")

with tab4:
    st.markdown("### 📋 Detailed Transaction Report")
    
    if not filtered_df.empty:
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            type_filter = st.selectbox(
                "Transaction Type",
                ["All", "Income", "Expense"]
            )
        
        with col2:
            categories = ["All"] + sorted(filtered_df["Category"].unique().tolist())
            category_filter = st.selectbox("Category", categories)
        
        with col3:
            sort_by = st.selectbox(
                "Sort By",
                ["Date (Newest)", "Date (Oldest)", "Amount (Highest)", "Amount (Lowest)"]
            )
        
        # Apply filters
        report_df = filtered_df.copy()
        
        if type_filter != "All":
            report_df = report_df[report_df["Type"] == type_filter]
        
        if category_filter != "All":
            report_df = report_df[report_df["Category"] == category_filter]
        
        # Apply sorting
        if sort_by == "Date (Newest)":
            report_df = report_df.sort_values("Date", ascending=False)
        elif sort_by == "Date (Oldest)":
            report_df = report_df.sort_values("Date", ascending=True)
        elif sort_by == "Amount (Highest)":
            report_df = report_df.sort_values("Amount", ascending=False)
        else:
            report_df = report_df.sort_values("Amount", ascending=True)
        
        # Display
        st.markdown(f"**{len(report_df)} transactions**")
        
        display_df = report_df.copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
        display_df["Amount"] = display_df["Amount"].apply(lambda x: format_currency(x))
        
        st.dataframe(display_df[["Date", "Category", "Type", "Amount", "Description"]], 
                    use_container_width=True, hide_index=True)
        
        # Export option
        st.markdown("---")
        
        csv = report_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Report as CSV",
            data=csv,
            file_name=f"report_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No transactions found for the selected period.")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280;'>
    <p>📊 Reports help you make informed financial decisions.</p>
    <p>© 2025 {DEVELOPER_NAME}</p>
</div>
""", unsafe_allow_html=True)
