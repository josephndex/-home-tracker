"""
Utility functions for HomeTracker - Smart Home Management System
Data operations, formatting, and helper functions
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Tuple, Any
from decimal import Decimal
import logging
from sqlalchemy import text

from database import get_db_manager
from config import CURRENCY_SYMBOL, DEFAULT_CATEGORIES, MAX_AMOUNT, MIN_AMOUNT, MAX_DESCRIPTION_LENGTH

logger = logging.getLogger(__name__)


# ==================== FORMATTING FUNCTIONS ====================

def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"{CURRENCY_SYMBOL} {amount:,.2f}"


def format_date(date_obj) -> str:
    """Format date for display."""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, "%Y-%m-%d")
        except:
            return date_obj
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime("%d %b %Y")
    return str(date_obj)


def format_datetime(dt_obj) -> str:
    """Format datetime for display."""
    if isinstance(dt_obj, str):
        try:
            dt_obj = datetime.fromisoformat(dt_obj)
        except:
            return dt_obj
    if hasattr(dt_obj, 'strftime'):
        return dt_obj.strftime("%d %b %Y %H:%M")
    return str(dt_obj)


# ==================== VALIDATION FUNCTIONS ====================

def validate_amount(amount) -> bool:
    """Validate amount input."""
    try:
        amount = float(amount)
        return MIN_AMOUNT <= amount <= MAX_AMOUNT
    except (ValueError, TypeError):
        return False


def validate_category(category) -> bool:
    """Validate category input."""
    if not category or not str(category).strip():
        return False
    return len(str(category).strip()) <= 50


def validate_description(description) -> bool:
    """Validate description input."""
    if description is None:
        return True
    return len(str(description)) <= MAX_DESCRIPTION_LENGTH


def validate_entry(amount, category, description="") -> List[str]:
    """Validate complete entry and return list of errors."""
    errors = []
    
    if not validate_amount(amount):
        errors.append(f"Amount must be between {MIN_AMOUNT} and {MAX_AMOUNT}")
    
    if not validate_category(category):
        errors.append("Category is required and must be less than 50 characters")
    
    if not validate_description(description):
        errors.append(f"Description must be less than {MAX_DESCRIPTION_LENGTH} characters")
    
    return errors


# ==================== CATEGORY FUNCTIONS ====================

def load_categories(db_config: int = 1) -> List[str]:
    """Load categories from database."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return DEFAULT_CATEGORIES
    
    try:
        query = text("SELECT name FROM ht_categories WHERE is_active = TRUE ORDER BY name")
        with db.engine.connect() as conn:
            result = conn.execute(query)
            categories = [row[0] for row in result.fetchall()]
        
        return categories if categories else DEFAULT_CATEGORIES
        
    except Exception as e:
        logger.error(f"Failed to load categories: {e}")
        return DEFAULT_CATEGORIES


def get_category_id(category_name: str, db_config: int = 1) -> Optional[int]:
    """Get category ID by name."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return None
    
    try:
        query = text("SELECT id FROM ht_categories WHERE name = :name")
        with db.engine.connect() as conn:
            result = conn.execute(query, {"name": category_name})
            row = result.fetchone()
            return row[0] if row else None
    except Exception as e:
        logger.error(f"Failed to get category ID: {e}")
        return None


def add_category(category_name: str, db_config: int = 1) -> Tuple[bool, str]:
    """Add a new category."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    category_name = category_name.strip()
    
    if not category_name:
        return False, "Category name cannot be empty"
    
    if len(category_name) > 50:
        return False, "Category name must be less than 50 characters"
    
    try:
        # Check if exists
        check_query = text("SELECT id FROM ht_categories WHERE name = :name")
        with db.engine.connect() as conn:
            result = conn.execute(check_query, {"name": category_name})
            if result.fetchone():
                return False, "Category already exists"
        
        # Insert new category
        insert_query = text("""
            INSERT INTO ht_categories (name, category_type, is_default, is_active)
            VALUES (:name, 'expense', FALSE, TRUE)
        """)
        with db.engine.connect() as conn:
            conn.execute(insert_query, {"name": category_name})
            conn.commit()
        
        return True, "Category added successfully"
        
    except Exception as e:
        logger.error(f"Failed to add category: {e}")
        return False, f"Error: {str(e)}"


def delete_category(category_name: str, db_config: int = 1) -> Tuple[bool, str]:
    """Delete a category (soft delete)."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        # Check if default
        check_query = text("SELECT is_default FROM ht_categories WHERE name = :name")
        with db.engine.connect() as conn:
            result = conn.execute(check_query, {"name": category_name})
            row = result.fetchone()
            if row and row[0]:
                return False, "Cannot delete default categories"
        
        # Check if in use
        usage_query = text("""
            SELECT COUNT(*) FROM ht_transactions t
            JOIN ht_categories c ON t.category_id = c.id
            WHERE c.name = :name
        """)
        with db.engine.connect() as conn:
            result = conn.execute(usage_query, {"name": category_name})
            count = result.fetchone()[0]
            if count > 0:
                return False, "Cannot delete category that has transactions"
        
        # Soft delete
        update_query = text("UPDATE ht_categories SET is_active = FALSE WHERE name = :name")
        with db.engine.connect() as conn:
            conn.execute(update_query, {"name": category_name})
            conn.commit()
        
        return True, "Category deleted successfully"
        
    except Exception as e:
        logger.error(f"Failed to delete category: {e}")
        return False, f"Error: {str(e)}"


# ==================== TRANSACTION FUNCTIONS ====================

def load_transactions(user_id: Optional[int] = None, db_config: int = 1) -> pd.DataFrame:
    """Load transactions from database."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Description"])
    
    try:
        query = text("""
            SELECT t.id, t.transaction_date as Date, t.transaction_type as Type, 
                   t.amount as Amount, c.name as Category, t.description as Description,
                   t.created_at, t.user_id
            FROM ht_transactions t
            LEFT JOIN ht_categories c ON t.category_id = c.id
            ORDER BY t.transaction_date DESC, t.created_at DESC
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
        
        if not rows:
            return pd.DataFrame(columns=["id", "Date", "Type", "Amount", "Category", "Description"])
        
        df = pd.DataFrame(rows, columns=["id", "Date", "Type", "Amount", "Category", "Description", "created_at", "user_id"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        
        return df
        
    except Exception as e:
        logger.error(f"Failed to load transactions: {e}")
        return pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Description"])


def add_transaction(transaction_date, transaction_type: str, amount: float, 
                   category: str, description: str = "", user_id: Optional[int] = None,
                   db_config: int = 1) -> Tuple[bool, str]:
    """Add a new transaction."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    # Validate
    errors = validate_entry(amount, category, description)
    if errors:
        return False, "; ".join(errors)
    
    try:
        # Get category ID
        category_id = get_category_id(category, db_config)
        
        insert_query = text("""
            INSERT INTO ht_transactions (user_id, transaction_date, transaction_type, 
                                        category_id, amount, description)
            VALUES (:user_id, :trans_date, :trans_type, :category_id, :amount, :description)
        """)
        
        with db.engine.connect() as conn:
            conn.execute(insert_query, {
                "user_id": user_id,
                "trans_date": transaction_date,
                "trans_type": transaction_type,
                "category_id": category_id,
                "amount": amount,
                "description": description
            })
            conn.commit()
        
        return True, f"{transaction_type} added successfully!"
        
    except Exception as e:
        logger.error(f"Failed to add transaction: {e}")
        return False, f"Error: {str(e)}"


def delete_transaction(transaction_id: int, db_config: int = 1) -> Tuple[bool, str]:
    """Delete a transaction."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        delete_query = text("DELETE FROM ht_transactions WHERE id = :id")
        with db.engine.connect() as conn:
            conn.execute(delete_query, {"id": transaction_id})
            conn.commit()
        
        return True, "Transaction deleted successfully"
        
    except Exception as e:
        logger.error(f"Failed to delete transaction: {e}")
        return False, f"Error: {str(e)}"


# ==================== ANALYTICS FUNCTIONS ====================

def get_monthly_summary(df: pd.DataFrame, year: int, month: int) -> Dict[str, Any]:
    """Get monthly summary for specific year and month."""
    if df.empty:
        return {"budget": 0, "expense": 0, "net": 0, "transactions": 0}
    
    filtered_df = df[(df["Date"].dt.year == year) & (df["Date"].dt.month == month)]
    
    budget = filtered_df[filtered_df["Type"] == "Budget"]["Amount"].sum()
    expense = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
    net = budget - expense
    
    return {
        "budget": float(budget),
        "expense": float(expense),
        "net": float(net),
        "transactions": len(filtered_df)
    }


def get_total_balance(df: pd.DataFrame) -> float:
    """Calculate total balance (budget - expenses)."""
    if df.empty:
        return 0.0
    
    budget = df[df["Type"] == "Budget"]["Amount"].sum()
    expense = df[df["Type"] == "Expense"]["Amount"].sum()
    return float(budget - expense)


def get_top_spending_category(df: pd.DataFrame, months: int = 1) -> str:
    """Get top spending category for the last N months."""
    if df.empty:
        return "No expenses"
    
    cutoff_date = datetime.now() - timedelta(days=30*months)
    recent_df = df[df["Date"] >= cutoff_date]
    expense_df = recent_df[recent_df["Type"] == "Expense"]
    
    if expense_df.empty:
        return "No expenses"
    
    top_category = expense_df.groupby("Category")["Amount"].sum().idxmax()
    return top_category


def get_average_daily_spending(df: pd.DataFrame, days: int = 30) -> float:
    """Calculate average daily spending."""
    if df.empty:
        return 0.0
    
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_df = df[df["Date"] >= cutoff_date]
    expense_df = recent_df[recent_df["Type"] == "Expense"]
    
    if expense_df.empty:
        return 0.0
    
    return float(expense_df["Amount"].sum() / days)


def get_category_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Get detailed statistics for each category."""
    if df.empty:
        return pd.DataFrame()
    
    expense_df = df[df["Type"] == "Expense"]
    
    if expense_df.empty:
        return pd.DataFrame()
    
    category_stats = expense_df.groupby("Category").agg({
        "Amount": ["sum", "mean", "count", "min", "max"]
    }).reset_index()
    
    category_stats.columns = ["Category", "Total", "Average", "Count", "Min", "Max"]
    category_stats = category_stats.sort_values("Total", ascending=False)
    
    return category_stats


def get_spending_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Generate spending insights and recommendations."""
    insights = []
    
    if df.empty:
        return insights
    
    expense_df = df[df["Type"] == "Expense"]
    
    if expense_df.empty:
        return insights
    
    total_expense = expense_df["Amount"].sum()
    
    # Category analysis
    category_sum = expense_df.groupby("Category")["Amount"].sum()
    top_category = category_sum.idxmax()
    top_percent = (category_sum.max() / total_expense) * 100
    
    if top_percent > 50:
        insights.append({
            "type": "warning",
            "message": f"⚠️ {top_percent:.1f}% of spending is in {top_category}. Consider diversifying."
        })
    
    # Average daily spending
    avg_daily = get_average_daily_spending(df)
    insights.append({
        "type": "info",
        "message": f"📊 Average daily spending: {format_currency(avg_daily)}"
    })
    
    # Month comparison
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
                "message": f"📈 Spending increased {change_percent:.1f}% vs last month"
            })
        elif change_percent < -10:
            insights.append({
                "type": "success",
                "message": f"📉 Great! Spending decreased {abs(change_percent):.1f}% vs last month"
            })
    
    return insights


# ==================== BUDGET FUNCTIONS ====================

def get_budget(category_id: int, month: int, year: int, user_id: Optional[int] = None, 
               db_config: int = 1) -> float:
    """Get budget for a category in a specific month."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return 0.0
    
    try:
        query = text("""
            SELECT amount FROM ht_budgets 
            WHERE category_id = :category_id AND month = :month AND year = :year
        """)
        with db.engine.connect() as conn:
            result = conn.execute(query, {
                "category_id": category_id,
                "month": month,
                "year": year
            })
            row = result.fetchone()
            return float(row[0]) if row else 0.0
    except Exception as e:
        logger.error(f"Failed to get budget: {e}")
        return 0.0


def set_budget(category_id: int, month: int, year: int, amount: float, 
               user_id: Optional[int] = None, db_config: int = 1) -> Tuple[bool, str]:
    """Set budget for a category in a specific month."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        # Upsert budget
        query = text("""
            INSERT INTO ht_budgets (user_id, category_id, month, year, amount)
            VALUES (:user_id, :category_id, :month, :year, :amount)
            ON DUPLICATE KEY UPDATE amount = :amount, updated_at = NOW()
        """)
        
        with db.engine.connect() as conn:
            conn.execute(query, {
                "user_id": user_id,
                "category_id": category_id,
                "month": month,
                "year": year,
                "amount": amount
            })
            conn.commit()
        
        return True, "Budget saved successfully"
        
    except Exception as e:
        logger.error(f"Failed to set budget: {e}")
        return False, f"Error: {str(e)}"


# ==================== KITCHEN INVENTORY FUNCTIONS ====================

def load_inventory(user_id: Optional[int] = None, db_config: int = 1) -> pd.DataFrame:
    """Load kitchen inventory."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return pd.DataFrame()
    
    try:
        query = text("""
            SELECT id, item_name, category, quantity, unit, min_quantity, 
                   expiry_date, location, notes, is_active
            FROM ht_kitchen_inventory
            WHERE is_active = TRUE
            ORDER BY category, item_name
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
        
        if not rows:
            return pd.DataFrame()
        
        df = pd.DataFrame(rows, columns=["id", "item_name", "category", "quantity", "unit", 
                                          "min_quantity", "expiry_date", "location", "notes", "is_active"])
        return df
        
    except Exception as e:
        logger.error(f"Failed to load inventory: {e}")
        return pd.DataFrame()


def add_inventory_item(item_name: str, category: str, quantity: float, unit: str,
                       min_quantity: float = 0, expiry_date=None, location: str = "",
                       notes: str = "", user_id: Optional[int] = None, 
                       db_config: int = 1) -> Tuple[bool, str]:
    """Add item to kitchen inventory."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        query = text("""
            INSERT INTO ht_kitchen_inventory 
            (user_id, item_name, category, quantity, unit, min_quantity, expiry_date, location, notes)
            VALUES (:user_id, :item_name, :category, :quantity, :unit, :min_quantity, :expiry_date, :location, :notes)
        """)
        
        with db.engine.connect() as conn:
            conn.execute(query, {
                "user_id": user_id,
                "item_name": item_name,
                "category": category,
                "quantity": quantity,
                "unit": unit,
                "min_quantity": min_quantity,
                "expiry_date": expiry_date,
                "location": location,
                "notes": notes
            })
            conn.commit()
        
        return True, "Item added to inventory"
        
    except Exception as e:
        logger.error(f"Failed to add inventory item: {e}")
        return False, f"Error: {str(e)}"


def update_inventory_quantity(item_id: int, quantity: float, db_config: int = 1) -> Tuple[bool, str]:
    """Update inventory item quantity."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        query = text("UPDATE ht_kitchen_inventory SET quantity = :quantity WHERE id = :id")
        with db.engine.connect() as conn:
            conn.execute(query, {"quantity": quantity, "id": item_id})
            conn.commit()
        
        return True, "Quantity updated"
        
    except Exception as e:
        logger.error(f"Failed to update inventory: {e}")
        return False, f"Error: {str(e)}"


def get_low_stock_items(db_config: int = 1) -> pd.DataFrame:
    """Get items that are low in stock."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return pd.DataFrame()
    
    try:
        query = text("""
            SELECT item_name, category, quantity, unit, min_quantity
            FROM ht_kitchen_inventory
            WHERE is_active = TRUE AND quantity <= min_quantity
            ORDER BY (quantity / NULLIF(min_quantity, 0)) ASC
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
        
        if not rows:
            return pd.DataFrame()
        
        return pd.DataFrame(rows, columns=["item_name", "category", "quantity", "unit", "min_quantity"])
        
    except Exception as e:
        logger.error(f"Failed to get low stock items: {e}")
        return pd.DataFrame()


def get_expiring_items(days: int = 7, db_config: int = 1) -> pd.DataFrame:
    """Get items expiring within specified days."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return pd.DataFrame()
    
    try:
        query = text("""
            SELECT item_name, category, quantity, unit, expiry_date
            FROM ht_kitchen_inventory
            WHERE is_active = TRUE 
            AND expiry_date IS NOT NULL 
            AND expiry_date <= DATE_ADD(CURDATE(), INTERVAL :days DAY)
            ORDER BY expiry_date ASC
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query, {"days": days})
            rows = result.fetchall()
        
        if not rows:
            return pd.DataFrame()
        
        return pd.DataFrame(rows, columns=["item_name", "category", "quantity", "unit", "expiry_date"])
        
    except Exception as e:
        logger.error(f"Failed to get expiring items: {e}")
        return pd.DataFrame()


# ==================== SHOPPING LIST FUNCTIONS ====================

def load_shopping_list(user_id: Optional[int] = None, include_purchased: bool = False,
                       db_config: int = 1) -> pd.DataFrame:
    """Load shopping list."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return pd.DataFrame()
    
    try:
        if include_purchased:
            query = text("""
                SELECT id, item_name, category, quantity, unit, estimated_price, 
                       priority, is_purchased, purchased_at, notes
                FROM ht_shopping_list
                ORDER BY is_purchased, priority DESC, item_name
            """)
        else:
            query = text("""
                SELECT id, item_name, category, quantity, unit, estimated_price, 
                       priority, is_purchased, notes
                FROM ht_shopping_list
                WHERE is_purchased = FALSE
                ORDER BY priority DESC, item_name
            """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
        
        if not rows:
            return pd.DataFrame()
        
        cols = ["id", "item_name", "category", "quantity", "unit", "estimated_price", 
                "priority", "is_purchased", "purchased_at", "notes"] if include_purchased else \
               ["id", "item_name", "category", "quantity", "unit", "estimated_price", 
                "priority", "is_purchased", "notes"]
        
        return pd.DataFrame(rows, columns=cols)
        
    except Exception as e:
        logger.error(f"Failed to load shopping list: {e}")
        return pd.DataFrame()


def add_shopping_item(item_name: str, category: str = "", quantity: float = 1,
                      unit: str = "pieces", estimated_price: float = 0,
                      priority: str = "medium", notes: str = "",
                      user_id: Optional[int] = None, db_config: int = 1) -> Tuple[bool, str]:
    """Add item to shopping list."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        query = text("""
            INSERT INTO ht_shopping_list 
            (user_id, item_name, category, quantity, unit, estimated_price, priority, notes)
            VALUES (:user_id, :item_name, :category, :quantity, :unit, :estimated_price, :priority, :notes)
        """)
        
        with db.engine.connect() as conn:
            conn.execute(query, {
                "user_id": user_id,
                "item_name": item_name,
                "category": category,
                "quantity": quantity,
                "unit": unit,
                "estimated_price": estimated_price,
                "priority": priority,
                "notes": notes
            })
            conn.commit()
        
        return True, "Item added to shopping list"
        
    except Exception as e:
        logger.error(f"Failed to add shopping item: {e}")
        return False, f"Error: {str(e)}"


def mark_item_purchased(item_id: int, db_config: int = 1) -> Tuple[bool, str]:
    """Mark shopping list item as purchased."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        query = text("""
            UPDATE ht_shopping_list 
            SET is_purchased = TRUE, purchased_at = NOW()
            WHERE id = :id
        """)
        with db.engine.connect() as conn:
            conn.execute(query, {"id": item_id})
            conn.commit()
        
        return True, "Item marked as purchased"
        
    except Exception as e:
        logger.error(f"Failed to mark item purchased: {e}")
        return False, f"Error: {str(e)}"


# ==================== GOALS FUNCTIONS ====================

def load_goals(user_id: Optional[int] = None, db_config: int = 1) -> pd.DataFrame:
    """Load financial goals."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return pd.DataFrame()
    
    try:
        query = text("""
            SELECT id, goal_name, target_amount, current_amount, deadline, 
                   status, priority, notes
            FROM ht_goals
            WHERE status = 'active'
            ORDER BY deadline ASC
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
        
        if not rows:
            return pd.DataFrame()
        
        return pd.DataFrame(rows, columns=["id", "goal_name", "target_amount", "current_amount", 
                                            "deadline", "status", "priority", "notes"])
        
    except Exception as e:
        logger.error(f"Failed to load goals: {e}")
        return pd.DataFrame()


def add_goal(goal_name: str, target_amount: float, deadline=None, priority: str = "medium",
             notes: str = "", user_id: Optional[int] = None, db_config: int = 1) -> Tuple[bool, str]:
    """Add a new financial goal."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        query = text("""
            INSERT INTO ht_goals (user_id, goal_name, target_amount, deadline, priority, notes)
            VALUES (:user_id, :goal_name, :target_amount, :deadline, :priority, :notes)
        """)
        
        with db.engine.connect() as conn:
            conn.execute(query, {
                "user_id": user_id,
                "goal_name": goal_name,
                "target_amount": target_amount,
                "deadline": deadline,
                "priority": priority,
                "notes": notes
            })
            conn.commit()
        
        return True, "Goal added successfully"
        
    except Exception as e:
        logger.error(f"Failed to add goal: {e}")
        return False, f"Error: {str(e)}"


def update_goal_progress(goal_id: int, amount: float, db_config: int = 1) -> Tuple[bool, str]:
    """Update goal progress."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        query = text("UPDATE ht_goals SET current_amount = :amount WHERE id = :id")
        with db.engine.connect() as conn:
            conn.execute(query, {"amount": amount, "id": goal_id})
            conn.commit()
        
        return True, "Goal progress updated"
        
    except Exception as e:
        logger.error(f"Failed to update goal: {e}")
        return False, f"Error: {str(e)}"


# ==================== UI HELPER FUNCTIONS ====================

def show_success_message(message: str):
    """Show success message."""
    st.success(f"✅ {message}")


def show_error_message(message: str):
    """Show error message."""
    st.error(f"❌ {message}")


def show_warning_message(message: str):
    """Show warning message."""
    st.warning(f"⚠️ {message}")


def show_info_message(message: str):
    """Show info message."""
    st.info(f"ℹ️ {message}")


def create_metric_card(title: str, value: float, delta: float = None, delta_color: str = "normal"):
    """Create a styled metric card."""
    st.metric(
        label=title,
        value=format_currency(value),
        delta=format_currency(delta) if delta else None,
        delta_color=delta_color
    )


# ==================== GOALS FUNCTIONS (EXTENDED) ====================

def get_goals_list(user_id=None, db_config: int = 1) -> list:
    """Load financial goals as list of dictionaries."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return []
    
    try:
        query = text("""
            SELECT id, goal_name, target_amount, current_amount, deadline, 
                   category, description, priority, status, created_at
            FROM ht_goals
            ORDER BY deadline ASC
        """)
        
        with db.engine.connect() as conn:
            result = conn.execute(query)
            rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "target_amount": float(row[2]) if row[2] else 0,
                "current_amount": float(row[3]) if row[3] else 0,
                "deadline": row[4],
                "category": row[5],
                "description": row[6],
                "priority": row[7],
                "status": row[8] or "In Progress",
                "created_at": row[9]
            }
            for row in rows
        ]
        
    except Exception as e:
        logger.error(f"Failed to get goals list: {e}")
        return []


def save_goal(goal_data: dict, user_id=None, db_config: int = 1) -> Tuple[bool, str]:
    """Save (create or update) a financial goal."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        if goal_data.get('id'):
            # Update existing goal
            query = text("""
                UPDATE ht_goals SET 
                    goal_name = :name,
                    target_amount = :target_amount,
                    current_amount = :current_amount,
                    deadline = :deadline,
                    category = :category,
                    description = :description,
                    priority = :priority,
                    status = :status,
                    updated_at = NOW()
                WHERE id = :id
            """)
            params = {
                "id": goal_data.get('id'),
                "name": goal_data.get('name'),
                "target_amount": goal_data.get('target_amount', 0),
                "current_amount": goal_data.get('current_amount', 0),
                "deadline": goal_data.get('deadline'),
                "category": goal_data.get('category', 'General'),
                "description": goal_data.get('description', ''),
                "priority": goal_data.get('priority', 'Medium'),
                "status": goal_data.get('status', 'In Progress')
            }
        else:
            # Create new goal
            query = text("""
                INSERT INTO ht_goals 
                (user_id, goal_name, target_amount, current_amount, deadline, 
                 category, description, priority, status)
                VALUES (:user_id, :name, :target_amount, :current_amount, :deadline,
                        :category, :description, :priority, :status)
            """)
            params = {
                "user_id": user_id,
                "name": goal_data.get('name'),
                "target_amount": goal_data.get('target_amount', 0),
                "current_amount": goal_data.get('current_amount', 0),
                "deadline": goal_data.get('deadline'),
                "category": goal_data.get('category', 'General'),
                "description": goal_data.get('description', ''),
                "priority": goal_data.get('priority', 'Medium'),
                "status": goal_data.get('status', 'In Progress')
            }
        
        with db.engine.connect() as conn:
            conn.execute(query, params)
            conn.commit()
        
        return True, "Goal saved successfully"
        
    except Exception as e:
        logger.error(f"Failed to save goal: {e}")
        return False, f"Error: {str(e)}"


def delete_goal(goal_id: int, user_id=None, db_config: int = 1) -> Tuple[bool, str]:
    """Delete a financial goal."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        query = text("DELETE FROM ht_goals WHERE id = :id")
        with db.engine.connect() as conn:
            conn.execute(query, {"id": goal_id})
            conn.commit()
        
        return True, "Goal deleted successfully"
        
    except Exception as e:
        logger.error(f"Failed to delete goal: {e}")
        return False, f"Error: {str(e)}"


# ==================== SYSTEM STATS FUNCTIONS ====================

def get_system_stats(db_config: int = 1) -> Dict[str, Any]:
    """Get system-wide statistics."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return {
            "total_users": 0,
            "total_transactions": 0,
            "total_volume": 0,
            "total_categories": 0
        }
    
    try:
        stats = {}
        
        # User count
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM ht_users"))
            stats["total_users"] = result.fetchone()[0]
        
        # Transaction count and volume
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM ht_transactions"))
            row = result.fetchone()
            stats["total_transactions"] = row[0]
            stats["total_volume"] = float(row[1])
        
        # Category count
        with db.engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM ht_categories WHERE is_active = TRUE"))
            stats["total_categories"] = result.fetchone()[0]
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get system stats: {e}")
        return {
            "total_users": 0,
            "total_transactions": 0,
            "total_volume": 0,
            "total_categories": 0
        }


def get_date_range_data(df: pd.DataFrame, start_date, end_date) -> pd.DataFrame:
    """Filter dataframe by date range."""
    if df.empty:
        return df
    
    return df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]


# ==================== ADMIN DANGEROUS ACTIONS ====================

def clear_all_transactions(db_config: int = 1) -> Tuple[bool, str]:
    """Clear all transactions - DANGEROUS ADMIN ACTION."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        with db.engine.connect() as conn:
            conn.execute(text("DELETE FROM ht_transactions"))
            conn.commit()
        
        logger.warning("All transactions cleared by admin!")
        return True, "All transactions cleared"
        
    except Exception as e:
        logger.error(f"Failed to clear transactions: {e}")
        return False, f"Error: {str(e)}"


def clear_activity_logs(db_config: int = 1) -> Tuple[bool, str]:
    """Clear all activity logs - DANGEROUS ADMIN ACTION."""
    db = get_db_manager(db_config)
    
    if not db.engine:
        return False, "Database connection not available"
    
    try:
        with db.engine.connect() as conn:
            conn.execute(text("DELETE FROM ht_activity_logs"))
            conn.commit()
        
        logger.warning("All activity logs cleared by admin!")
        return True, "All activity logs cleared"
        
    except Exception as e:
        logger.error(f"Failed to clear activity logs: {e}")
        return False, f"Error: {str(e)}"
