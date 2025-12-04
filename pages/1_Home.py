"""
Home Page - Dashboard for HomeTracker
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, THEME_COLORS
from auth import check_authentication, get_current_user, require_authentication, log_page_visit
from utils import (
    load_transactions, get_total_balance, format_currency, 
    get_monthly_summary, get_top_spending_category, get_average_daily_spending,
    get_spending_insights, get_low_stock_items, get_expiring_items
)

# Require authentication
require_authentication()
log_page_visit("1_Home.py")

# Get current user
user = get_current_user()
user_name = user.get('full_name', user.get('username', 'User')) if user else 'User'

# Page header
st.markdown(f"""
<div class='main-header' style='background: linear-gradient(135deg, #14b8a6 0%, #f43f5e 50%, #06b6d4 100%);
    padding: 2rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;
    box-shadow: 0 20px 50px rgba(20, 184, 166, 0.3);'>
    <h1 style='color: white !important; margin: 0; font-size: 2.5rem;'>🏠 HomeTracker Dashboard</h1>
    <p style='color: rgba(255,255,255,0.9) !important; margin: 0.5rem 0 0 0;'>
        Welcome back, <strong>{user_name}</strong>! Here's your household summary for <strong>{datetime.today():%B %Y}</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# Quick action buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("➕ Add Transaction", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Add_Transaction.py")
with col2:
    if st.button("📊 View Reports", use_container_width=True):
        st.switch_page("pages/4_Reports.py")
with col3:
    if st.button("🍳 Kitchen", use_container_width=True):
        st.switch_page("pages/5_Kitchen.py")
with col4:
    if st.button("🛒 Shopping List", use_container_width=True):
        st.switch_page("pages/6_Shopping_List.py")

st.markdown("---")

# Load data
df_data = load_transactions()

if df_data.empty:
    st.info("ℹ️ No transactions yet. Start by adding your first budget or expense!")
    
    st.markdown("""
    ### 🚀 Getting Started
    
    1. **Add your monthly budget** - Set how much you plan to spend
    2. **Track expenses** - Record your daily spending
    3. **Manage kitchen inventory** - Keep track of what you have
    4. **Create shopping lists** - Never forget what you need
    
    Click the **➕ Add Transaction** button above to get started!
    """)
    
else:
    # Calculate metrics
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_data = get_monthly_summary(df_data, current_year, current_month)
    total_balance = get_total_balance(df_data)
    top_category = get_top_spending_category(df_data)
    avg_daily = get_average_daily_spending(df_data)
    
    # Main metrics
    st.markdown("### 📊 Financial Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💵 Monthly Budget",
            format_currency(monthly_data['budget']),
            help="Total budget allocated this month"
        )
    
    with col2:
        st.metric(
            "📤 Total Expenses",
            format_currency(monthly_data['expense']),
            help="Total spent this month"
        )
    
    with col3:
        remaining = monthly_data['budget'] - monthly_data['expense']
        delta_color = "normal" if remaining >= 0 else "inverse"
        st.metric(
            "💰 Remaining",
            format_currency(remaining),
            delta=f"{(remaining/monthly_data['budget']*100):.1f}% left" if monthly_data['budget'] > 0 else None,
            delta_color=delta_color
        )
    
    with col4:
        st.metric(
            "📈 Total Balance",
            format_currency(total_balance),
            help="Overall balance (all time)"
        )
    
    # Budget progress bar
    if monthly_data['budget'] > 0:
        progress = min(monthly_data['expense'] / monthly_data['budget'], 1.0)
        st.progress(progress, text=f"Budget Usage: {progress*100:.1f}%")
        
        if progress >= 1:
            st.error("⚠️ You've exceeded your monthly budget!")
        elif progress >= 0.8:
            st.warning("⚠️ Budget is running low! Over 80% has been spent.")
        else:
            st.success("🎉 Great job! You're on track with your budget.")
    
    st.markdown("---")
    
    # Two-column layout for charts and insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Recent Transactions")
        recent_df = df_data.head(10).copy()
        recent_df["Date"] = pd.to_datetime(recent_df["Date"]).dt.strftime("%d %b %Y")
        recent_df["Amount"] = recent_df["Amount"].apply(lambda x: format_currency(x))
        st.dataframe(
            recent_df[["Date", "Type", "Category", "Amount", "Description"]],
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("### 💰 Expenses by Category")
        expense_df = df_data[df_data["Type"] == "Expense"]
        
        if not expense_df.empty:
            pie_data = expense_df.groupby("Category")["Amount"].sum().reset_index()
            
            fig_pie = px.pie(
                pie_data, 
                names="Category", 
                values="Amount",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_pie.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data to display")
    
    st.markdown("---")
    
    # Cash flow chart
    st.markdown("### 📈 Cash Flow Over Time")
    
    if not df_data.empty:
        # Prepare data
        df_chart = df_data.copy()
        df_chart['Date'] = pd.to_datetime(df_chart['Date'])
        
        # Group by date and type
        daily_budget = df_chart[df_chart['Type'] == 'Budget'].groupby('Date')['Amount'].sum().reset_index()
        daily_expense = df_chart[df_chart['Type'] == 'Expense'].groupby('Date')['Amount'].sum().reset_index()
        
        # Create figure
        fig = go.Figure()
        
        if not daily_budget.empty:
            fig.add_trace(go.Scatter(
                x=daily_budget['Date'],
                y=daily_budget['Amount'],
                mode='lines+markers',
                name='Budget',
                line=dict(color='#10b981', width=3),
                marker=dict(size=8)
            ))
        
        if not daily_expense.empty:
            fig.add_trace(go.Scatter(
                x=daily_expense['Date'],
                y=daily_expense['Amount'],
                mode='lines+markers',
                name='Expenses',
                line=dict(color='#ef4444', width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                title="Date"
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)',
                title="Amount (KSH)"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            margin=dict(t=50, b=50, l=50, r=50)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Insights and Alerts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💡 Spending Insights")
        insights = get_spending_insights(df_data)
        
        if insights:
            for insight in insights:
                if insight['type'] == 'warning':
                    st.warning(insight['message'])
                elif insight['type'] == 'success':
                    st.success(insight['message'])
                else:
                    st.info(insight['message'])
        else:
            st.info("Add more transactions to get personalized insights!")
        
        st.markdown(f"""
        <div style='background: #1e293b; padding: 1rem; border-radius: 12px; margin-top: 1rem;'>
            <p style='color: #a78bfa; font-weight: 600; margin-bottom: 0.5rem;'>📊 Quick Stats</p>
            <p style='color: #e2e8f0; margin: 0.25rem 0;'>
                <strong>Top Category:</strong> {top_category}
            </p>
            <p style='color: #e2e8f0; margin: 0.25rem 0;'>
                <strong>Avg Daily Spending:</strong> {format_currency(avg_daily)}
            </p>
            <p style='color: #e2e8f0; margin: 0.25rem 0;'>
                <strong>Transactions This Month:</strong> {monthly_data['transactions']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🍳 Kitchen Alerts")
        
        try:
            low_stock = get_low_stock_items()
            expiring = get_expiring_items(days=7)
            
            if not low_stock.empty:
                st.warning(f"🔔 **{len(low_stock)} items low in stock:**")
                for _, item in low_stock.head(5).iterrows():
                    st.markdown(f"- {item['item_name']} ({item['quantity']} {item['unit']} left)")
            else:
                st.success("✅ All items are well stocked!")
            
            if not expiring.empty:
                st.warning(f"⏰ **{len(expiring)} items expiring soon:**")
                for _, item in expiring.head(5).iterrows():
                    st.markdown(f"- {item['item_name']} (expires {item['expiry_date']})")
            else:
                st.success("✅ No items expiring soon!")
                
        except Exception as e:
            st.info("Set up your kitchen inventory to see alerts here!")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280; padding: 1rem;'>
    <p>Need help? Check out the <a href='#' style='color: #14b8a6;'>About</a> page</p>
    <p>© 2025 {DEVELOPER_NAME} | All rights reserved</p>
</div>
""", unsafe_allow_html=True)
