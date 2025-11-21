import streamlit as st
from config import DEVELOPER_NAME, DEVELOPER_EMAIL, DEVELOPER_GITHUB, APP_TITLE, CURRENCY_SYMBOL

st.title("ℹ️ About Madam Becky House Management Tracker")

st.markdown("""
### 🏠 Your Complete Household Management Solution

Welcome to **Madam Becky House Management Tracker** — a simple yet powerful app designed to help manage household expenses, 
especially kitchen needs. Whether tracking daily groceries, managing budgets for household supplies, or monitoring spending, 
this app provides all the tools needed for efficient home management.

**Built for Kenya** 🇰🇪 with KSH currency support and features tailored for household management.
""")

st.markdown("---")

# Main Features Section
st.subheader("🌟 What Makes This App Special")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 📊 Core Features
    
    **📝 Smart Expense Tracking**
    - Add budgets and expenses for household needs
    - Track kitchen supplies, groceries, and utilities
    - Bulk import via CSV for quick data entry
    - Edit and delete transactions easily
    - Filter by date, category, or custom ranges
    
    **💰 Household Budget Management**
    - Set monthly budgets per category
    - Real-time progress tracking with visual indicators
    - Track spending on groceries, cooking gas, vegetables, etc.
    - Budget vs. actual spending comparisons
    
    **🎯 Household Goal Setting**
    - Create household saving goals with deadlines
    - Track progress with interactive progress bars
    - Update savings towards goals anytime
    - Visual motivation to stay on track
    """)

with col2:
    st.markdown("""
    #### ⭐ Advanced Features
    
    **🏷️ Dynamic Category Management**
    - Create custom categories that fit your lifestyle
    - Rename categories (updates all transactions)
    - Delete unused categories safely
    - Import/export categories for backup
    - View category usage analytics
    
    **📈 Advanced Analytics & Statistics**
    - Daily expense trends and patterns
    - Weekday spending analysis
    - Cumulative spending tracking
    - Category-wise deep dive (min, max, average)
    - AI-powered spending insights
    - Month-over-month comparisons
    - Savings rate calculations
    
    **📊 Rich Visualizations**
    - Interactive pie, bar, and line charts
    - Monthly and yearly summaries
    - Category distribution analysis
    - Cash flow visualization
    """)

st.markdown("---")

# Why Choose This App
st.subheader("✨ Why You'll Love This App")

feat_col1, feat_col2, feat_col3, feat_col4 = st.columns(4)

with feat_col1:
    st.markdown("""
    **🔒 Privacy First**
    
    - All data stored locally
    - No cloud, no accounts
    - You own your data
    - Export anytime
    """)

with feat_col2:
    st.markdown("""
    **🚀 Easy to Use**
    
    - Clean, intuitive interface
    - No learning curve
    - Quick data entry
    - Mobile-friendly
    """)

with feat_col3:
    st.markdown("""
    **💪 Powerful Features**
    
    - Advanced analytics
    - Smart insights
    - Flexible categories
    - Bulk operations
    """)

with feat_col4:
    st.markdown("""
    **⚡ Fast & Reliable**
    
    - Instant responses
    - Works offline
    - Automatic backups
    - CSV-based storage
    """)

st.markdown("---")

# How It Works
st.subheader("🔧 How It Works")

st.markdown("""
#### Simple 3-Step Process:

1. **📝 Track Your Money**
   - Add income and expenses as they happen
   - Use custom categories that make sense to you
   - Bulk import transactions from CSV if needed

2. **📊 Understand Your Spending**
   - View beautiful charts and reports
   - Get smart insights about your habits
   - Identify areas to save money

3. **🎯 Achieve Your Goals**
   - Set budgets to control spending
   - Create financial goals and track progress
   - Make informed decisions with data
""")

st.markdown("---")

# Data & Privacy
st.subheader("🔐 Your Data, Your Privacy")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Where Your Data Lives
    
    All your financial data is stored in **CSV files** in the `data/` folder on your computer:
    
    - `add_expense.csv` - Your transactions
    - `financial_goals.csv` - Your goals
    - `budgets.csv` - Your budget settings
    - `categories.csv` - Your custom categories
    
    **You can edit these files directly** with Excel or any spreadsheet software!
    """)

with col2:
    st.markdown("""
    #### Backup & Security
    
    - ✅ Automatic backups created in `backups/` folder
    - ✅ No internet connection required
    - ✅ No user accounts or passwords
    - ✅ No data sent to any server
    - ✅ Easy to backup (just copy the files)
    - ✅ Easy to restore (replace the files)
    - ✅ Complete control over your data
    """)

st.markdown("---")

# Currency Info
st.subheader(f"💵 Currency: {CURRENCY_SYMBOL}")

st.markdown(f"""
This app is configured for **Kenyan Shilling (KSH)** with appropriate:

- **Amount Ranges**: KSH 0.01 to KSH 10,000,000
- **Budget Templates**: Realistic amounts for household expenses
- **Display Formats**: Clear KSH formatting throughout

Perfect for household management and kitchen expense tracking in Kenya! 🇰🇪
""")

st.markdown("---")

# Technology Stack
st.subheader("⚙️ Built With")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### Core Technologies
    - 🐍 **Python** - Programming language
    - 🎨 **Streamlit** - Web interface
    - 📊 **Pandas** - Data processing
    - 📈 **Plotly** - Interactive charts
    """)

with col2:
    st.markdown("""
    #### Key Features
    - CSV-based storage (no database)
    - Responsive design
    - Real-time updates
    - Caching for performance
    """)

st.markdown("---")

# Support & Contribute
st.subheader("💡 Get Help & Contribute")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📚 Learn More**
    - Check the **Guidelines** page
    - Read `README.md` file
    - See `QUICKSTART.md`
    - View `ENHANCEMENTS.md`
    """)

with col2:
    st.markdown("""
    **🆘 Need Help?**
    - Review the Guidelines page
    - Check troubleshooting tips
    - Explore example data
    - Ask the community
    """)

with col3:
    st.markdown("""
    **🤝 Contribute**
    - Report bugs
    - Suggest features
    - Share feedback
    - Improve docs
    """)

st.markdown("---")

# Version Info
st.subheader("📦 Version Information")

st.markdown("""
**Version 3.0 - Enhanced Edition**

This version includes:
- ✅ Dynamic category management
- ✅ Advanced statistics and insights
- ✅ KSH currency support
- ✅ Smart spending recommendations
- ✅ Weekday and cumulative analysis
- ✅ Enhanced import/export features

See `ENHANCEMENTS.md` for complete changelog.
""")

st.markdown("---")

# Footer
st.success("💚 Thank you for using Madam Becky House Management Tracker! Manage your household efficiently!")

st.markdown("""
<div style='text-align: center; padding: 20px; color: gray;'>
    <p>Your home, your control. Track smart, spend wise, manage better! 🏠</p>
    <p>© 2025 Madam Becky House Management Tracker | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
