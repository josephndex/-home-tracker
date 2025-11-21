# 🚀 Quick Start Guide - Personal Finance Tracker

## Welcome! 👋

This guide will help you get started with your Personal Finance Tracker in under 5 minutes.

## Step 1: Installation ⚙️

```bash
# Install required packages
pip install -r requirements.txt
```

## Step 2: Launch the App 🚀

```bash
# Run the application
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`

## Step 3: First Time Setup 🎯

### Add Your First Transaction

1. Click on **"➕ Add Expense"** in the sidebar
2. Fill in the details:
   - **Type**: Choose "Income" or "Expense"
   - **Category**: Select from available categories
   - **Amount**: Enter amount in KSH
   - **Date**: Pick the transaction date
   - **Description**: Add optional notes
3. Click **"💾 Save Entry"**

### Set Up Categories (Optional)

1. Go to **"🏷️ Categories"** page
2. Add custom categories that match your lifestyle:
   - Click "➕ Add New Category"
   - Enter category name (e.g., "Gym", "Groceries")
   - Save!
3. You can also rename or delete categories here

### Set Your Budget 💰

1. Navigate to **"💰 Budget"** page
2. Choose a budget template:
   - **Conservative**: Lower spending limits
   - **Moderate**: Balanced approach
3. Or set custom amounts for each category
4. Save your budgets

## Step 4: Explore Features 🎨

### Home Dashboard 🏠
- View total income, expenses, and net savings
- See recent transactions
- Check expense distribution by category

### Reports 📊
- Monthly and yearly summaries
- Visual charts (pie, line, bar)
- Filter by date range
- Export data as CSV

### Statistics 📈
- **NEW!** Advanced analytics page
- Daily expense trends
- Weekday spending patterns
- Category-wise deep dive
- Smart spending insights
- Savings recommendations

### Monthly Data 📅
- Month-by-month breakdown
- Compare different periods
- Track your progress

### Goals 🎯
- Set financial goals
- Track progress
- Stay motivated

## Quick Tips 💡

### Daily Use
1. Add transactions as they happen (or daily)
2. Check your budget status weekly
3. Review statistics monthly

### Data Management
- **Export**: Download your data regularly as backup
- **Import**: Bulk upload transactions using CSV
- **Categories**: Keep them organized and relevant

### Best Practices
- ✅ Be consistent with categories
- ✅ Add descriptions to track spending better
- ✅ Review statistics page for insights
- ✅ Adjust budgets based on actual spending
- ✅ Set realistic financial goals

## Common Tasks 📝

### How to Import Multiple Transactions
1. Go to "Add Expense" → "Import/Export" tab
2. Download sample CSV to see format
3. Fill in your transactions
4. Upload the CSV file
5. Review preview and confirm merge

### How to Manage Categories
1. Go to "Categories" page
2. **To Add**: Use "Add New Category" form
3. **To Rename**: Use "Rename Category" form (updates all transactions)
4. **To Delete**: Select category and confirm deletion (only if unused)

### How to Set Budget
1. Go to "Budget" page
2. Set monthly budget for each category
3. Use templates for quick setup
4. Monitor progress in real-time

### How to View Statistics
1. Go to "Statistics" page
2. Explore different visualizations:
   - Daily trends
   - Category breakdowns
   - Weekday patterns
   - Cumulative growth
3. Read smart insights and recommendations

## Currency Note 💵

This app is configured for **Kenyan Shilling (KSH)**. Budget templates and amount ranges are set accordingly:
- Minimum amount: KSH 0.01
- Maximum amount: KSH 10,000,000

To change currency, edit `config.py`:
```python
CURRENCY = "KSH"
CURRENCY_SYMBOL = "KSH"
```

## Need Help? 🆘

1. Check the **"📘 Guidelines"** page in the app
2. Review the **README.md** for detailed documentation
3. Check data files in `/data` folder for direct CSV editing

## What's Next? 🎯

1. ✅ Add your first week of transactions
2. ✅ Set up your monthly budget
3. ✅ Create custom categories
4. ✅ Set a financial goal
5. ✅ Review your first statistics report

---

**Happy Tracking! 💰**

Track your finances, achieve your goals, and build better money habits! 🚀
