"""
Kitchen Central - Your Kitchen Management Hub
The heart of home management with a focus on kitchen essentials
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, CURRENCY_SYMBOL, KITCHEN_CATEGORIES
from auth import require_authentication, get_current_user, log_page_visit
from utils import load_transactions, format_currency, get_category_id, get_budget

# Require authentication
require_authentication()
log_page_visit("5_Kitchen.py")

user = get_current_user()
user_id = user.get('id') if user else None

# Kitchen-themed header
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='background: linear-gradient(135deg, #14b8a6 0%, #f43f5e 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 3rem; margin-bottom: 0.5rem;'>
        🍳 Kitchen Central
    </h1>
    <p style='color: #a78bfa; font-size: 1.2rem;'>
        Your Smart Kitchen Management Hub
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.15) 0%, rgba(244, 63, 94, 0.15) 100%);
    padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(244, 63, 94, 0.3);
    margin-bottom: 2rem;'>
    <div style='display: flex; align-items: center; gap: 1rem;'>
        <span style='font-size: 2.5rem;'>👨‍🍳</span>
        <div>
            <h3 style='color: #14b8a6; margin: 0;'>Welcome to Kitchen Central!</h3>
            <p style='color: #e2e8f0; margin: 0;'>
                Track your kitchen expenses, manage grocery budgets, and keep your pantry organized.
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load data
df_data = load_transactions()

# Filter for kitchen categories only
kitchen_cat_list = [
    "Groceries", "Vegetables", "Meat & Poultry", "Fish & Seafood", "Fruits",
    "Dairy & Eggs", "Beverages", "Snacks", "Cooking Oil", "Spices & Seasonings",
    "Baking Supplies", "Cleaning Supplies", "Kitchen Supplies", "Cooking Gas"
]

if not df_data.empty:
    kitchen_df = df_data[
        (df_data["Category"].isin(kitchen_cat_list)) &
        (df_data["Type"] == "Expense")
    ].copy()
else:
    kitchen_df = pd.DataFrame()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Overview", "📊 Analytics", "🛒 Shopping List", "📈 Trends"])

with tab1:
    st.markdown("### 🏠 Kitchen Overview")
    
    # Current month stats
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    if not kitchen_df.empty:
        month_kitchen_df = kitchen_df[
            (kitchen_df["Date"].dt.month == current_month) &
            (kitchen_df["Date"].dt.year == current_year)
        ]
        
        total_kitchen_spending = month_kitchen_df["Amount"].sum()
        last_month_df = kitchen_df[
            (kitchen_df["Date"].dt.month == (current_month - 1 if current_month > 1 else 12)) &
            (kitchen_df["Date"].dt.year == (current_year if current_month > 1 else current_year - 1))
        ]
        last_month_spending = last_month_df["Amount"].sum()
        
        spending_change = ((total_kitchen_spending - last_month_spending) / last_month_spending * 100) if last_month_spending > 0 else 0
    else:
        total_kitchen_spending = 0
        spending_change = 0
    
    # Hero metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;'>
            <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>🛒 This Month</p>
            <h2 style='color: white; margin: 0.5rem 0;'>{}</h2>
        </div>
        """.format(format_currency(total_kitchen_spending)), unsafe_allow_html=True)
    
    with col2:
        delta_color = "#ef4444" if spending_change > 0 else "#10b981"
        delta_icon = "📈" if spending_change > 0 else "📉"
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;'>
            <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>{delta_icon} vs Last Month</p>
            <h2 style='color: white; margin: 0.5rem 0;'>{spending_change:+.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_daily = total_kitchen_spending / datetime.now().day if datetime.now().day > 0 else 0
        st.markdown("""
        <div style='background: linear-gradient(135deg, #14b8a6 0%, #ea580c 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;'>
            <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>📅 Daily Average</p>
            <h2 style='color: white; margin: 0.5rem 0;'>{}</h2>
        </div>
        """.format(format_currency(avg_daily)), unsafe_allow_html=True)
    
    with col4:
        transaction_count = len(month_kitchen_df) if not kitchen_df.empty else 0
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f43f5e 0%, #9333ea 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;'>
            <p style='color: rgba(255,255,255,0.8); margin: 0; font-size: 0.9rem;'>📝 Purchases</p>
            <h2 style='color: white; margin: 0.5rem 0;'>{transaction_count}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Category breakdown for kitchen
    st.markdown("### 🍽️ Kitchen Category Spending")
    
    if not kitchen_df.empty and not month_kitchen_df.empty:
        category_spending = month_kitchen_df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig = px.pie(
                values=category_spending.values,
                names=category_spending.index,
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Oranges[::-1]
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                showlegend=False,
                margin=dict(t=20, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Category cards
            for category, amount in category_spending.head(5).items():
                emoji = KITCHEN_CATEGORIES.get(category, "🍴")
                percentage = (amount / total_kitchen_spending * 100) if total_kitchen_spending > 0 else 0
                
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 0.8rem;
                    border-radius: 8px; margin-bottom: 0.5rem;
                    display: flex; justify-content: space-between; align-items: center;'>
                    <span style='color: #e2e8f0;'>{emoji} {category}</span>
                    <span style='color: #a78bfa; font-weight: bold;'>{format_currency(amount)} ({percentage:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No kitchen transactions yet this month. Start adding your grocery purchases!")
    
    # Recent kitchen purchases
    st.markdown("---")
    st.markdown("### 🕐 Recent Kitchen Purchases")
    
    if not kitchen_df.empty:
        recent_kitchen = kitchen_df.sort_values("Date", ascending=False).head(10)
        
        for _, row in recent_kitchen.iterrows():
            emoji = KITCHEN_CATEGORIES.get(row["Category"], "🍴")
            date_str = row["Date"].strftime("%b %d")
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.03); padding: 0.8rem;
                border-radius: 8px; margin-bottom: 0.5rem;
                border-left: 3px solid #14b8a6;'>
                <div style='display: flex; justify-content: space-between;'>
                    <span style='color: #e2e8f0;'>{emoji} {row["Category"]}</span>
                    <span style='color: #10b981; font-weight: bold;'>{format_currency(row["Amount"])}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-top: 0.3rem;'>
                    <span style='color: #6b7280; font-size: 0.85rem;'>{row.get("Description", "")}</span>
                    <span style='color: #6b7280; font-size: 0.85rem;'>{date_str}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No kitchen purchases recorded yet.")

with tab2:
    st.markdown("### 📊 Kitchen Analytics")
    
    if not kitchen_df.empty:
        # Time period selector
        period = st.selectbox(
            "Analysis Period",
            ["Last 7 Days", "Last 30 Days", "Last 3 Months", "This Year"],
            index=1
        )
        
        # Filter data based on period
        today = datetime.now()
        if period == "Last 7 Days":
            start_date = today - timedelta(days=7)
        elif period == "Last 30 Days":
            start_date = today - timedelta(days=30)
        elif period == "Last 3 Months":
            start_date = today - timedelta(days=90)
        else:
            start_date = today.replace(month=1, day=1)
        
        period_df = kitchen_df[kitchen_df["Date"] >= start_date]
        
        if not period_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Spending Over Time")
                
                daily_spending = period_df.groupby(period_df["Date"].dt.date)["Amount"].sum().reset_index()
                daily_spending.columns = ["Date", "Amount"]
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=daily_spending["Date"],
                    y=daily_spending["Amount"],
                    mode='lines+markers',
                    fill='tozeroy',
                    line_color='#14b8a6',
                    fillcolor='rgba(20, 184, 166, 0.2)'
                ))
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title="Date",
                    yaxis_title=f"Spending ({CURRENCY_SYMBOL})",
                    margin=dict(t=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Category Comparison")
                
                cat_comparison = period_df.groupby("Category")["Amount"].sum().sort_values(ascending=True)
                
                fig = px.bar(
                    y=cat_comparison.index,
                    x=cat_comparison.values,
                    orientation='h',
                    color=cat_comparison.values,
                    color_continuous_scale="Oranges"
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title=f"Amount ({CURRENCY_SYMBOL})",
                    yaxis_title="",
                    coloraxis_showscale=False,
                    margin=dict(t=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Shopping frequency analysis
            st.markdown("---")
            st.markdown("#### 📅 Shopping Frequency Analysis")
            
            period_df["DayOfWeek"] = period_df["Date"].dt.day_name()
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            
            shopping_frequency = period_df.groupby("DayOfWeek").size().reindex(day_order, fill_value=0)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    x=shopping_frequency.index,
                    y=shopping_frequency.values,
                    color=shopping_frequency.values,
                    color_continuous_scale="Purples"
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title="Day of Week",
                    yaxis_title="Number of Purchases",
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                avg_spending_by_day = period_df.groupby("DayOfWeek")["Amount"].mean().reindex(day_order, fill_value=0)
                
                fig = px.bar(
                    x=avg_spending_by_day.index,
                    y=avg_spending_by_day.values,
                    color=avg_spending_by_day.values,
                    color_continuous_scale="Oranges"
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title="Day of Week",
                    yaxis_title=f"Avg Spending ({CURRENCY_SYMBOL})",
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Insights
            most_frequent_day = shopping_frequency.idxmax()
            highest_spending_day = avg_spending_by_day.idxmax()
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
                padding: 1rem; border-radius: 12px; border: 1px solid rgba(244, 63, 94, 0.3);'>
                <h4 style='color: #14b8a6; margin-bottom: 0.5rem;'>💡 Insights</h4>
                <ul style='color: #e2e8f0; margin: 0;'>
                    <li>You shop most frequently on <strong>{most_frequent_day}</strong></li>
                    <li>Your highest spending day is <strong>{highest_spending_day}</strong></li>
                    <li>Total kitchen purchases in this period: <strong>{len(period_df)}</strong></li>
                    <li>Average purchase amount: <strong>{format_currency(period_df["Amount"].mean())}</strong></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No data for the selected period.")
    else:
        st.info("No kitchen transactions recorded yet.")

with tab3:
    st.markdown("### 🛒 Smart Shopping List")
    
    st.markdown("""
    <div style='background: rgba(20, 184, 166, 0.1); padding: 1rem; border-radius: 12px;
        border-left: 4px solid #14b8a6; margin-bottom: 1rem;'>
        <p style='color: #e2e8f0; margin: 0;'>
            Create and manage your shopping list. Items are based on your common purchases.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize shopping list in session state
    if "shopping_list" not in st.session_state:
        st.session_state.shopping_list = []
    
    # Add item form
    with st.form("add_item_form"):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            new_item = st.text_input("Item Name", placeholder="e.g., Milk, Bread, Eggs...")
        
        with col2:
            quantity = st.number_input("Quantity", min_value=1, value=1)
        
        with col3:
            category = st.selectbox("Category", list(KITCHEN_CATEGORIES.keys()))
        
        if st.form_submit_button("➕ Add to List", use_container_width=True):
            if new_item:
                st.session_state.shopping_list.append({
                    "item": new_item,
                    "quantity": quantity,
                    "category": category,
                    "checked": False
                })
                st.rerun()
    
    st.markdown("---")
    
    # Quick add suggestions based on history
    if not kitchen_df.empty:
        st.markdown("#### 💡 Quick Add (Based on Your History)")
        
        # Get most common descriptions/items
        common_items = kitchen_df["Description"].value_counts().head(8).index.tolist()
        
        cols = st.columns(4)
        for i, item in enumerate(common_items):
            if item and len(item) > 0:
                with cols[i % 4]:
                    if st.button(f"+ {item[:15]}...", key=f"quick_{i}", use_container_width=True):
                        st.session_state.shopping_list.append({
                            "item": item,
                            "quantity": 1,
                            "category": "Groceries",
                            "checked": False
                        })
                        st.rerun()
    
    st.markdown("---")
    
    # Display shopping list
    st.markdown("#### 📝 Your Shopping List")
    
    if st.session_state.shopping_list:
        for i, item in enumerate(st.session_state.shopping_list):
            col1, col2, col3, col4 = st.columns([0.5, 3, 1, 0.5])
            
            with col1:
                checked = st.checkbox("", value=item["checked"], key=f"check_{i}")
                if checked != item["checked"]:
                    st.session_state.shopping_list[i]["checked"] = checked
                    st.rerun()
            
            with col2:
                emoji = KITCHEN_CATEGORIES.get(item["category"], "🛒")
                style = "text-decoration: line-through; color: #6b7280;" if item["checked"] else "color: #e2e8f0;"
                st.markdown(f"<span style='{style}'>{emoji} {item['item']}</span>", unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"<span style='color: #a78bfa;'>x{item['quantity']}</span>", unsafe_allow_html=True)
            
            with col4:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.shopping_list.pop(i)
                    st.rerun()
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Checked Items", use_container_width=True):
                st.session_state.shopping_list = [
                    item for item in st.session_state.shopping_list if not item["checked"]
                ]
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear All", use_container_width=True, type="secondary"):
                st.session_state.shopping_list = []
                st.rerun()
    else:
        st.info("Your shopping list is empty. Add items above!")

with tab4:
    st.markdown("### 📈 Kitchen Spending Trends")
    
    if not kitchen_df.empty:
        # Monthly comparison
        st.markdown("#### Monthly Kitchen Spending")
        
        kitchen_df["Month"] = kitchen_df["Date"].dt.to_period("M").astype(str)
        monthly_spending = kitchen_df.groupby("Month")["Amount"].sum().tail(12)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=monthly_spending.index,
            y=monthly_spending.values,
            marker_color='#14b8a6',
            text=[format_currency(v) for v in monthly_spending.values],
            textposition='outside'
        ))
        
        # Add trend line
        fig.add_trace(go.Scatter(
            x=monthly_spending.index,
            y=monthly_spending.values,
            mode='lines',
            line=dict(color='#f43f5e', width=2, dash='dash'),
            name='Trend'
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e2e8f0'),
            xaxis_title="Month",
            yaxis_title=f"Spending ({CURRENCY_SYMBOL})",
            showlegend=False,
            margin=dict(t=40)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Category trends over time
        st.markdown("---")
        st.markdown("#### Category Trends (Last 6 Months)")
        
        # Get last 6 months of data
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_df = kitchen_df[kitchen_df["Date"] >= six_months_ago]
        
        if not recent_df.empty:
            recent_df["Month"] = recent_df["Date"].dt.to_period("M").astype(str)
            
            # Get top 5 categories
            top_cats = recent_df.groupby("Category")["Amount"].sum().nlargest(5).index.tolist()
            
            pivot_df = recent_df[recent_df["Category"].isin(top_cats)].groupby(
                ["Month", "Category"]
            )["Amount"].sum().unstack(fill_value=0)
            
            fig = go.Figure()
            
            colors = ['#14b8a6', '#f43f5e', '#10b981', '#6366f1', '#eab308']
            
            for i, cat in enumerate(pivot_df.columns):
                fig.add_trace(go.Scatter(
                    x=pivot_df.index,
                    y=pivot_df[cat],
                    name=cat,
                    mode='lines+markers',
                    line=dict(color=colors[i % len(colors)], width=2)
                ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title="Month",
                yaxis_title=f"Spending ({CURRENCY_SYMBOL})",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Spending predictions
        st.markdown("---")
        st.markdown("#### 🔮 Spending Forecast")
        
        if len(monthly_spending) >= 3:
            avg_spending = monthly_spending.mean()
            trend = (monthly_spending.iloc[-1] - monthly_spending.iloc[0]) / len(monthly_spending)
            predicted_next_month = monthly_spending.iloc[-1] + trend
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📊 Average Monthly", format_currency(avg_spending))
            
            with col2:
                st.metric("📈 Monthly Trend", format_currency(trend), delta=f"{(trend/avg_spending*100):.1f}%")
            
            with col3:
                st.metric("🔮 Next Month Est.", format_currency(max(predicted_next_month, 0)))
            
            st.markdown("""
            <div style='background: rgba(244, 63, 94, 0.1); padding: 1rem; border-radius: 12px;
                border-left: 4px solid #f43f5e;'>
                <p style='color: #e2e8f0; margin: 0;'>
                    💡 <strong>Pro Tip:</strong> Based on your spending patterns, consider setting a monthly 
                    kitchen budget of <strong>{}</strong> to stay on track.
                </p>
            </div>
            """.format(format_currency(avg_spending * 1.1)), unsafe_allow_html=True)
        else:
            st.info("Need at least 3 months of data for spending forecast.")
    else:
        st.info("Start tracking your kitchen expenses to see trends and insights!")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280;'>
    <p>🍳 Kitchen Central - Your smart kitchen management companion</p>
    <p>© 2025 {DEVELOPER_NAME}</p>
</div>
""", unsafe_allow_html=True)
