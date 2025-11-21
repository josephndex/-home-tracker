import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils import *
from config import *

st.title("💰 Budget Management")

# Load data
df_data = load_cached_expense_data()

# Budget persistence helpers
def load_budgets():
    try:
        if os.path.exists(BUDGETS_FILE):
            df = pd.read_csv(BUDGETS_FILE)
            return {row['Category']: float(row['Budget']) for _, row in df.iterrows()}
    except Exception:
        pass
    return {}

def save_budgets(budgets_dict):
    try:
        df = pd.DataFrame([(k, v) for k, v in budgets_dict.items()], columns=["Category", "Budget"])
        df.to_csv(BUDGETS_FILE, index=False)
    except Exception:
        pass

# Budget storage in session state (backed by CSV)
if 'budgets' not in st.session_state:
    st.session_state.budgets = load_budgets()

# Budget management functions
def save_budget(category, amount):
    """Save budget for a category"""
    st.session_state.budgets[category] = amount
    save_budgets(st.session_state.budgets)

def get_budget(category):
    """Get budget for a category"""
    return st.session_state.budgets.get(category, 0)

def get_spent_amount(df, category, year, month):
    """Get amount spent in a category for a specific month"""
    filtered_df = df[(df["Date"].dt.year == year) & 
                     (df["Date"].dt.month == month) & 
                     (df["Type"] == "Expense") & 
                     (df["Category"] == category)]
    return filtered_df["Amount"].sum()

def calculate_budget_progress(budget, spent):
    """Calculate budget progress percentage"""
    if budget == 0:
        return 0
    return min(100, (spent / budget) * 100)

# Main budget interface
tab1, tab2 = st.tabs(["📊 Budget Overview", "⚙️ Set Budgets"])

with tab1:
    st.subheader("📊 Monthly Budget Overview")
    
    # Month/Year selector
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Year", sorted(df_data["Date"].dt.year.unique(), reverse=True))
    with col2:
        selected_month = st.selectbox("Month", range(1, 13), format_func=lambda x: datetime(2000, x, 1).strftime("%B"))
    
    # Get current month's data
    current_month_data = df_data[(df_data["Date"].dt.year == selected_year) & 
                                (df_data["Date"].dt.month == selected_month)]
    
    if current_month_data.empty:
        show_info_message("No data available for selected month.")
    else:
        # Overall budget summary
        st.markdown("### 📈 Overall Budget Summary")
        
        total_budget = sum(st.session_state.budgets.values())
        total_spent = current_month_data[current_month_data["Type"] == "Expense"]["Amount"].sum()
        total_income = current_month_data[current_month_data["Type"] == "Income"]["Amount"].sum()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            create_metric_card("💰 Total Income", total_income)
        with col2:
            create_metric_card("💸 Total Spent", total_spent)
        with col3:
            create_metric_card("📊 Total Budget", total_budget)
        with col4:
            remaining = total_budget - total_spent
            delta_color = "normal" if remaining >= 0 else "inverse"
            create_metric_card("🎯 Remaining", remaining, delta_color=delta_color)
        
        # Budget progress bar
        if total_budget > 0:
            progress = calculate_budget_progress(total_budget, total_spent)
            st.progress(progress / 100, text=f"Budget Usage: {progress:.1f}%")
            
            if progress > 100:
                show_warning_message("⚠️ You've exceeded your monthly budget!")
            elif progress > 80:
                show_warning_message("⚠️ You're approaching your budget limit.")
            else:
                show_success_message("🎉 Great job staying within budget!")
        
        # Category-wise budget tracking
        st.markdown("### 📋 Category-wise Budget Tracking")
        
        if st.session_state.budgets:
            budget_data = []
            for category, budget_amount in st.session_state.budgets.items():
                spent_amount = get_spent_amount(df_data, category, selected_year, selected_month)
                progress = calculate_budget_progress(budget_amount, spent_amount)
                
                budget_data.append({
                    "Category": category,
                    "Budget": budget_amount,
                    "Spent": spent_amount,
                    "Remaining": budget_amount - spent_amount,
                    "Progress": progress
                })
            
            budget_df = pd.DataFrame(budget_data)
            
            # Display budget table
            st.dataframe(
                budget_df.style.format({
                    "Budget": lambda x: format_currency(x),
                    "Spent": lambda x: format_currency(x),
                    "Remaining": lambda x: format_currency(x),
                    "Progress": lambda x: f"{x:.1f}%"
                }),
                use_container_width=True,
                hide_index=True
            )
            
            # Budget vs Spent chart
            fig = px.bar(
                budget_df, 
                x="Category", 
                y=["Budget", "Spent"],
                title="Budget vs Spent by Category",
                barmode="group"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Progress chart
            fig_progress = px.bar(
                budget_df,
                x="Category",
                y="Progress",
                title="Budget Progress by Category (%)",
                color="Progress",
                color_continuous_scale=["green", "yellow", "red"]
            )
            st.plotly_chart(fig_progress, use_container_width=True)
        else:
            show_info_message("No budgets set. Go to 'Set Budgets' tab to create budgets.")

with tab2:
    st.subheader("⚙️ Set Monthly Budgets")
    
    # Budget setting interface
    st.markdown("Set your monthly budget for each category:")
    
    # Get unique categories from data
    all_categories = sorted(df_data["Category"].unique())
    
    # Create budget inputs for each category
    for category in all_categories:
        current_budget = get_budget(category)
        new_budget = st.number_input(
            f"Budget for {category} ({CURRENCY})",
            min_value=0.0,
            value=float(current_budget),
            step=100.0,
            format="%.2f"
        )
        
        if new_budget != current_budget:
            save_budget(category, new_budget)
    
    # Quick budget templates
    st.markdown("### 🚀 Quick Budget Templates")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 Conservative Budget"):
            conservative_budgets = {
                "Food": 10000,
                "Transport": 5000,
                "Shopping": 7000,
                "Bills": 15000,
                "Utilities": 8000,
                "Others": 5000
            }
            for category, amount in conservative_budgets.items():
                save_budget(category, amount)
            show_success_message("Conservative budget template applied!")
    
    with col2:
        if st.button("💸 Moderate Budget"):
            moderate_budgets = {
                "Food": 20000,
                "Transport": 10000,
                "Shopping": 15000,
                "Bills": 25000,
                "Utilities": 15000,
                "Others": 10000
            }
            for category, amount in moderate_budgets.items():
                save_budget(category, amount)
            show_success_message("Moderate budget template applied!")
    
    with col3:
        if st.button("🎯 Custom Budget"):
            st.markdown("Enter your custom budget amounts:")
            custom_budget = {}
            for category in all_categories:
                amount = st.number_input(f"{category}", min_value=0.0, step=100.0)
                custom_budget[category] = amount
            
            if st.button("Apply Custom Budget"):
                for category, amount in custom_budget.items():
                    save_budget(category, amount)
                show_success_message("Custom budget applied!")
    
    # Budget recommendations
    st.markdown("### 💡 Budget Recommendations")
    
    if not df_data.empty:
        # Analyze spending patterns
        recent_data = df_data[df_data["Date"] >= datetime.now() - timedelta(days=90)]
        avg_spending = recent_data[recent_data["Type"] == "Expense"].groupby("Category")["Amount"].mean()
        
        st.markdown("Based on your recent spending patterns:")
        for category, avg_amount in avg_spending.items():
            recommended_budget = avg_amount * 1.2  # 20% buffer
            st.write(f"**{category}**: Average spending {format_currency(avg_amount)}, recommended budget {format_currency(recommended_budget)}")
    
    # Export/Import budgets
    st.markdown("### 📁 Budget Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export budgets
        if st.session_state.budgets:
            budget_export = pd.DataFrame(list(st.session_state.budgets.items()), columns=["Category", "Budget"])
            csv = budget_export.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Export Budgets",
                data=csv,
                file_name="budgets.csv",
                mime="text/csv"
            )
    
    with col2:
        # Import budgets
        uploaded_file = st.file_uploader("Import Budgets", type=['csv'])
        if uploaded_file is not None:
            try:
                budget_import = pd.read_csv(uploaded_file)
                for _, row in budget_import.iterrows():
                    save_budget(row['Category'], row['Budget'])
                show_success_message("Budgets imported successfully!")
            except Exception as e:
                show_error_message(f"Error importing budgets: {str(e)}")

# Footer
st.markdown("---")
st.markdown("💡 **Tip**: Set realistic budgets based on your income and spending patterns.")
