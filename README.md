# 💸 Personal Finance Tracker - Enhanced Edition

A comprehensive personal finance management application built with Streamlit that helps you track expenses, income, set budgets, and achieve financial goals. Enhanced with advanced analytics, dynamic category management, and KSH currency support.

## ✨ Features

### 📊 Core Features
- **Expense & Income Tracking**: Add, edit, and delete financial transactions
- **Budget Management**: Set monthly budgets and track spending against them
- **Financial Goals**: Set and track progress towards financial goals
- **Data Visualization**: Interactive charts and reports with Plotly
- **Data Export/Import**: Backup and restore your financial data
- **CSV-Based Storage**: All data stored in CSV files (no database required)

### 🎯 Advanced Features
- **Dynamic Category Management**: Create, edit, and delete categories from the app or CSV
- **Advanced Statistics**: Deep insights with cumulative spending, weekday patterns, and more
- **Smart Insights**: AI-powered spending recommendations and alerts
- **Daily/Monthly/Yearly Analytics**: Multiple time-based views of your finances
- **Category Analytics**: Detailed statistics per category with min/max/average
- **Smart Validation**: Input validation to prevent data errors
- **Data Cleanup**: Tools to maintain data quality
- **Caching**: Improved performance with data caching
- **Backup System**: Automatic backup creation and management
- **Responsive Design**: Works on desktop and mobile devices
- **KSH Currency**: Configured for Kenyan Shilling with appropriate amount ranges

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd expense_tracker_copy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run main.py
   ```

4. **Open your browser**
   Navigate to `http://localhost:8501`

## 📁 Project Structure

```
Personal-Expense-Tracker/
├── main.py                  # Main application entry point with navigation
├── config.py                # Configuration and constants (KSH currency)
├── utils.py                 # Shared utility functions with advanced analytics
├── home.py                  # Home dashboard with quick stats
├── add_expense.py           # Add/edit/import transactions
├── budget.py                # Budget management with templates
├── report.py                # Reports and visualizations
├── statistics.py            # ⭐ NEW: Advanced statistics & insights
├── categories.py            # ⭐ NEW: Dynamic category management (CRUD)
├── monthly.py               # Monthly overview
├── goal.py                  # Financial goals tracking
├── about.py                 # About page
├── guidelines.py            # User guidelines
├── data/                    # Data storage (CSV files)
│   ├── add_expense.csv      # Transaction data
│   ├── financial_goals.csv  # Goals data
│   ├── budgets.csv          # Budget configuration
│   └── categories.csv       # ⭐ NEW: Custom categories
├── backups/                 # Automatic backup files
├── images/                  # Application images
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🆕 What's New in This Enhanced Version

### 🌟 Major Enhancements

1. **Dynamic Category Management** 
   - Create, edit, and delete categories directly from the app
   - Category usage analytics shows which categories you use most
   - Import/export categories via CSV
   - Prevents deletion of categories with existing transactions
   - Rename categories and automatically update all transactions

2. **Advanced Statistics Page**
   - Daily expense trends with interactive charts
   - Weekday spending patterns analysis
   - Cumulative spending growth tracking
   - Category-wise deep dive with min/max/average
   - Smart insights and recommendations
   - Month-over-month comparison
   - Savings rate calculation and recommendations

3. **KSH Currency Support**
   - Configured for Kenyan Shilling
   - Appropriate amount ranges (0.01 to 10,000,000 KSH)
   - Budget templates adjusted for Kenya context

4. **Enhanced Analytics Functions**
   - `get_spending_insights()` - AI-powered recommendations
   - `get_weekday_spending()` - Day-of-week patterns
   - `get_cumulative_spending()` - Track spending growth
   - `get_category_statistics()` - Detailed category metrics
   - `get_most_expensive_day()` - Identify peak spending days

5. **Improved Category System**
   - Categories stored in `categories.csv` for easy editing
   - Default categories: Salary, Food, Transport, Shopping, Bills, Utilities, Entertainment, Healthcare, Education, Others
   - Add custom categories that fit your lifestyle
   - Bulk import/export functionality

## 🎮 How to Use

### 1. Getting Started
- **Home Page**: View your financial summary and recent transactions
- **Add Expense**: Record new income or expense entries with dynamic categories
- **Budget**: Set and track monthly budgets by category

### 2. Adding Transactions
1. Go to "Add Expense" page
2. Select transaction type (Income/Expense)
3. Choose from your custom categories
4. Enter amount (in KSH) and date
5. Add optional description
6. Click "Save Entry"

### 3. Managing Categories
1. Go to "Categories" page
2. View all existing categories and their usage
3. Add new categories for your specific needs
4. Rename existing categories (updates all transactions)
5. Delete unused categories
6. Import/export categories via CSV

### 4. Budget Management
1. Go to "Budget" page
2. Set monthly budgets for each category (in KSH)
3. Use quick templates (Conservative/Moderate) or set custom amounts
4. Monitor spending against budgets with visual progress bars

### 5. Advanced Statistics
1. Go to "Statistics" page
2. View daily expense trends and patterns
3. Analyze spending by day of week
4. See cumulative spending growth
5. Get personalized savings recommendations
6. Identify top categories to optimize

### 6. Data Management
- **Export Data**: Download your data as CSV
- **Import Data**: Bulk upload transactions via CSV
- **Backup**: Automatic backups are created regularly
- **Category Management**: Export/import categories for backup

## 🔧 Configuration

### Customizing Categories
Edit `config.py` to modify default categories:
```python
DEFAULT_CATEGORIES = ["Salary", "Food", "Transport", "Shopping", "Bills", "Others"]
```

### Currency Settings
Change currency in `config.py`:
```python
CURRENCY = "₹"  # Change to your preferred currency
```

## 🛠️ Data Validation

The application includes comprehensive data validation:
- **Amount Validation**: Must be between 0.01 and 1,000,000
- **Category Validation**: Required field with 50 character limit
- **Description Validation**: Optional field with 200 character limit
- **Date Validation**: Ensures valid date format

## 📊 Data Storage

- **Format**: CSV files stored in `data/` directory
- **Backup**: Automatic backups in `backups/` directory
- **Security**: Data stays on your local machine

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'streamlit'"**
   ```bash
   pip install streamlit
   ```

2. **Data not loading**
   - Check if `data/` directory exists
   - Verify CSV file permissions

3. **Performance issues**
   - Use data cleanup tools to remove invalid entries
   - Clear browser cache

### Data Recovery
- Check `backups/` directory for recent backups
- Use data cleanup tools to fix common issues

## 🔒 Privacy & Security

- **Local Storage**: All data is stored locally on your machine
- **No Cloud**: No data is sent to external servers
- **Backup**: Regular automatic backups protect your data

## 🎨 Customization

### Styling
Modify the application appearance by editing CSS in individual pages or creating a custom theme.

### Adding Features
The modular structure makes it easy to add new features:
1. Create new Python files for new pages
2. Add navigation entries in `main.py`
3. Use utility functions from `utils.py`

## 📈 Performance Tips

1. **Regular Cleanup**: Use data cleanup tools monthly
2. **Limit Data**: Archive old data if performance slows
3. **Browser Cache**: Clear cache if experiencing issues

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 Changelog

### Version 3.0 (Enhanced Edition - Current)
- ✅ **NEW**: Dynamic category management (CRUD operations)
- ✅ **NEW**: Advanced statistics page with deep insights
- ✅ **NEW**: KSH currency support with appropriate ranges
- ✅ **NEW**: Smart spending insights and recommendations
- ✅ **NEW**: Weekday spending pattern analysis
- ✅ **NEW**: Cumulative spending tracking
- ✅ **NEW**: Category usage analytics
- ✅ **NEW**: Bulk category import/export
- ✅ **ENHANCED**: Budget templates adjusted for Kenya
- ✅ **ENHANCED**: More detailed category statistics
- ✅ **ENHANCED**: Improved navigation and UI organization

### Version 2.0
- ✅ Added budget management system
- ✅ Improved data validation
- ✅ Added data cleanup tools
- ✅ Enhanced UI/UX
- ✅ Added caching for better performance
- ✅ Implemented backup system

### Version 1.0 (Original)
- ✅ Basic expense tracking
- ✅ Simple reports
- ✅ Goal setting

## 📞 Support

- **Documentation**: Check the Guidelines page in the app
- **Issues**: Report bugs through GitHub issues
- **Issues**: Report bugs through GitHub issues

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io)
- Data visualization with [Plotly](https://plotly.com)
- Data processing with [Pandas](https://pandas.pydata.org)

---

**Happy Financial Tracking! 💰**
"# Personal-Finance-Tracker" 
