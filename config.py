"""
Configuration settings for HomeTracker - Smart Home Management System
A comprehensive home management application with focus on kitchen management
"""
import os

# App Settings
APP_TITLE = "HomeTracker - Smart Home Management"
APP_VERSION = "2.0.0"
APP_ICON = "🏠"
PAGE_LAYOUT = "wide"

# Developer Info
DEVELOPER_NAME = "Joseph Nderitu"
DEVELOPER_EMAIL = "josephnderito16@gmail.com"
DEVELOPER_GITHUB = "github.com/josephndex"

# Data Settings
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Theme Colors - STUNNING Teal/Cyan/Rose palette
THEME_COLORS = {
    'primary': '#14b8a6',       # Vibrant teal
    'secondary': '#f43f5e',     # Beautiful rose
    'accent': '#06b6d4',        # Cyan blue
    'gradient_start': '#14b8a6',
    'gradient_mid': '#06b6d4',
    'gradient_end': '#f43f5e',
    'success': '#14b8a6',
    'warning': '#fbbf24',
    'danger': '#ef4444',
    'info': '#06b6d4',
    'dark': '#0f172a',
    'darker': '#042f2e',
    'card_bg': '#134e4a',
    'text_primary': '#f1f5f9',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
    'border': 'rgba(20, 184, 166, 0.3)',
    'glow_teal': 'rgba(20, 184, 166, 0.4)',
    'glow_rose': 'rgba(244, 63, 94, 0.3)',
    'light': '#f8f9fa'
}

# Categories - Focused on Home & Kitchen Management
DEFAULT_CATEGORIES = [
    # Kitchen & Food
    "Groceries",
    "Vegetables", 
    "Meat & Poultry",
    "Fish & Seafood",
    "Fruits",
    "Dairy & Eggs",
    "Beverages",
    "Snacks",
    "Baking Supplies",
    "Spices & Condiments",
    "Cooking Gas",
    "Kitchen Supplies",
    "Kitchen Appliances",
    # Home Maintenance
    "Cleaning Supplies",
    "Utilities (Water)",
    "Utilities (Electricity)",
    "House Maintenance",
    "Furniture",
    "Home Decor",
    # Personal & Family
    "Health & Medicine",
    "Personal Care",
    "Clothing",
    "Education",
    "Entertainment",
    "Transportation",
    "Others"
]

# Kitchen-specific categories with emojis for inventory
KITCHEN_CATEGORIES = {
    "Groceries": "🛒",
    "Vegetables": "🥬",
    "Meat & Poultry": "🍖",
    "Fish & Seafood": "🐟",
    "Fruits": "🍎",
    "Dairy & Eggs": "🥛",
    "Beverages": "🥤",
    "Snacks": "🍪",
    "Cooking Oil": "🫒",
    "Spices & Seasonings": "🧂",
    "Baking Supplies": "🧁",
    "Cleaning Supplies": "🧹",
    "Kitchen Supplies": "🍳",
    "Cooking Gas": "🔥",
    "Grains & Cereals": "🌾",
    "Canned Goods": "🥫",
    "Frozen Foods": "🧊",
    "Condiments": "🍯"
}

# Units for kitchen inventory
INVENTORY_UNITS = [
    "kg", "g", "lbs", "oz",  # Weight
    "L", "ml", "cups", "tbsp", "tsp",  # Volume
    "pieces", "packs", "bottles", "cans", "bags",  # Count
    "bunches", "bundles", "loaves", "dozens"  # Other
]

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

# Budget Thresholds
BUDGET_THRESHOLDS = {
    'excellent': 50,   # Under 50% spent
    'good': 75,        # 50-75% spent
    'warning': 90,     # 75-90% spent
    'danger': 100      # Over 90% spent
}

# Database configurations  
# Config 1: Remote server | Config 2: Local server
DB_CONFIGS = {
    1: "Remote Server (NDERITU)",
    2: "Local Server (localhost)"
}

# Meal types for planning
MEAL_TYPES = [
    "Breakfast",
    "Lunch", 
    "Dinner",
    "Snack",
    "Dessert"
]

# Days of the week
DAYS_OF_WEEK = [
    "Monday",
    "Tuesday",
    "Wednesday", 
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
]

# Chart dimensions
CHART_HEIGHT = 600
CHART_WIDTH = 1200

# Session timeout in minutes
SESSION_TIMEOUT_MINUTES = 30

# Super Admin username
SUPER_ADMIN_USERNAME = "NDERITU"
