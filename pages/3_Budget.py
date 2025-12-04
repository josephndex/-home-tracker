"""
Budget Management Page - Set and track monthly budgets
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, CURRENCY_SYMBOL
from auth import require_authentication, get_current_user, log_page_visit
from utils import (
    load_categories, load_transactions, format_currency, get_category_id,
    get_budget, set_budget, show_success_message, show_error_message
)

# Require authentication
require_authentication()
log_page_visit("3_Budget.py")

user = get_current_user()
user_id = user.get('id') if user else None

st.title("💰 Budget Management")

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
    padding: 1rem; border-radius: 12px; border-left: 4px solid #f43f5e; margin-bottom: 1rem;'>
    <p style='color: #e2e8f0; margin: 0;'>
        Set monthly budgets for each category and track your spending against them.
    </p>
</div>
""", unsafe_allow_html=True)

# Load data
df_data = load_transactions()
categories = load_categories()

# Tabs
tab1, tab2 = st.tabs(["📊 Budget Overview", "⚙️ Set Budgets"])

with tab1:
    st.markdown("### 📊 Monthly Budget Overview")
    
    # Month/Year selector
    col1, col2 = st.columns(2)
    
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    with col1:
        years = list(range(current_year - 2, current_year + 2))
        selected_year = st.selectbox("Year", years, index=years.index(current_year))
    
    with col2:
        months = list(range(1, 13))
        selected_month = st.selectbox(
            "Month",
            months,
            index=current_month - 1,
            format_func=lambda x: datetime(2000, x, 1).strftime("%B")
        )
    
    # Get budget data for each category
    budget_data = []
    total_budget = 0
    total_spent = 0
    
    for category in categories:
        category_id = get_category_id(category)
        if category_id:
            budget_amount = get_budget(category_id, selected_month, selected_year, user_id)
            
            # Get spent amount for this category
            if not df_data.empty:
                category_expenses = df_data[
                    (df_data["Date"].dt.year == selected_year) &
                    (df_data["Date"].dt.month == selected_month) &
                    (df_data["Type"] == "Expense") &
                    (df_data["Category"] == category)
                ]["Amount"].sum()
            else:
                category_expenses = 0
            
            remaining = budget_amount - category_expenses
            progress = (category_expenses / budget_amount * 100) if budget_amount > 0 else 0
            
            budget_data.append({
                "Category": category,
                "Budget": budget_amount,
                "Spent": category_expenses,
                "Remaining": remaining,
                "Progress": min(progress, 100)
            })
            
            total_budget += budget_amount
            total_spent += category_expenses
    
    # Overall summary
    st.markdown("### 📈 Overall Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Budget", format_currency(total_budget))
    
    with col2:
        st.metric("💸 Total Spent", format_currency(total_spent))
    
    with col3:
        remaining = total_budget - total_spent
        delta_color = "normal" if remaining >= 0 else "inverse"
        st.metric("🎯 Remaining", format_currency(remaining))
    
    with col4:
        if total_budget > 0:
            usage = (total_spent / total_budget) * 100
            st.metric("📈 Usage", f"{usage:.1f}%")
        else:
            st.metric("📈 Usage", "0%")
    
    # Progress bar
    if total_budget > 0:
        progress = min(total_spent / total_budget, 1.0)
        st.progress(progress, text=f"Budget Usage: {progress*100:.1f}%")
        
        if progress >= 1:
            st.error("⚠️ You've exceeded your monthly budget!")
        elif progress >= 0.8:
            st.warning("⚠️ You're approaching your budget limit.")
        else:
            st.success("🎉 Great job staying within budget!")
    
    st.markdown("---")
    
    # Category breakdown
    st.markdown("### 📋 Category Breakdown")
    
    budget_df = pd.DataFrame(budget_data)
    
    if not budget_df.empty and budget_df["Budget"].sum() > 0:
        # Display table
        display_df = budget_df.copy()
        display_df["Budget"] = display_df["Budget"].apply(lambda x: format_currency(x))
        display_df["Spent"] = display_df["Spent"].apply(lambda x: format_currency(x))
        display_df["Remaining"] = display_df["Remaining"].apply(lambda x: format_currency(x))
        display_df["Progress"] = display_df["Progress"].apply(lambda x: f"{x:.1f}%")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Budget vs Spent")
            
            # Filter only categories with budget
            chart_df = budget_df[budget_df["Budget"] > 0]
            
            if not chart_df.empty:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Budget',
                    x=chart_df['Category'],
                    y=chart_df['Budget'],
                    marker_color='#10b981'
                ))
                
                fig.add_trace(go.Bar(
                    name='Spent',
                    x=chart_df['Category'],
                    y=chart_df['Spent'],
                    marker_color='#ef4444'
                ))
                
                fig.update_layout(
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    margin=dict(t=20, b=100)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Budget Progress")
            
            chart_df = budget_df[budget_df["Budget"] > 0]
            
            if not chart_df.empty:
                fig = px.bar(
                    chart_df,
                    x="Category",
                    y="Progress",
                    color="Progress",
                    color_continuous_scale=["green", "yellow", "red"],
                    range_color=[0, 100]
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis=dict(tickangle=-45),
                    yaxis=dict(title="Usage %"),
                    margin=dict(t=20, b=100),
                    coloraxis_showscale=False
                )
                
                # Add threshold line
                fig.add_hline(y=80, line_dash="dash", line_color="orange", 
                            annotation_text="Warning (80%)")
                fig.add_hline(y=100, line_dash="dash", line_color="red",
                            annotation_text="Limit (100%)")
                
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No budgets set yet. Go to 'Set Budgets' tab to configure your monthly budgets.")

with tab2:
    st.markdown("### ⚙️ Set Monthly Budgets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        budget_year = st.selectbox(
            "Budget Year",
            list(range(current_year - 1, current_year + 2)),
            index=1,
            key="budget_set_year"
        )
    
    with col2:
        budget_month = st.selectbox(
            "Budget Month",
            list(range(1, 13)),
            index=current_month - 1,
            format_func=lambda x: datetime(2000, x, 1).strftime("%B"),
            key="budget_set_month"
        )
    
    st.markdown(f"**Setting budgets for {datetime(budget_year, budget_month, 1).strftime('%B %Y')}**")
    
    st.markdown("---")
    
    # Budget input form
    with st.form("budget_form"):
        st.markdown("#### Enter Budget for Each Category")
        
        budget_inputs = {}
        
        # Create columns for better layout
        cols = st.columns(3)
        
        for i, category in enumerate(categories):
            col_idx = i % 3
            category_id = get_category_id(category)
            
            if category_id:
                current_budget = get_budget(category_id, budget_month, budget_year, user_id)
                
                with cols[col_idx]:
                    budget_inputs[category] = st.number_input(
                        f"{category}",
                        min_value=0.0,
                        value=float(current_budget),
                        step=100.0,
                        format="%.2f",
                        key=f"budget_{category}"
                    )
        
        st.markdown("---")
        
        submitted = st.form_submit_button("💾 Save All Budgets", use_container_width=True, type="primary")
        
        if submitted:
            success_count = 0
            error_count = 0
            
            for category, amount in budget_inputs.items():
                category_id = get_category_id(category)
                if category_id:
                    success, _ = set_budget(category_id, budget_month, budget_year, amount, user_id)
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
            
            if success_count > 0:
                show_success_message(f"Saved {success_count} budgets!")
                st.rerun()
            if error_count > 0:
                show_error_message(f"Failed to save {error_count} budgets")
    
    st.markdown("---")
    
    # Quick templates
    st.markdown("### 🚀 Quick Budget Templates")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**💰 Conservative**")
        st.caption("Basic essentials only")
        if st.button("Apply Conservative", use_container_width=True):
            # Apply conservative budget
            templates = {
                "Groceries": 5000,
                "Vegetables": 2000,
                "Meat & Poultry": 3000,
                "Utilities (Water)": 1500,
                "Utilities (Electricity)": 2500,
                "Transportation": 3000
            }
            for cat, amt in templates.items():
                cat_id = get_category_id(cat)
                if cat_id:
                    set_budget(cat_id, budget_month, budget_year, amt, user_id)
            show_success_message("Conservative template applied!")
            st.rerun()
    
    with col2:
        st.markdown("**💸 Moderate**")
        st.caption("Balanced spending")
        if st.button("Apply Moderate", use_container_width=True):
            templates = {
                "Groceries": 10000,
                "Vegetables": 4000,
                "Meat & Poultry": 6000,
                "Fish & Seafood": 3000,
                "Fruits": 2000,
                "Utilities (Water)": 2500,
                "Utilities (Electricity)": 4000,
                "Transportation": 5000,
                "Cleaning Supplies": 2000
            }
            for cat, amt in templates.items():
                cat_id = get_category_id(cat)
                if cat_id:
                    set_budget(cat_id, budget_month, budget_year, amt, user_id)
            show_success_message("Moderate template applied!")
            st.rerun()
    
    with col3:
        st.markdown("**🎯 Comfortable**")
        st.caption("Full household needs")
        if st.button("Apply Comfortable", use_container_width=True):
            templates = {
                "Groceries": 15000,
                "Vegetables": 6000,
                "Meat & Poultry": 10000,
                "Fish & Seafood": 5000,
                "Fruits": 4000,
                "Dairy & Eggs": 3000,
                "Beverages": 3000,
                "Cooking Gas": 2500,
                "Utilities (Water)": 3500,
                "Utilities (Electricity)": 6000,
                "Transportation": 8000,
                "Cleaning Supplies": 3000,
                "Kitchen Supplies": 2000
            }
            for cat, amt in templates.items():
                cat_id = get_category_id(cat)
                if cat_id:
                    set_budget(cat_id, budget_month, budget_year, amt, user_id)
            show_success_message("Comfortable template applied!")
            st.rerun()

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280;'>
    <p>💡 Tip: Set realistic budgets based on your income and past spending patterns.</p>
    <p>© 2025 {DEVELOPER_NAME}</p>
</div>
""", unsafe_allow_html=True)
