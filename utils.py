import streamlit as st
import pandas as pd
import os
import re
import shutil
from datetime import datetime, timedelta
from pandas.errors import EmptyDataError
from config import *

# ==================== CATEGORY MANAGEMENT ====================
def load_categories():
    """Load categories from CSV file"""
    try:
        if os.path.exists(CATEGORIES_FILE):
            df = pd.read_csv(CATEGORIES_FILE)
            return df["Category"].tolist()
    except (FileNotFoundError, EmptyDataError):
        pass
    # Return default categories if file doesn't exist
    save_categories(DEFAULT_CATEGORIES)
    return DEFAULT_CATEGORIES

def save_categories(categories):
    """Save categories to CSV file"""
    df = pd.DataFrame({"Category": categories})
    df.to_csv(CATEGORIES_FILE, index=False)

def add_category(category_name):
    """Add a new category"""
    categories = load_categories()
    category_name = sanitize_input(category_name).strip()
    
    if not category_name:
        return False, "Category name cannot be empty"
    
    if len(category_name) > MAX_CATEGORY_LENGTH:
        return False, f"Category name must be less than {MAX_CATEGORY_LENGTH} characters"
    
    if category_name in categories:
        return False, "Category already exists"
    
    categories.append(category_name)
    save_categories(categories)
    return True, "Category added successfully"

def delete_category(category_name):
    """Delete a category"""
    categories = load_categories()
    
    if category_name not in categories:
        return False, "Category not found"
    
    if category_name in DEFAULT_CATEGORIES:
        return False, "Cannot delete default categories"
    
    # Check if category is being used in expenses
    df = load_expense_data()
    if not df.empty and category_name in df["Category"].values:
        return False, "Cannot delete category that has transactions. Please reassign or delete those transactions first."
    
    categories.remove(category_name)
    save_categories(categories)
    return True, "Category deleted successfully"

def rename_category(old_name, new_name):
    """Rename a category and update all associated transactions"""
    categories = load_categories()
    new_name = sanitize_input(new_name).strip()
    
    if not new_name:
        return False, "New category name cannot be empty"
    
    if len(new_name) > MAX_CATEGORY_LENGTH:
        return False, f"Category name must be less than {MAX_CATEGORY_LENGTH} characters"
    
    if old_name not in categories:
        return False, "Original category not found"
    
    if new_name in categories and new_name != old_name:
        return False, "New category name already exists"
    
    # Update category list
    categories = [new_name if cat == old_name else cat for cat in categories]
    save_categories(categories)
    
    # Update all transactions with this category
    df = load_expense_data()
    if not df.empty:
        df.loc[df["Category"] == old_name, "Category"] = new_name
        save_expense_data(df)
    
    return True, "Category renamed successfully"

# ==================== DATA LOADING AND SAVING ====================
def load_expense_data():
    """Load expense data from CSV with proper error handling"""
    try:
        df = pd.read_csv(EXPENSE_FILE)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date"])  # Remove invalid date rows
        return df
    except (FileNotFoundError, EmptyDataError):
        return pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Description"])

def save_expense_data(df):
    """Save expense data to CSV"""
    df.to_csv(EXPENSE_FILE, index=False)

def load_goals_data():
    """Load goals data from CSV"""
    try:
        return pd.read_csv(GOALS_FILE, parse_dates=["Deadline"])
    except (FileNotFoundError, EmptyDataError):
        return pd.DataFrame(columns=["Goal", "Target Amount", "Amount Saved", "Deadline"])

def save_goals_data(df):
    """Save goals data to CSV"""
    df.to_csv(GOALS_FILE, index=False)

# Validation functions
def validate_amount(amount):
    """Validate amount input"""
    try:
        amount = float(amount)
        return MIN_AMOUNT <= amount <= MAX_AMOUNT
    except (ValueError, TypeError):
        return False

def validate_category(category):
    """Validate category input"""
    if not category or not str(category).strip():
        return False
    return len(str(category).strip()) <= 50

def validate_description(description):
    """Validate description input"""
    if description is None:
        return True  # Description is optional
    return len(str(description)) <= MAX_DESCRIPTION_LENGTH

def sanitize_input(text):
    """Remove potentially harmful characters"""
    if text is None:
        return ""
    return re.sub(r'[<>"\']', '', str(text))

def validate_entry(amount, category, description=""):
    """Validate complete entry"""
    errors = []
    
    if not validate_amount(amount):
        errors.append(f"Amount must be between {MIN_AMOUNT} and {MAX_AMOUNT}")
    
    if not validate_category(category):
        errors.append("Category is required and must be less than 50 characters")
    
    if not validate_description(description):
        errors.append(f"Description must be less than {MAX_DESCRIPTION_LENGTH} characters")
    
    return errors

# Data analysis functions
def get_monthly_summary(df, year, month):
    """Get monthly summary for specific year and month"""
    filtered_df = df[(df["Date"].dt.year == year) & (df["Date"].dt.month == month)]
    
    budget = filtered_df[filtered_df["Type"] == "Budget"]["Amount"].sum()
    expense = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
    net = budget - expense
    
    return {
        "budget": budget,
        "expense": expense,
        "net": net,
        "transactions": len(filtered_df)
    }

def get_total_balance(df):
    """Calculate total balance (budget - expenses)"""
    budget = df[df["Type"] == "Budget"]["Amount"].sum()
    expense = df[df["Type"] == "Expense"]["Amount"].sum()
    return budget - expense

def get_top_spending_category(df, months=1):
    """Get top spending category for the last N months"""
    cutoff_date = datetime.now() - timedelta(days=30*months)
    recent_df = df[df["Date"] >= cutoff_date]
    expense_df = recent_df[recent_df["Type"] == "Expense"]
    
    if expense_df.empty:
        return "No expenses"
    
    top_category = expense_df.groupby("Category")["Amount"].sum().idxmax()
    return top_category

def get_average_daily_spending(df, days=30):
    """Calculate average daily spending"""
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_df = df[df["Date"] >= cutoff_date]
    expense_df = recent_df[recent_df["Type"] == "Expense"]
    
    if expense_df.empty:
        return 0
    
    total_expense = expense_df["Amount"].sum()
    return total_expense / days

# Backup functions
def create_backup():
    """Create automatic backup of data files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup expense file
    if os.path.exists(EXPENSE_FILE):
        backup_expense = f"{BACKUP_DIR}/expenses_backup_{timestamp}.csv"
        shutil.copy2(EXPENSE_FILE, backup_expense)
    
    # Backup goals file
    if os.path.exists(GOALS_FILE):
        backup_goals = f"{BACKUP_DIR}/goals_backup_{timestamp}.csv"
        shutil.copy2(GOALS_FILE, backup_goals)
    
    return timestamp

def cleanup_old_backups(keep_days=30):
    """Remove backups older than specified days"""
    cutoff_time = datetime.now() - timedelta(days=keep_days)
    
    for filename in os.listdir(BACKUP_DIR):
        filepath = os.path.join(BACKUP_DIR, filename)
        if os.path.isfile(filepath):
            file_time = datetime.fromtimestamp(os.path.getctime(filepath))
            if file_time < cutoff_time:
                os.remove(filepath)

# UI helper functions
def format_currency(amount):
    """Format amount as currency"""
    return f"{CURRENCY_SYMBOL} {amount:,.2f}"

# ==================== ADVANCED ANALYTICS ====================
def get_daily_expense_trend(df, days=30):
    """Get daily expense trend for visualization"""
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_df = df[df["Date"] >= cutoff_date]
    expense_df = recent_df[recent_df["Type"] == "Expense"]
    
    if expense_df.empty:
        return pd.DataFrame()
    
    daily_expenses = expense_df.groupby("Date")["Amount"].sum().reset_index()
    return daily_expenses

def get_weekday_spending(df):
    """Analyze spending by day of the week"""
    expense_df = df[df["Type"] == "Expense"].copy()
    
    if expense_df.empty:
        return pd.DataFrame()
    
    expense_df["weekday"] = expense_df["Date"].dt.day_name()
    weekday_df = expense_df.groupby("weekday")["Amount"].sum().reset_index()
    
    # Order by day of week
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_df["weekday"] = pd.Categorical(weekday_df["weekday"], categories=weekday_order, ordered=True)
    weekday_df = weekday_df.sort_values("weekday")
    
    return weekday_df

def get_cumulative_spending(df):
    """Calculate cumulative spending over time"""
    expense_df = df[df["Type"] == "Expense"].copy()
    
    if expense_df.empty:
        return pd.DataFrame()
    
    daily_expenses = expense_df.groupby("Date")["Amount"].sum().reset_index()
    daily_expenses = daily_expenses.sort_values("Date")
    daily_expenses["cumulative"] = daily_expenses["Amount"].cumsum()
    
    return daily_expenses

def get_most_expensive_day(df):
    """Find the day with highest spending"""
    expense_df = df[df["Type"] == "Expense"]
    
    if expense_df.empty:
        return None, 0
    
    daily_expenses = expense_df.groupby("Date")["Amount"].sum()
    max_date = daily_expenses.idxmax()
    max_amount = daily_expenses.max()
    
    return max_date, max_amount

def get_category_statistics(df):
    """Get detailed statistics for each category"""
    expense_df = df[df["Type"] == "Expense"]
    
    if expense_df.empty:
        return pd.DataFrame()
    
    category_stats = expense_df.groupby("Category").agg({
        "Amount": ["sum", "mean", "count", "min", "max"]
    }).reset_index()
    
    category_stats.columns = ["Category", "Total", "Average", "Count", "Min", "Max"]
    category_stats = category_stats.sort_values("Total", ascending=False)
    
    return category_stats

def get_spending_insights(df):
    """Generate spending insights and recommendations"""
    insights = []
    
    if df.empty:
        return insights
    
    expense_df = df[df["Type"] == "Expense"]
    
    if expense_df.empty:
        return insights
    
    # Total spending
    total_expense = expense_df["Amount"].sum()
    
    # Category analysis
    category_sum = expense_df.groupby("Category")["Amount"].sum()
    top_category = category_sum.idxmax()
    top_percent = (category_sum.max() / total_expense) * 100
    
    if top_percent > 50:
        insights.append({
            "type": "warning",
            "message": f"⚠️ {top_percent:.1f}% of your expenses are in {top_category}. Consider reducing spending here."
        })
    
    # Average daily spending
    avg_daily = get_average_daily_spending(df)
    insights.append({
        "type": "info",
        "message": f"📊 Your average daily spending is {format_currency(avg_daily)}"
    })
    
    # Compare this month vs last month
    current_month = datetime.now().month
    current_year = datetime.now().year
    current_month_expense = df[
        (df["Date"].dt.year == current_year) & 
        (df["Date"].dt.month == current_month) & 
        (df["Type"] == "Expense")
    ]["Amount"].sum()
    
    last_month = current_month - 1 if current_month > 1 else 12
    last_year = current_year if current_month > 1 else current_year - 1
    last_month_expense = df[
        (df["Date"].dt.year == last_year) & 
        (df["Date"].dt.month == last_month) & 
        (df["Type"] == "Expense")
    ]["Amount"].sum()
    
    if last_month_expense > 0:
        change_percent = ((current_month_expense - last_month_expense) / last_month_expense) * 100
        if change_percent > 10:
            insights.append({
                "type": "warning",
                "message": f"📈 Your spending increased by {change_percent:.1f}% compared to last month"
            })
        elif change_percent < -10:
            insights.append({
                "type": "success",
                "message": f"📉 Great job! Your spending decreased by {abs(change_percent):.1f}% compared to last month"
            })
    
    return insights

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a styled metric card"""
    st.metric(
        label=title,
        value=format_currency(value),
        delta=format_currency(delta) if delta else None,
        delta_color=delta_color
    )

def show_success_message(message):
    """Show success message with consistent styling"""
    st.success(f"✅ {message}")

def show_error_message(message):
    """Show error message with consistent styling"""
    st.error(f"❌ {message}")

def show_warning_message(message):
    """Show warning message with consistent styling"""
    st.warning(f"⚠️ {message}")

def show_info_message(message):
    """Show info message with consistent styling"""
    st.info(f"ℹ️ {message}")

# Caching decorators
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_expense_data():
    """Cached version of load_expense_data"""
    return load_expense_data()

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_cached_monthly_summary(year, month):
    """Cached monthly summary calculation"""
    df = load_cached_expense_data()
    return get_monthly_summary(df, year, month)
