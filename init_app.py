"""
Initialization script for Personal Finance Tracker
Run this once to set up initial data files
"""

import os
import pandas as pd
from config import *

def initialize_app():
    """Initialize the application with default data files"""
    
    print("🚀 Initializing Personal Finance Tracker...")
    
    # Ensure directories exist
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    print(f"✅ Created directories: {DATA_DIR}, {BACKUP_DIR}")
    
    # Initialize categories file if not exists
    if not os.path.exists(CATEGORIES_FILE):
        categories_df = pd.DataFrame({"Category": DEFAULT_CATEGORIES})
        categories_df.to_csv(CATEGORIES_FILE, index=False)
        print(f"✅ Created categories file with {len(DEFAULT_CATEGORIES)} default categories")
    else:
        print("ℹ️  Categories file already exists")
    
    # Initialize expense file if not exists
    if not os.path.exists(EXPENSE_FILE):
        expense_df = pd.DataFrame(columns=["Date", "Type", "Amount", "Category", "Description"])
        expense_df.to_csv(EXPENSE_FILE, index=False)
        print("✅ Created empty expense file")
    else:
        print("ℹ️  Expense file already exists")
    
    # Initialize goals file if not exists
    if not os.path.exists(GOALS_FILE):
        goals_df = pd.DataFrame(columns=["Goal", "Target Amount", "Amount Saved", "Deadline"])
        goals_df.to_csv(GOALS_FILE, index=False)
        print("✅ Created empty goals file")
    else:
        print("ℹ️  Goals file already exists")
    
    # Initialize budgets file if not exists
    if not os.path.exists(BUDGETS_FILE):
        budgets_df = pd.DataFrame(columns=["Category", "Budget"])
        budgets_df.to_csv(BUDGETS_FILE, index=False)
        print("✅ Created empty budgets file")
    else:
        print("ℹ️  Budgets file already exists")
    
    print("\n🎉 Initialization complete!")
    print("\n📝 Next steps:")
    print("   1. Run: streamlit run main.py")
    print("   2. Add your first transaction")
    print("   3. Set up your budget")
    print("   4. Explore the features!")
    print(f"\n💡 Currency is set to: {CURRENCY_SYMBOL}")

if __name__ == "__main__":
    initialize_app()
