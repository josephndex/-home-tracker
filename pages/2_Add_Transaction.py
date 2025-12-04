"""
Add Transaction Page - Add Budget or Expense
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME
from auth import require_authentication, get_current_user, log_page_visit
from utils import (
    load_categories, add_transaction, load_transactions, delete_transaction,
    format_currency, show_success_message, show_error_message
)

# Require authentication
require_authentication()
log_page_visit("2_Add_Transaction.py")

user = get_current_user()
user_id = user.get('id') if user else None

st.title("➕ Add Budget or Expense")

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
    padding: 1rem; border-radius: 12px; border-left: 4px solid #14b8a6; margin-bottom: 1rem;'>
    <p style='color: #e2e8f0; margin: 0;'>
        Track your household finances by adding budget allocations and expense records.
    </p>
</div>
""", unsafe_allow_html=True)

# Tabs for different functions
tab1, tab2, tab3 = st.tabs(["➕ Add Entry", "📄 Transactions", "📁 Import/Export"])

with tab1:
    st.markdown("### Add New Transaction")
    
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            entry_type = st.selectbox(
                "Transaction Type",
                ["Expense", "Budget"],
                help="Select whether this is a budget allocation or an expense"
            )
        
        with col2:
            categories = load_categories()
            category = st.selectbox(
                "Category",
                categories,
                help="Select the category for this transaction"
            )
        
        col3, col4 = st.columns(2)
        
        with col3:
            amount = st.number_input(
                "💰 Amount (KSH)",
                min_value=0.01,
                max_value=10000000.0,
                format="%.2f",
                help="Enter the transaction amount"
            )
        
        with col4:
            trans_date = st.date_input(
                "📅 Transaction Date",
                value=datetime.now().date(),
                format="YYYY-MM-DD",
                help="Select the date of this transaction"
            )
        
        description = st.text_input(
            "📝 Description (optional)",
            placeholder="e.g., Weekly groceries at Naivas",
            max_chars=200,
            help="Add a brief description for this transaction"
        )
        
        submitted = st.form_submit_button("💾 Save Transaction", use_container_width=True, type="primary")
        
        if submitted:
            if amount <= 0:
                show_error_message("Please enter a valid amount")
            else:
                success, message = add_transaction(
                    transaction_date=trans_date,
                    transaction_type=entry_type,
                    amount=amount,
                    category=category,
                    description=description,
                    user_id=user_id
                )
                
                if success:
                    show_success_message(message)
                    st.balloons()
                    st.rerun()
                else:
                    show_error_message(message)

with tab2:
    st.markdown("### Recent Transactions")
    
    df_data = load_transactions()
    
    if df_data.empty:
        st.info("No transactions yet. Start by adding one above!")
    else:
        # Filter options
        st.markdown("#### 🗂️ Filter By")
        filter_option = st.radio(
            "Select time range:",
            ["This Week", "This Month", "This Year", "All Time", "Custom Range"],
            horizontal=True
        )
        
        today = datetime.now()
        
        if filter_option == "This Week":
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif filter_option == "This Month":
            start_date = today.replace(day=1)
            end_date = today
        elif filter_option == "This Year":
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif filter_option == "All Time":
            start_date = df_data["Date"].min()
            end_date = today
        else:  # Custom Range
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("📅 From Date", value=today.replace(day=1))
            with col2:
                end_date = st.date_input("📅 To Date", value=today)
        
        # Filter data
        df_data["Date"] = pd.to_datetime(df_data["Date"], errors="coerce")
        start_cmp = pd.to_datetime(start_date)
        end_cmp = pd.to_datetime(end_date) + timedelta(days=1)
        
        mask = (df_data["Date"] >= start_cmp) & (df_data["Date"] < end_cmp)
        filtered_data = df_data.loc[mask].sort_values(by="Date", ascending=False).copy()
        
        if filtered_data.empty:
            st.info(f"No transactions from {start_date} to {end_date}")
        else:
            # Summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", len(filtered_data))
            with col2:
                total_budget = filtered_data[filtered_data["Type"] == "Budget"]["Amount"].sum()
                st.metric("Total Budget", format_currency(total_budget))
            with col3:
                total_expense = filtered_data[filtered_data["Type"] == "Expense"]["Amount"].sum()
                st.metric("Total Expenses", format_currency(total_expense))
            with col4:
                st.metric("Net", format_currency(total_budget - total_expense))
            
            # Display data
            display_df = filtered_data.copy()
            display_df["Date"] = pd.to_datetime(display_df["Date"]).dt.strftime('%d %b %Y')
            display_df["Amount"] = display_df["Amount"].apply(lambda x: format_currency(x))
            
            st.dataframe(
                display_df[["Date", "Type", "Category", "Amount", "Description"]],
                use_container_width=True,
                hide_index=True
            )
            
            # Delete functionality
            st.markdown("---")
            st.markdown("#### 🗑️ Delete Transaction")
            
            def format_row(i):
                try:
                    row = filtered_data.loc[i]
                    date_str = pd.to_datetime(row['Date']).strftime('%d %b %Y')
                    return f"{date_str} | {row['Type']} | {row['Category']} | KSH {row['Amount']:,.2f}"
                except:
                    return str(i)
            
            delete_idx = st.selectbox(
                "Select transaction to delete:",
                options=filtered_data.index.tolist(),
                format_func=format_row
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Delete Selected", type="secondary"):
                    trans_id = filtered_data.loc[delete_idx, 'id']
                    success, message = delete_transaction(int(trans_id))
                    if success:
                        show_success_message(message)
                        st.rerun()
                    else:
                        show_error_message(message)
            
            # Download
            st.markdown("---")
            csv = filtered_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Transactions (CSV)",
                data=csv,
                file_name=f"transactions_{start_date}_to_{end_date}.csv",
                mime='text/csv'
            )

with tab3:
    st.markdown("### 📁 Import/Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📥 Download Sample CSV")
        st.markdown("Download a sample CSV with the correct format.")
        
        sample_data = pd.DataFrame({
            "Date": ["2025-01-15", "2025-01-16", "2025-01-17"],
            "Type": ["Expense", "Budget", "Expense"],
            "Category": ["Groceries", "Groceries", "Vegetables"],
            "Amount": [1500.0, 10000.0, 500.0],
            "Description": ["Weekly shopping", "Monthly budget", "Fresh vegetables"]
        })
        
        csv_sample = sample_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Sample",
            data=csv_sample,
            file_name="sample_transactions.csv",
            mime="text/csv"
        )
        
        st.markdown("""
        **CSV Format:**
        - Date: YYYY-MM-DD
        - Type: "Budget" or "Expense"
        - Category: Category name
        - Amount: Numeric value
        - Description: Optional text
        """)
    
    with col2:
        st.markdown("#### 📤 Upload & Import CSV")
        st.markdown("Upload a CSV file to import transactions.")
        
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                required_columns = ["Date", "Type", "Category", "Amount"]
                missing = [col for col in required_columns if col not in uploaded_df.columns]
                
                if missing:
                    st.error(f"Missing columns: {', '.join(missing)}")
                else:
                    st.markdown("**Preview:**")
                    st.dataframe(uploaded_df.head(), use_container_width=True, hide_index=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Records", len(uploaded_df))
                    with col2:
                        st.metric("Budget", len(uploaded_df[uploaded_df["Type"] == "Budget"]))
                    with col3:
                        st.metric("Expenses", len(uploaded_df[uploaded_df["Type"] == "Expense"]))
                    
                    if st.button("🔄 Import Data", type="primary"):
                        success_count = 0
                        error_count = 0
                        
                        for _, row in uploaded_df.iterrows():
                            try:
                                success, _ = add_transaction(
                                    transaction_date=pd.to_datetime(row['Date']).date(),
                                    transaction_type=row['Type'],
                                    amount=float(row['Amount']),
                                    category=row['Category'],
                                    description=row.get('Description', ''),
                                    user_id=user_id
                                )
                                if success:
                                    success_count += 1
                                else:
                                    error_count += 1
                            except:
                                error_count += 1
                        
                        if success_count > 0:
                            show_success_message(f"Imported {success_count} records!")
                        if error_count > 0:
                            show_error_message(f"Failed to import {error_count} records")
                        
                        st.rerun()
            
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

# Footer
st.markdown("---")
st.caption(f"© 2025 {DEVELOPER_NAME}")
