# 🏠 HomeTracker - Smart Home Management System

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A stunning, modern home management application with a special focus on kitchen and food expense tracking. Built with Streamlit and MySQL for a beautiful, responsive experience.

![HomeTracker Dashboard](https://via.placeholder.com/800x400/1a0d2e/f97316?text=HomeTracker+Dashboard)

## ✨ Features

### 📊 Dashboard
- Real-time financial overview
- Interactive charts and visualizations
- Quick insights and spending summaries

### 🍳 Kitchen Central
- Dedicated kitchen expense tracking
- Smart shopping list management
- Kitchen spending analytics
- Category-specific tracking (Groceries, Vegetables, Meat, Seafood, etc.)

### 💰 Budget Management
- Set monthly budgets by category
- Visual progress indicators
- Budget templates (Conservative, Moderate, Comfortable)
- Threshold alerts

### 📈 Reports & Analytics
- Comprehensive financial reports
- Spending trends and patterns
- Category analysis
- Export to CSV

### 🎯 Financial Goals
- Set and track savings goals
- Progress visualization
- Deadline tracking
- Priority management

### 📂 Category Management
- Custom categories
- Kitchen-specific categories with emojis
- Usage statistics

### 🔐 Security
- Secure authentication with bcrypt
- Role-based access control
- Admin panel (Super Admin: NDERITU)
- Activity logging

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MySQL Server
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/hometracker.git
   cd hometracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Create the database**
   ```sql
   CREATE DATABASE hometracker;
   ```

6. **Run the application**
   ```bash
   streamlit run main.py
   ```

7. **Access the app**
   - Open your browser to `http://localhost:8501`
   - Register with username `NDERITU` to become Super Admin

## 🗄️ Database Schema

The application uses the following tables:
- `ht_users` - User accounts and authentication
- `ht_transactions` - Income and expense records
- `ht_categories` - Expense/income categories
- `ht_budgets` - Monthly budget allocations
- `ht_goals` - Financial goals
- `ht_kitchen_inventory` - Kitchen inventory tracking
- `ht_shopping_list` - Shopping list items
- `ht_activity_logs` - User activity tracking

## 🎨 Theme

HomeTracker features a stunning orange/purple gradient theme:
- **Primary**: `#f97316` (Orange)
- **Secondary**: `#a855f7` (Purple)
- **Accent**: `#667eea` (Electric Blue)

## 📱 Pages

| Page | Description |
|------|-------------|
| Login | Authentication & Registration |
| Home | Dashboard with overview |
| Add Transaction | Record expenses/income |
| Budget | Set and track budgets |
| Reports | Financial reports |
| Kitchen | Kitchen expense management |
| Statistics | Advanced analytics |
| Goals | Financial goal tracking |
| Categories | Manage categories |
| Admin | Admin panel (hidden) |
| Settings | User preferences |
| About | Application info |

## 🍳 Kitchen Categories

Special focus on kitchen-related expenses:
- 🛒 Groceries
- 🥬 Vegetables
- 🍖 Meat & Poultry
- 🐟 Fish & Seafood
- 🍎 Fruits
- 🥛 Dairy & Eggs
- 🥤 Beverages
- 🍪 Snacks
- 🫒 Cooking Oil
- 🧂 Spices & Seasonings
- 🧁 Baking Supplies
- 🧹 Cleaning Supplies
- 🍳 Kitchen Supplies
- 🔥 Cooking Gas

## 🔐 Admin Access

The Super Admin user is `NDERITU`. This user:
- Has full admin privileges
- Can manage all users
- Can view activity logs
- Can access system settings
- Cannot be deleted or demoted

The Admin panel is hidden from regular users.

## 📝 Environment Variables

```env
# Database Configuration
DB_NAME_1=hometracker
DB_HOST_1=localhost
DB_USER_1=your_username
DB_PASSWORD_1=your_password
DB_PORT_1=3306

# Application Settings
APP_SECRET_KEY=your-secret-key
DEBUG=False
SESSION_TIMEOUT_HOURS=24
```

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MySQL + SQLAlchemy
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **Security**: bcrypt
- **Styling**: Custom CSS

## 📄 License

MIT License - feel free to use and modify!

## 👨‍💻 Developer

**Joseph Nderitu**
- Email: josephnderito16@gmail.com
- GitHub: github.com/josephndex

---

<p align="center">
  Made with ❤️ by Joseph Nderitu
</p>
