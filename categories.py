import streamlit as st
import pandas as pd
from utils import *
from config import *

st.title("🏷️ Category Management")

st.markdown("""
Manage your expense and income categories here. You can:
- ✅ View all existing categories
- ➕ Add new categories
- ✏️ Rename categories
- 🗑️ Delete unused categories
""")

st.markdown("---")

# Load current categories
categories = load_categories()
df = load_expense_data()

# ==================== VIEW CATEGORIES ====================
st.markdown("### 📋 Current Categories")

col1, col2 = st.columns([3, 1])

with col1:
    # Display categories with usage count
    if categories:
        category_data = []
        for cat in categories:
            count = len(df[df["Category"] == cat]) if not df.empty else 0
            is_default = "✅ Yes" if cat in DEFAULT_CATEGORIES else "No"
            category_data.append({
                "Category": cat,
                "Transactions": count,
                "Default": is_default
            })
        
        category_df = pd.DataFrame(category_data)
        st.dataframe(category_df, use_container_width=True, hide_index=True)
        
        st.caption(f"Total Categories: {len(categories)}")
    else:
        st.info("No categories found. Add your first category below!")

with col2:
    st.metric("📊 Total Categories", len(categories))
    if not df.empty:
        st.metric("📝 Total Transactions", len(df))

st.markdown("---")

# ==================== ADD NEW CATEGORY ====================
st.markdown("### ➕ Add New Category")

with st.form("add_category_form"):
    new_category = st.text_input(
        "Category Name",
        max_chars=MAX_CATEGORY_LENGTH,
        placeholder="Enter new category name (e.g., 'Groceries', 'Gym')"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        submit_add = st.form_submit_button("➕ Add Category", type="primary", use_container_width=True)
    
    if submit_add:
        if new_category:
            success, message = add_category(new_category)
            if success:
                show_success_message(message)
                st.rerun()
            else:
                show_error_message(message)
        else:
            show_error_message("Please enter a category name")

st.markdown("---")

# ==================== RENAME CATEGORY ====================
st.markdown("### ✏️ Rename Category")

with st.form("rename_category_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        old_category = st.selectbox(
            "Select Category to Rename",
            options=categories,
            key="rename_old"
        )
    
    with col2:
        new_category_name = st.text_input(
            "New Name",
            max_chars=MAX_CATEGORY_LENGTH,
            placeholder="Enter new category name"
        )
    
    submit_rename = st.form_submit_button("✏️ Rename Category", type="primary")
    
    if submit_rename:
        if old_category and new_category_name:
            success, message = rename_category(old_category, new_category_name)
            if success:
                show_success_message(message)
                st.info(f"ℹ️ All transactions with '{old_category}' have been updated to '{new_category_name}'")
                st.rerun()
            else:
                show_error_message(message)
        else:
            show_error_message("Please select a category and enter a new name")

st.markdown("---")

# ==================== DELETE CATEGORY ====================
st.markdown("### 🗑️ Delete Category")

st.warning("⚠️ **Warning**: Categories with existing transactions cannot be deleted. You must first reassign or delete those transactions.")

with st.form("delete_category_form"):
    delete_category_name = st.selectbox(
        "Select Category to Delete",
        options=[cat for cat in categories if cat not in DEFAULT_CATEGORIES],
        key="delete_cat"
    )
    
    # Show transaction count for selected category
    if delete_category_name and not df.empty:
        trans_count = len(df[df["Category"] == delete_category_name])
        if trans_count > 0:
            st.error(f"⚠️ This category has {trans_count} transaction(s). Cannot delete.")
        else:
            st.success("✅ This category has no transactions and can be safely deleted.")
    
    confirm_delete = st.checkbox("I understand this action cannot be undone")
    submit_delete = st.form_submit_button("🗑️ Delete Category", type="secondary")
    
    if submit_delete:
        if not confirm_delete:
            show_error_message("Please confirm deletion by checking the box")
        elif delete_category_name:
            success, message = delete_category(delete_category_name)
            if success:
                show_success_message(message)
                st.rerun()
            else:
                show_error_message(message)
        else:
            show_error_message("Please select a category to delete")

st.markdown("---")

# ==================== BULK OPERATIONS ====================
st.markdown("### 📦 Bulk Operations")

with st.expander("🔄 Reset to Default Categories"):
    st.warning("⚠️ This will reset all categories to the default list. Custom categories will be removed (if not in use).")
    
    if st.button("Reset Categories", type="secondary"):
        # Check if any custom categories are in use
        custom_cats = [cat for cat in categories if cat not in DEFAULT_CATEGORIES]
        in_use = []
        
        for cat in custom_cats:
            if not df.empty and cat in df["Category"].values:
                in_use.append(cat)
        
        if in_use:
            show_warning_message(f"Cannot reset: {', '.join(in_use)} are in use. These categories will be kept.")
            # Keep categories in use
            new_categories = list(set(DEFAULT_CATEGORIES + in_use))
            save_categories(new_categories)
            st.rerun()
        else:
            save_categories(DEFAULT_CATEGORIES)
            show_success_message("Categories reset to defaults!")
            st.rerun()

with st.expander("📥 Import Categories from CSV"):
    st.markdown("""
    Upload a CSV file with a single column named 'Category' containing category names.
    
    **CSV Format:**
    ```
    Category
    Groceries
    Gym
    Rent
    ```
    """)
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'], key="import_cat")
    
    if uploaded_file is not None:
        try:
            import_df = pd.read_csv(uploaded_file)
            
            if "Category" not in import_df.columns:
                show_error_message("CSV must have a 'Category' column")
            else:
                imported_cats = import_df["Category"].dropna().unique().tolist()
                
                st.write("**Preview of categories to import:**")
                st.write(", ".join(imported_cats))
                
                if st.button("Confirm Import"):
                    current_cats = load_categories()
                    new_cats = [cat for cat in imported_cats if cat not in current_cats]
                    
                    if new_cats:
                        all_cats = current_cats + new_cats
                        save_categories(all_cats)
                        show_success_message(f"Imported {len(new_cats)} new categories!")
                        st.rerun()
                    else:
                        show_info_message("All categories already exist!")
        except Exception as e:
            show_error_message(f"Error reading file: {str(e)}")

with st.expander("📤 Export Categories to CSV"):
    if categories:
        export_df = pd.DataFrame({"Category": categories})
        csv_data = export_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Download Categories",
            data=csv_data,
            file_name=f"categories_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No categories to export")

# ==================== CATEGORY USAGE ANALYTICS ====================
st.markdown("---")
st.markdown("### 📊 Category Usage Analytics")

if not df.empty:
    # Most used categories
    category_usage = df.groupby("Category").size().sort_values(ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔥 Most Used Categories")
        top_5 = category_usage.head(5)
        for cat, count in top_5.items():
            st.write(f"**{cat}**: {count} transactions")
    
    with col2:
        st.markdown("#### 💤 Least Used Categories")
        # Show categories with 0 transactions
        unused = [cat for cat in categories if cat not in df["Category"].values]
        if unused:
            for cat in unused[:5]:
                st.write(f"**{cat}**: 0 transactions")
        else:
            st.success("✅ All categories are being used!")
    
    # Visualize category usage
    import plotly.express as px
    
    usage_df = pd.DataFrame({
        "Category": category_usage.index,
        "Count": category_usage.values
    })
    
    fig = px.bar(
        usage_df.head(10),
        x="Category",
        y="Count",
        title="Top 10 Most Used Categories",
        color="Count",
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No transaction data available yet. Start adding expenses to see analytics!")

# Footer
st.markdown("---")
st.caption("💡 Tip: Keep your categories organized and relevant to your spending habits for better tracking!")
