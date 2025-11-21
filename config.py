import os
import pandas as pd
from datetime import datetime

# File paths
DATA_DIR = "data"
EXPENSE_FILE = os.path.join(DATA_DIR, "add_expense.csv")
GOALS_FILE = os.path.join(DATA_DIR, "financial_goals.csv")
BACKUP_DIR = "backups"
BUDGETS_FILE = os.path.join(DATA_DIR, "budgets.csv")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.csv")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Categories - now stored in CSV - Focused on Home & Kitchen Management
DEFAULT_CATEGORIES = ["Groceries", "Vegetables", "Meat & Poultry", "Fish & Seafood", "Fruits", "Cooking Gas", "Kitchen Supplies", "Cleaning Supplies", "Utilities (Water/Electricity)", "House Maintenance", "Others"]

# Currency
CURRENCY = "KSH"
CURRENCY_SYMBOL = "KSH"

# Date formats
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Validation limits
MAX_AMOUNT = 10000000  # Maximum transaction amount (10 million KSH)
MAX_DESCRIPTION_LENGTH = 200
MIN_AMOUNT = 0.01
MAX_CATEGORY_LENGTH = 50

# App settings
APP_TITLE = "Madam Becky House Management Tracker"
APP_ICON = "🏠"
PAGE_LAYOUT = "wide"

# Developer info
DEVELOPER_NAME = "Joseph Nderitu"
DEVELOPER_EMAIL = "josephnderito16@gmail.com"
DEVELOPER_GITHUB = "github.com/josephndex"

# Initialize CSV files if they don't exist
def _initialize_csv_files():
    """Automatically create CSV files if they don't exist"""
    
    # Initialize categories file
    if not os.path.exists(CATEGORIES_FILE):
        categories_df = pd.DataFrame({"Category": DEFAULT_CATEGORIES})
        categories_df.to_csv(CATEGORIES_FILE, index=False)
    
    # Initialize expense file
    if not os.path.exists(EXPENSE_FILE):
        expense_df = pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Description"])
        expense_df.to_csv(EXPENSE_FILE, index=False)
    
    # Initialize goals file
    if not os.path.exists(GOALS_FILE):
        goals_df = pd.DataFrame(columns=["Goal", "Target Amount", "Amount Saved", "Deadline"])
        goals_df.to_csv(GOALS_FILE, index=False)
    
    # Initialize budgets file
    if not os.path.exists(BUDGETS_FILE):
        budgets_df = pd.DataFrame(columns=["Category", "Budget"])
        budgets_df.to_csv(BUDGETS_FILE, index=False)

# Auto-initialize on import
_initialize_csv_files()