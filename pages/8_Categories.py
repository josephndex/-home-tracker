"""
Categories Management Page - Manage expense and income categories
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, CURRENCY_SYMBOL, KITCHEN_CATEGORIES, DEFAULT_CATEGORIES
from auth import require_authentication, get_current_user, log_page_visit
from utils import (
    load_categories, add_category, delete_category, 
    load_transactions, format_currency
)

# Require authentication
require_authentication()
log_page_visit("8_Categories.py")

user = get_current_user()
user_id = user.get('id') if user else None

st.title("📂 Category Management")

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
    padding: 1rem; border-radius: 12px; border-left: 4px solid #f43f5e; margin-bottom: 1rem;'>
    <p style='color: #e2e8f0; margin: 0;'>
        Manage your expense and income categories to better organize your finances.
    </p>
</div>
""", unsafe_allow_html=True)

# Load data
categories = load_categories()
df_data = load_transactions()

# Tabs
tab1, tab2, tab3 = st.tabs(["📋 All Categories", "➕ Add Category", "📊 Category Stats"])

with tab1:
    st.markdown("### 📋 Your Categories")
    
    # Search and filter
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search = st.text_input("🔍 Search categories", placeholder="Type to search...")
    
    with col2:
        sort_by = st.selectbox("Sort by", ["Alphabetical", "Most Used", "Least Used"])
    
    # Filter categories
    filtered_categories = [c for c in categories if search.lower() in c.lower()] if search else categories
    
    # Get usage stats
    category_usage = {}
    if not df_data.empty:
        usage_counts = df_data["Category"].value_counts().to_dict()
        category_usage = usage_counts
    
    # Sort categories
    if sort_by == "Alphabetical":
        filtered_categories.sort()
    elif sort_by == "Most Used":
        filtered_categories.sort(key=lambda x: category_usage.get(x, 0), reverse=True)
    else:
        filtered_categories.sort(key=lambda x: category_usage.get(x, 0))
    
    st.markdown(f"**{len(filtered_categories)} categories found**")
    
    st.markdown("---")
    
    # Display categories in a grid
    cols = st.columns(3)
    
    for i, category in enumerate(filtered_categories):
        col_idx = i % 3
        usage = category_usage.get(category, 0)
        emoji = KITCHEN_CATEGORIES.get(category, "📁")
        
        # Calculate total spent in category
        if not df_data.empty:
            total_spent = df_data[
                (df_data["Category"] == category) & 
                (df_data["Type"] == "Expense")
            ]["Amount"].sum()
        else:
            total_spent = 0
        
        with cols[col_idx]:
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 1rem;
                border-radius: 12px; margin-bottom: 0.8rem;
                border: 1px solid rgba(244, 63, 94, 0.2);'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-size: 1.5rem;'>{emoji}</span>
                    <span style='color: #a78bfa; font-size: 0.8rem;'>{usage} uses</span>
                </div>
                <h4 style='color: #e2e8f0; margin: 0.5rem 0;'>{category}</h4>
                <p style='color: #6b7280; margin: 0; font-size: 0.85rem;'>
                    Total: {format_currency(total_spent)}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Check if category is a default one
            is_default = category in DEFAULT_CATEGORIES
            
            if not is_default:
                if st.button("🗑️ Delete", key=f"del_{i}_{category}", use_container_width=True):
                    delete_category(category)
                    st.success(f"Category '{category}' deleted!")
                    st.rerun()
    
    # Kitchen categories section
    st.markdown("---")
    st.markdown("### 🍳 Kitchen Categories")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
        padding: 1rem; border-radius: 12px; margin-bottom: 1rem;'>
        <p style='color: #e2e8f0; margin: 0;'>
            These are your kitchen-specific categories for better tracking of food and kitchen expenses.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    kitchen_cols = st.columns(4)
    for i, (cat, emoji) in enumerate(KITCHEN_CATEGORIES.items()):
        with kitchen_cols[i % 4]:
            usage = category_usage.get(cat, 0)
            st.markdown(f"""
            <div style='background: rgba(20, 184, 166, 0.1); padding: 0.8rem;
                border-radius: 8px; margin-bottom: 0.5rem; text-align: center;'>
                <span style='font-size: 1.5rem;'>{emoji}</span>
                <p style='color: #e2e8f0; margin: 0.3rem 0 0 0; font-size: 0.85rem;'>{cat}</p>
                <span style='color: #6b7280; font-size: 0.75rem;'>{usage} uses</span>
            </div>
            """, unsafe_allow_html=True)

with tab2:
    st.markdown("### ➕ Add New Category")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("add_category_form"):
            new_category = st.text_input(
                "Category Name",
                placeholder="e.g., Pet Supplies, Garden, Electronics..."
            )
            
            category_type = st.selectbox(
                "Category Type",
                ["Expense", "Income", "Both"]
            )
            
            emoji_options = ["📁", "🛒", "🍳", "🏠", "🚗", "💊", "📚", "🎮", "👕", 
                           "💼", "🎯", "🎉", "🔧", "💡", "📦", "🎁", "🌿", "🐕"]
            
            selected_emoji = st.selectbox("Category Icon", emoji_options)
            
            description = st.text_area(
                "Description (Optional)",
                placeholder="Describe what this category is for..."
            )
            
            submitted = st.form_submit_button("➕ Add Category", use_container_width=True, type="primary")
            
            if submitted:
                if new_category:
                    if new_category not in categories:
                        add_category(new_category, category_type, selected_emoji, description)
                        st.success(f"Category '{new_category}' added successfully!")
                        st.rerun()
                    else:
                        st.error("This category already exists!")
                else:
                    st.error("Please enter a category name.")
    
    with col2:
        st.markdown("#### 💡 Category Suggestions")
        
        suggestions = [
            {"name": "Pet Supplies", "emoji": "🐕", "desc": "Food, toys, vet bills"},
            {"name": "Garden & Plants", "emoji": "🌿", "desc": "Plants, tools, seeds"},
            {"name": "Electronics", "emoji": "📱", "desc": "Gadgets and accessories"},
            {"name": "Personal Care", "emoji": "💆", "desc": "Grooming and self-care"},
            {"name": "Subscriptions", "emoji": "📺", "desc": "Streaming and memberships"},
            {"name": "Gifts", "emoji": "🎁", "desc": "Presents for others"},
        ]
        
        for suggestion in suggestions:
            if suggestion["name"] not in categories:
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 0.8rem;
                    border-radius: 8px; margin-bottom: 0.5rem;'>
                    <div style='display: flex; align-items: center; gap: 0.5rem;'>
                        <span style='font-size: 1.2rem;'>{suggestion["emoji"]}</span>
                        <span style='color: #e2e8f0;'>{suggestion["name"]}</span>
                    </div>
                    <p style='color: #6b7280; margin: 0.3rem 0 0 0; font-size: 0.85rem;'>
                        {suggestion["desc"]}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"➕ Add {suggestion['name']}", key=f"sug_{suggestion['name']}"):
                    add_category(suggestion["name"], "Expense", suggestion["emoji"], suggestion["desc"])
                    st.success(f"Category '{suggestion['name']}' added!")
                    st.rerun()

with tab3:
    st.markdown("### 📊 Category Statistics")
    
    if not df_data.empty:
        expense_df = df_data[df_data["Type"] == "Expense"]
        
        if not expense_df.empty:
            # Top spending categories
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Top Spending Categories")
                
                top_categories = expense_df.groupby("Category")["Amount"].sum().nlargest(10)
                
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
                    xaxis_title=f"Total Spent ({CURRENCY_SYMBOL})",
                    yaxis_title="",
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📈 Most Used Categories")
                
                usage_counts = expense_df["Category"].value_counts().head(10)
                
                fig = px.bar(
                    y=usage_counts.index,
                    x=usage_counts.values,
                    orientation='h',
                    color=usage_counts.values,
                    color_continuous_scale="Purples"
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title="Number of Transactions",
                    yaxis_title="",
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Category spending over time
            st.markdown("---")
            st.markdown("#### 📅 Category Spending Trends")
            
            # Get top 5 categories for trend
            top_5_cats = expense_df.groupby("Category")["Amount"].sum().nlargest(5).index.tolist()
            
            expense_df["Month"] = expense_df["Date"].dt.to_period("M").astype(str)
            
            trend_df = expense_df[expense_df["Category"].isin(top_5_cats)]
            monthly_trend = trend_df.groupby(["Month", "Category"])["Amount"].sum().unstack(fill_value=0)
            
            if not monthly_trend.empty:
                fig = px.line(
                    monthly_trend,
                    markers=True,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title="Month",
                    yaxis_title=f"Spending ({CURRENCY_SYMBOL})",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Category statistics table
            st.markdown("---")
            st.markdown("#### 📋 Detailed Category Statistics")
            
            category_stats = expense_df.groupby("Category").agg({
                "Amount": ["sum", "mean", "count", "min", "max"]
            }).round(2)
            
            category_stats.columns = ["Total", "Average", "Count", "Min", "Max"]
            category_stats = category_stats.sort_values("Total", ascending=False)
            
            # Format currency columns
            for col in ["Total", "Average", "Min", "Max"]:
                category_stats[col] = category_stats[col].apply(lambda x: format_currency(x))
            
            st.dataframe(category_stats, use_container_width=True)
        else:
            st.info("No expense transactions to analyze.")
    else:
        st.info("No transactions recorded yet. Start adding transactions to see category statistics!")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280;'>
    <p>📂 Well-organized categories make budgeting easier!</p>
    <p>© 2025 {DEVELOPER_NAME}</p>
</div>
""", unsafe_allow_html=True)
