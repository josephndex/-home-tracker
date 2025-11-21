import streamlit as st
import pandas as pd
from config import *

st.set_page_config(page_title=APP_TITLE, layout=PAGE_LAYOUT, page_icon=APP_ICON)

# Create navigation pages
home_page = st.Page("home.py", title="🏠 Home", default=True)
about_page = st.Page("about.py", title="ℹ️ About")  
expense_add_page = st.Page("add_expense.py", title="➕ Add Expense")
budget_page = st.Page("budget.py", title="💰 Budget")
report_page = st.Page("report.py", title="📊 Reports")      
statistics_page = st.Page("statistics.py", title="📈 Statistics")
monthly_page = st.Page("monthly.py", title="📅 Monthly Data") 
goals_page = st.Page("goal.py", title="🎯 Goals")
categories_page = st.Page("categories.py", title="🏷️ Categories")
guidelines_page = st.Page("guidelines.py", title="📘 Guidelines")
    
# Create navigation with organized groups
pg = st.navigation(pages=[
    home_page, 
    about_page, 
    expense_add_page, 
    budget_page, 
    report_page, 
    statistics_page,
    monthly_page, 
    goals_page, 
    categories_page,
    guidelines_page
])

# Enhanced sidebar with quick stats
with st.sidebar:  
    # Quick stats in sidebar
    try:
        from utils import load_expense_data, get_total_balance, format_currency
        df_data = load_expense_data()
        if not df_data.empty and 'Date' in df_data.columns:
            # Ensure Date column is datetime
            df_data['Date'] = pd.to_datetime(df_data['Date'], errors='coerce')
            df_data = df_data.dropna(subset=['Date'])
            
            if not df_data.empty:
                total_balance = get_total_balance(df_data)
                st.metric("💰 Total Balance", format_currency(total_balance))
    except Exception as e:
        pass  
    
    # Quick actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Quick Add", use_container_width=True,type="tertiary"):
            st.switch_page("add_expense.py")
    with col2:
        if st.button("📊 Reports", use_container_width=True,type="tertiary"):
            st.switch_page("report.py")

    st.markdown("---")
    st.caption(f"© {DEVELOPER_NAME} • All rights reserved")

pg.run()
