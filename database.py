"""
Database module for HomeTracker - Smart Home Management System
Handles all database connections and operations
"""
import os
import logging
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
import streamlit as st
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime, Float, Boolean, Text, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

Base = declarative_base()


def get_database_credentials(db_config: int = 1) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Get database credentials from environment variables, Streamlit secrets, or .env file.
    
    Args:
        db_config: Database configuration number (1=Remote, 2=Local)
        
    Returns:
        Tuple of (db_name, host, user, password)
    """
    db_name = None
    host = None
    user = None
    password = None
    
    # Try environment variables first (for Docker deployment)
    db_name = os.environ.get(f'DB_NAME_{db_config}')
    host = os.environ.get(f'DB_HOST_{db_config}')
    user = os.environ.get(f'DB_USER_{db_config}')
    password = os.environ.get(f'DB_PASSWORD_{db_config}', '')  # Allow empty password
    
    if db_name and host and user:
        logger.info(f"Using environment variables for database config {db_config}")
        return db_name, host, user, password
    
    # Try Streamlit secrets second (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and f'database_{db_config}' in st.secrets:
            secrets = st.secrets[f'database_{db_config}']
            db_name = secrets.get('DB_NAME', '')
            host = secrets.get('DB_HOST', '')
            user = secrets.get('DB_USER', '')
            password = secrets.get('DB_PASSWORD', '')  # Allow empty password
            
            if db_name and host and user:
                logger.info(f"Using Streamlit secrets for database config {db_config}")
                return db_name, host, user, password
    except Exception as e:
        logger.debug(f"Streamlit secrets not available: {e}")
    
    # Fall back to .env file (for local development)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(current_dir, '.env')
    
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        db_name = os.getenv(f'DB_NAME_{db_config}')
        host = os.getenv(f'DB_HOST_{db_config}')
        user = os.getenv(f'DB_USER_{db_config}')
        password = os.getenv(f'DB_PASSWORD_{db_config}', '')  # Allow empty password
        logger.info(f"Using .env file for database config {db_config}")
    
    return db_name, host, user, password


class DatabaseManager:
    """
    Database manager for HomeTracker application.
    Handles all database operations including table creation and CRUD operations.
    """
    
    def __init__(self, db_config: int = 1):
        self.engine = None
        self.db_config = db_config
        self._create_engine()
    
    def _create_engine(self) -> bool:
        """Create database engine with error handling."""
        try:
            db_name, host, user, password = get_database_credentials(self.db_config)
            
            # Check required fields (password can be empty for local development)
            if not all([db_name, host, user]):
                logger.error("Missing database credentials")
                return False
            
            # Handle empty password (for local MySQL without password)
            password = password or ""
            
            engine_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{db_name}"
            self.engine = create_engine(
                engine_url,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            
            logger.info(f"Database engine created for config {self.db_config}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test database connection."""
        if not self.engine:
            return False
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create all required tables for HomeTracker."""
        if not self.engine:
            logger.error("Cannot create tables: No database engine")
            return False
        
        try:
            # Users table
            create_users_table = text("""
                CREATE TABLE IF NOT EXISTS ht_users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255),
                    phone VARCHAR(50),
                    bio TEXT,
                    role VARCHAR(50) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT TRUE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    last_page VARCHAR(255),
                    session_data TEXT
                )
            """)
            
            # Categories table
            create_categories_table = text("""
                CREATE TABLE IF NOT EXISTS ht_categories (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    category_type VARCHAR(50) DEFAULT 'expense',
                    icon VARCHAR(50),
                    color VARCHAR(20),
                    is_default BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Transactions table (expenses and budgets)
            create_transactions_table = text("""
                CREATE TABLE IF NOT EXISTS ht_transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    transaction_date DATE NOT NULL,
                    transaction_type ENUM('Budget', 'Expense') NOT NULL,
                    category_id INT,
                    amount DECIMAL(15, 2) NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES ht_users(id) ON DELETE SET NULL,
                    FOREIGN KEY (category_id) REFERENCES ht_categories(id) ON DELETE SET NULL
                )
            """)
            
            # Budgets table (monthly budgets per category)
            create_budgets_table = text("""
                CREATE TABLE IF NOT EXISTS ht_budgets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    category_id INT,
                    month INT NOT NULL,
                    year INT NOT NULL,
                    amount DECIMAL(15, 2) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_budget (user_id, category_id, month, year),
                    FOREIGN KEY (user_id) REFERENCES ht_users(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES ht_categories(id) ON DELETE CASCADE
                )
            """)
            
            # Financial goals table
            create_goals_table = text("""
                CREATE TABLE IF NOT EXISTS ht_goals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    goal_name VARCHAR(255) NOT NULL,
                    target_amount DECIMAL(15, 2) NOT NULL,
                    current_amount DECIMAL(15, 2) DEFAULT 0,
                    deadline DATE,
                    category VARCHAR(100) DEFAULT 'General',
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'In Progress',
                    priority VARCHAR(50) DEFAULT 'Medium',
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES ht_users(id) ON DELETE CASCADE
                )
            """)
            
            # Kitchen inventory table
            create_inventory_table = text("""
                CREATE TABLE IF NOT EXISTS ht_kitchen_inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    item_name VARCHAR(255) NOT NULL,
                    category VARCHAR(100),
                    quantity DECIMAL(10, 2) NOT NULL,
                    unit VARCHAR(50),
                    min_quantity DECIMAL(10, 2) DEFAULT 0,
                    expiry_date DATE,
                    location VARCHAR(100),
                    notes TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES ht_users(id) ON DELETE CASCADE
                )
            """)
            
            # Shopping list table
            create_shopping_list_table = text("""
                CREATE TABLE IF NOT EXISTS ht_shopping_list (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    item_name VARCHAR(255) NOT NULL,
                    category VARCHAR(100),
                    quantity DECIMAL(10, 2),
                    unit VARCHAR(50),
                    estimated_price DECIMAL(15, 2),
                    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
                    is_purchased BOOLEAN DEFAULT FALSE,
                    purchased_at DATETIME,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES ht_users(id) ON DELETE CASCADE
                )
            """)
            
            # Meal plans table
            create_meal_plans_table = text("""
                CREATE TABLE IF NOT EXISTS ht_meal_plans (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    plan_date DATE NOT NULL,
                    meal_type ENUM('Breakfast', 'Lunch', 'Dinner', 'Snack', 'Dessert') NOT NULL,
                    meal_name VARCHAR(255) NOT NULL,
                    ingredients TEXT,
                    recipe TEXT,
                    notes TEXT,
                    is_prepared BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES ht_users(id) ON DELETE CASCADE
                )
            """)
            
            # Activity logs table
            create_logs_table = text("""
                CREATE TABLE IF NOT EXISTS ht_activity_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    username VARCHAR(100),
                    action VARCHAR(100) NOT NULL,
                    page VARCHAR(255),
                    details TEXT,
                    ip_address VARCHAR(50),
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES ht_users(id) ON DELETE SET NULL
                )
            """)
            
            # Execute all table creations
            with self.engine.connect() as conn:
                conn.execute(create_users_table)
                conn.execute(create_categories_table)
                conn.execute(create_transactions_table)
                conn.execute(create_budgets_table)
                conn.execute(create_goals_table)
                conn.execute(create_inventory_table)
                conn.execute(create_shopping_list_table)
                conn.execute(create_meal_plans_table)
                conn.execute(create_logs_table)
                conn.commit()
            
            logger.info("All HomeTracker tables created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            return False
    
    def initialize_default_categories(self) -> bool:
        """Initialize default categories if they don't exist."""
        from config import DEFAULT_CATEGORIES
        
        if not self.engine:
            return False
        
        try:
            for category in DEFAULT_CATEGORIES:
                check_query = text("SELECT id FROM ht_categories WHERE name = :name")
                insert_query = text("""
                    INSERT INTO ht_categories (name, category_type, is_default, is_active)
                    VALUES (:name, 'expense', TRUE, TRUE)
                """)
                
                with self.engine.connect() as conn:
                    result = conn.execute(check_query, {"name": category})
                    if not result.fetchone():
                        conn.execute(insert_query, {"name": category})
                    conn.commit()
            
            logger.info("Default categories initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize categories: {e}")
            return False


# Singleton instance
_db_manager = None


def get_db_manager(db_config: int = 1) -> DatabaseManager:
    """Get the singleton DatabaseManager instance."""
    global _db_manager
    if _db_manager is None or _db_manager.db_config != db_config:
        _db_manager = DatabaseManager(db_config)
    return _db_manager


def init_database(db_config: int = 1) -> bool:
    """Initialize the database - create tables and default data."""
    db = get_db_manager(db_config)
    
    if not db.test_connection():
        logger.error("Cannot initialize database: Connection failed")
        return False
    
    if not db.create_tables():
        logger.error("Failed to create tables")
        return False
    
    if not db.initialize_default_categories():
        logger.error("Failed to initialize default categories")
        return False
    
    logger.info("Database initialized successfully")
    return True
