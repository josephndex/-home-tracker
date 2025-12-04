"""
Authentication Module for HomeTracker - Smart Home Management System
Handles user authentication, registration, and activity logging
"""
import streamlit as st
import hashlib
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

# Try to import bcrypt for secure password hashing
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logging.warning("bcrypt not available, falling back to SHA-256 hashing")

from database import get_db_manager, get_database_credentials
from config import SUPER_ADMIN_USERNAME, SESSION_TIMEOUT_MINUTES

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AuthManager:
    """
    Authentication manager for user login, registration, and activity logging.
    """
    
    def __init__(self, db_config: int = 1):
        self.db_config = db_config
        self.engine = None
        self._create_engine()
    
    def _create_engine(self) -> bool:
        """Create database engine."""
        try:
            db_name, host, user, password = get_database_credentials(self.db_config)
            
            # Check required fields (password can be empty for local development)
            if not all([db_name, host, user]):
                logger.error("Missing database credentials for auth")
                return False
            
            # Handle empty password
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
            return True
            
        except Exception as e:
            logger.error(f"Failed to create auth engine: {e}")
            return False
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt or SHA-256."""
        if BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt(rounds=12)
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            salt = os.urandom(16).hex()
            hash_value = hashlib.sha256((password + salt).encode()).hexdigest()
            return f"{salt}${hash_value}"
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify a password against a stored hash."""
        if BCRYPT_AVAILABLE and stored_hash.startswith('$2'):
            try:
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            except Exception:
                return False
        elif '$' in stored_hash and not stored_hash.startswith('$2'):
            try:
                salt, hash_value = stored_hash.split('$', 1)
                computed = hashlib.sha256((password + salt).encode()).hexdigest()
                return computed == hash_value
            except Exception:
                return False
        else:
            return hashlib.sha256(password.encode()).hexdigest() == stored_hash
    
    def register_user(self, username: str, email: str, password: str, full_name: str = "") -> Tuple[bool, str]:
        """Register a new user."""
        if not self.engine:
            return False, "Database connection not available"
        
        # Check if this is the super admin (NDERITU)
        is_super_admin = username.strip().upper() == SUPER_ADMIN_USERNAME
        
        try:
            password_hash = self.hash_password(password)
            
            insert_query = text("""
                INSERT INTO ht_users (username, email, password_hash, full_name, is_admin, created_at)
                VALUES (:username, :email, :password_hash, :full_name, :is_admin, :created_at)
            """)
            
            with self.engine.connect() as conn:
                conn.execute(insert_query, {
                    "username": username.strip(),
                    "email": email.strip().lower(),
                    "password_hash": password_hash,
                    "full_name": full_name.strip(),
                    "is_admin": is_super_admin,
                    "created_at": datetime.now()
                })
                conn.commit()
            
            self.log_activity(None, username, "USER_REGISTERED", "registration", f"New user registered: {email}")
            logger.info(f"User registered: {username}")
            
            if is_super_admin:
                return True, "Super Admin account created successfully! You have full access."
            
            return True, "Registration successful! You can now log in."
            
        except SQLAlchemyError as e:
            error_msg = str(e)
            if "Duplicate entry" in error_msg:
                if "username" in error_msg:
                    return False, "Username already exists. Please choose a different username."
                elif "email" in error_msg:
                    return False, "Email already registered. Please use a different email."
            logger.error(f"Registration failed: {e}")
            return False, f"Registration failed: {error_msg}"
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"An error occurred: {str(e)}"
    
    def authenticate_user(self, username_or_email: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """Authenticate a user."""
        if not self.engine:
            return False, None, "Database connection not available"
        
        try:
            query = text("""
                SELECT id, username, email, full_name, is_active, is_admin, 
                       last_page, session_data, password_hash
                FROM ht_users
                WHERE (username = :identifier OR email = :identifier)
                AND is_active = TRUE
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"identifier": username_or_email.strip()})
                user = result.fetchone()
            
            if not user:
                return False, None, "Invalid username/email or password"
            
            stored_hash = user[8]
            if not self.verify_password(password, stored_hash):
                self.log_activity(None, username_or_email, "LOGIN_FAILED", "login", "Invalid password attempt")
                return False, None, "Invalid username/email or password"
            
            user_data = {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "full_name": user[3],
                "is_active": user[4],
                "is_admin": user[5],
                "last_page": user[6],
                "session_data": user[7],
                "session_id": str(uuid.uuid4()),
                "login_time": datetime.now().isoformat()
            }
            
            # Auto-upgrade super admin
            if user_data["username"].upper() == SUPER_ADMIN_USERNAME and not user_data["is_admin"]:
                upgrade_query = text("UPDATE ht_users SET is_admin = TRUE WHERE id = :user_id")
                with self.engine.connect() as conn:
                    conn.execute(upgrade_query, {"user_id": user_data["id"]})
                    conn.commit()
                user_data["is_admin"] = True
            
            # Update last login
            update_query = text("UPDATE ht_users SET last_login = :last_login WHERE id = :user_id")
            with self.engine.connect() as conn:
                conn.execute(update_query, {"last_login": datetime.now(), "user_id": user_data["id"]})
                conn.commit()
            
            self.log_activity(user_data["id"], user_data["username"], "USER_LOGIN", "login", "User logged in")
            logger.info(f"User authenticated: {user_data['username']}")
            
            return True, user_data, "Login successful!"
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None, f"An error occurred: {str(e)}"
    
    def log_activity(self, user_id: Optional[int], username: str, action: str, page: str = "", details: str = ""):
        """Log user activity to the database."""
        if not self.engine:
            return
        
        try:
            insert_query = text("""
                INSERT INTO ht_activity_logs (user_id, username, action, page, details, timestamp)
                VALUES (:user_id, :username, :action, :page, :details, :timestamp)
            """)
            
            with self.engine.connect() as conn:
                conn.execute(insert_query, {
                    "user_id": user_id,
                    "username": username,
                    "action": action,
                    "page": page,
                    "details": details,
                    "timestamp": datetime.now()
                })
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    def save_user_session(self, user_id: int, page: str, session_data: str = ""):
        """Save user's current page and session data."""
        if not self.engine:
            return
        
        try:
            update_query = text("""
                UPDATE ht_users SET last_page = :page, session_data = :session_data
                WHERE id = :user_id
            """)
            
            with self.engine.connect() as conn:
                conn.execute(update_query, {
                    "page": page,
                    "session_data": session_data,
                    "user_id": user_id
                })
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
    
    def get_all_users(self) -> list:
        """Get all users (admin function)."""
        if not self.engine:
            return []
        
        try:
            query = text("""
                SELECT id, username, email, full_name, is_active, is_admin, created_at, last_login
                FROM ht_users
                ORDER BY created_at DESC
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query)
                users = result.fetchall()
            
            return [
                {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "full_name": user[3],
                    "is_active": user[4],
                    "is_admin": user[5],
                    "created_at": user[6],
                    "last_login": user[7],
                    "is_super_admin": user[1].upper() == SUPER_ADMIN_USERNAME
                }
                for user in users
            ]
            
        except Exception as e:
            logger.error(f"Failed to get users: {e}")
            return []
    
    def set_user_admin_status(self, user_id: int, is_admin: bool, by_user: str) -> Tuple[bool, str]:
        """Set a user's admin status."""
        if not self.engine:
            return False, "Database connection not available"
        
        try:
            check_query = text("SELECT username FROM ht_users WHERE id = :user_id")
            with self.engine.connect() as conn:
                result = conn.execute(check_query, {"user_id": user_id})
                user = result.fetchone()
            
            if user and user[0].upper() == SUPER_ADMIN_USERNAME:
                return False, "Cannot modify super admin's status"
            
            update_query = text("UPDATE ht_users SET is_admin = :is_admin WHERE id = :user_id")
            with self.engine.connect() as conn:
                conn.execute(update_query, {"is_admin": is_admin, "user_id": user_id})
                conn.commit()
            
            action = "ADMIN_GRANTED" if is_admin else "ADMIN_REVOKED"
            self.log_activity(None, by_user, action, "admin", f"User ID {user_id} admin status: {is_admin}")
            
            return True, f"User admin status {'granted' if is_admin else 'revoked'}"
            
        except Exception as e:
            logger.error(f"Failed to update admin status: {e}")
            return False, f"Error: {str(e)}"
    
    def set_user_active_status(self, user_id: int, is_active: bool, by_user: str) -> Tuple[bool, str]:
        """Activate or deactivate a user."""
        if not self.engine:
            return False, "Database connection not available"
        
        try:
            check_query = text("SELECT username FROM ht_users WHERE id = :user_id")
            with self.engine.connect() as conn:
                result = conn.execute(check_query, {"user_id": user_id})
                user = result.fetchone()
            
            if user and user[0].upper() == SUPER_ADMIN_USERNAME:
                return False, "Cannot deactivate super admin"
            
            update_query = text("UPDATE ht_users SET is_active = :is_active WHERE id = :user_id")
            with self.engine.connect() as conn:
                conn.execute(update_query, {"is_active": is_active, "user_id": user_id})
                conn.commit()
            
            action = "USER_ACTIVATED" if is_active else "USER_DEACTIVATED"
            self.log_activity(None, by_user, action, "admin", f"User ID {user_id} active: {is_active}")
            
            return True, f"User {'activated' if is_active else 'deactivated'}"
            
        except Exception as e:
            logger.error(f"Failed to update user status: {e}")
            return False, f"Error: {str(e)}"
    
    def delete_user(self, user_id: int, by_user: str) -> Tuple[bool, str]:
        """Permanently delete a user account."""
        if not self.engine:
            return False, "Database connection not available"
        
        try:
            check_query = text("SELECT username, email FROM ht_users WHERE id = :user_id")
            with self.engine.connect() as conn:
                result = conn.execute(check_query, {"user_id": user_id})
                user = result.fetchone()
            
            if not user:
                return False, "User not found"
            
            if user[0].upper() == SUPER_ADMIN_USERNAME:
                return False, "Cannot delete the Super Admin account"
            
            # Delete user's activity logs first
            delete_logs_query = text("DELETE FROM ht_activity_logs WHERE user_id = :user_id")
            delete_user_query = text("DELETE FROM ht_users WHERE id = :user_id")
            
            with self.engine.connect() as conn:
                conn.execute(delete_logs_query, {"user_id": user_id})
                conn.execute(delete_user_query, {"user_id": user_id})
                conn.commit()
            
            self.log_activity(None, by_user, "USER_DELETED", "admin", f"Deleted user: {user[0]} ({user[1]})")
            return True, f"User '{user[0]}' has been deleted"
            
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            return False, f"Error: {str(e)}"
    
    def get_activity_logs(self, limit: int = 100) -> list:
        """Get activity logs."""
        if not self.engine:
            return []
        
        try:
            query = text("""
                SELECT id, username, action, page, details, timestamp
                FROM ht_activity_logs
                ORDER BY timestamp DESC
                LIMIT :limit
            """)
            
            with self.engine.connect() as conn:
                result = conn.execute(query, {"limit": limit})
                logs = result.fetchall()
            
            return [
                {
                    "id": log[0],
                    "username": log[1],
                    "action": log[2],
                    "page": log[3],
                    "details": log[4],
                    "timestamp": log[5]
                }
                for log in logs
            ]
            
        except Exception as e:
            logger.error(f"Failed to get activity logs: {e}")
            return []


# Singleton instance
_auth_manager = None


def get_auth_manager(db_config: int = 1) -> AuthManager:
    """Get the singleton AuthManager instance."""
    global _auth_manager
    if _auth_manager is None or _auth_manager.db_config != db_config:
        _auth_manager = AuthManager(db_config)
    return _auth_manager


def check_session_timeout() -> bool:
    """Check if the current session has timed out."""
    if 'last_activity' not in st.session_state:
        return True
    
    last_activity = st.session_state.get('last_activity')
    if last_activity:
        try:
            if isinstance(last_activity, str):
                last_activity = datetime.fromisoformat(last_activity)
            
            if datetime.now() - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                return False
        except:
            pass
    
    return True


def update_activity():
    """Update the last activity timestamp."""
    st.session_state['last_activity'] = datetime.now()


def check_authentication() -> bool:
    """Check if user is authenticated and session is valid."""
    if not st.session_state.get('authenticated', False):
        return False
    
    if not check_session_timeout():
        user = st.session_state.get('user')
        if user:
            auth = get_auth_manager()
            auth.log_activity(user.get('id'), user.get('username', 'Unknown'), 
                            "SESSION_TIMEOUT", "security", "Session timed out")
        
        for key in ['authenticated', 'user', 'last_activity']:
            if key in st.session_state:
                del st.session_state[key]
        
        st.warning("⏰ Your session has timed out. Please log in again.")
        return False
    
    update_activity()
    return True


def get_current_user() -> Optional[Dict]:
    """Get the current logged-in user data."""
    if check_authentication():
        return st.session_state.get('user', None)
    return None


def require_authentication():
    """Require authentication - redirects to login if not authenticated."""
    if not check_authentication():
        st.warning("Please log in to access this page.")
        try:
            st.switch_page("pages/0_Login.py")
        except:
            st.rerun()
        st.stop()


def logout():
    """Log out the current user."""
    auth = get_auth_manager()
    user = get_current_user()
    
    if user:
        auth.log_activity(user.get('id'), user.get('username', 'Unknown'), "USER_LOGOUT", "logout", "User logged out")
    
    keys_to_clear = ['authenticated', 'user', 'last_activity', 'session_id']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state['authenticated'] = False


def is_super_admin(user: Optional[Dict] = None) -> bool:
    """Check if user is the super admin."""
    if user is None:
        user = get_current_user()
    if user:
        return user.get('username', '').upper() == SUPER_ADMIN_USERNAME
    return False


def is_admin(user: Optional[Dict] = None) -> bool:
    """Check if user is an admin."""
    if user is None:
        user = get_current_user()
    if user:
        return user.get('is_admin', False) or is_super_admin(user)
    return False


def require_admin():
    """Require admin access."""
    require_authentication()
    user = get_current_user()
    if not is_admin(user):
        st.error("Access Denied. Admin privileges required.")
        st.stop()


def log_page_visit(page_name: str):
    """Log when a user visits a page."""
    auth = get_auth_manager()
    user = get_current_user()
    
    if user:
        auth.log_activity(user.get('id'), user.get('username', 'Unknown'), 
                         "PAGE_VISIT", page_name, f"Visited {page_name}")
        if user.get('id'):
            auth.save_user_session(user.get('id'), page_name)


# ==================== ADMIN HELPER FUNCTIONS ====================

def get_all_users() -> list:
    """Get all users (admin function)."""
    auth = get_auth_manager()
    return auth.get_all_users()


def update_user_role(user_id: int, is_admin: bool) -> Tuple[bool, str]:
    """Update user admin role."""
    auth = get_auth_manager()
    current_user = get_current_user()
    by_user = current_user.get('username', 'Unknown') if current_user else 'System'
    return auth.set_user_admin_status(user_id, is_admin, by_user)


def delete_user(user_id: int) -> Tuple[bool, str]:
    """Delete a user."""
    auth = get_auth_manager()
    current_user = get_current_user()
    by_user = current_user.get('username', 'Unknown') if current_user else 'System'
    return auth.delete_user(user_id, by_user)


def get_activity_logs(limit: int = 100) -> list:
    """Get activity logs."""
    auth = get_auth_manager()
    return auth.get_activity_logs(limit)


def update_user_profile(user_id: int, profile_data: Dict) -> Tuple[bool, str]:
    """Update user profile."""
    auth = get_auth_manager()
    
    if not auth.engine:
        return False, "Database connection not available"
    
    try:
        update_query = text("""
            UPDATE ht_users SET 
                full_name = :full_name,
                email = :email,
                phone = :phone,
                bio = :bio,
                updated_at = NOW()
            WHERE id = :user_id
        """)
        
        with auth.engine.connect() as conn:
            conn.execute(update_query, {
                "full_name": profile_data.get('full_name', ''),
                "email": profile_data.get('email', ''),
                "phone": profile_data.get('phone', ''),
                "bio": profile_data.get('bio', ''),
                "user_id": user_id
            })
            conn.commit()
        
        return True, "Profile updated successfully"
        
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        return False, f"Error: {str(e)}"


def change_password(user_id: int, current_password: str, new_password: str) -> Tuple[bool, str]:
    """Change user password."""
    auth = get_auth_manager()
    
    if not auth.engine:
        return False, "Database connection not available"
    
    try:
        # Verify current password
        query = text("SELECT password_hash FROM ht_users WHERE id = :user_id")
        with auth.engine.connect() as conn:
            result = conn.execute(query, {"user_id": user_id})
            row = result.fetchone()
        
        if not row:
            return False, "User not found"
        
        if not auth.verify_password(current_password, row[0]):
            return False, "Current password is incorrect"
        
        # Update password
        new_hash = auth.hash_password(new_password)
        update_query = text("UPDATE ht_users SET password_hash = :password_hash WHERE id = :user_id")
        with auth.engine.connect() as conn:
            conn.execute(update_query, {"password_hash": new_hash, "user_id": user_id})
            conn.commit()
        
        return True, "Password changed successfully"
        
    except Exception as e:
        logger.error(f"Failed to change password: {e}")
        return False, f"Error: {str(e)}"
