"""
Login Page - User Authentication for HomeTracker
"""
import streamlit as st
import sys
import re
import time
sys.path.insert(0, '..')

from config import APP_TITLE, DEVELOPER_NAME, SUPER_ADMIN_USERNAME
from auth import get_auth_manager, check_authentication, logout
from database import init_database

# Custom CSS for STUNNING login page
st.markdown("""
<style>
    /* Animated background */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1a0d2e, #0f172a, #1e1033);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Hide sidebar on login */
    section[data-testid="stSidebar"] {
        display: none;
    }
    
    /* Login header */
    .login-header {
        background: linear-gradient(135deg, #14b8a6 0%, #f43f5e 50%, #06b6d4 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 20px 50px rgba(20, 184, 166, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .login-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
        animation: headerShine 4s ease-in-out infinite;
    }
    
    @keyframes headerShine {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    .login-header h1, .login-header p {
        color: white !important;
        position: relative;
        z-index: 1;
    }
    
    .app-logo {
        font-size: 3.5rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 4px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
    }
    
    .app-tagline {
        font-size: 1.1rem;
        opacity: 0.95;
        font-weight: 400;
        letter-spacing: 2px;
    }
    
    /* Welcome container */
    .welcome-container {
        background: linear-gradient(135deg, #14b8a6 0%, #ea580c 50%, #dc2626 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 15px 40px rgba(20, 184, 166, 0.4);
        animation: pulse-glow 2s infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 15px 40px rgba(20, 184, 166, 0.4); }
        50% { box-shadow: 0 20px 50px rgba(20, 184, 166, 0.6); }
    }
    
    .welcome-title {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .welcome-user {
        color: white !important;
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    /* Footer */
    .login-footer {
        text-align: center;
        color: #6b7280;
        margin-top: 2rem;
        font-size: 0.85rem;
    }
    
    .login-footer .signature {
        background: linear-gradient(90deg, #14b8a6, #ea580c, #14b8a6);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        font-weight: 600;
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }
</style>
""", unsafe_allow_html=True)


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str) -> tuple:
    """Validate password strength."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, ""


def render_login_form():
    """Render the login form."""
    st.markdown("### Sign In to Your Account")
    
    with st.form("login_form", clear_on_submit=False):
        username_email = st.text_input(
            "Username or Email",
            placeholder="Enter your username or email",
            key="login_username"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            if not username_email or not password:
                st.error("Please fill in all fields")
                return
            
            auth = get_auth_manager()
            success, user_data, message = auth.authenticate_user(username_email, password)
            
            if success and user_data:
                st.session_state['authenticated'] = True
                st.session_state['user'] = user_data
                
                user_name = user_data.get('full_name', user_data.get('username', 'User'))
                st.markdown(f"""
                <div class='welcome-container'>
                    <p class='welcome-title'>Welcome to HomeTracker!</p>
                    <p class='welcome-user'>{user_name}</p>
                </div>
                """, unsafe_allow_html=True)
                
                time.sleep(2)
                try:
                    st.switch_page("pages/1_Home.py")
                except:
                    st.rerun()
            else:
                st.error(f"{message}")


def render_registration_form():
    """Render the registration form."""
    st.markdown("### Create New Account")
    
    # Initialize database before registration
    init_database()
    
    with st.form("registration_form", clear_on_submit=True):
        full_name = st.text_input(
            "Full Name",
            placeholder="Enter your full name",
            key="reg_fullname"
        )
        
        username = st.text_input(
            "Username",
            placeholder="Choose a unique username",
            key="reg_username"
        )
        
        email = st.text_input(
            "Email",
            placeholder="Enter your email address",
            key="reg_email"
        )
        
        # Check if super admin
        is_super_admin_registration = username.strip().upper() == SUPER_ADMIN_USERNAME if username else False
        
        if is_super_admin_registration:
            st.success(f"Username '{SUPER_ADMIN_USERNAME}' is the **Super Admin** with full access!")
        
        col1, col2 = st.columns(2)
        with col1:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a password",
                key="reg_password"
            )
        with col2:
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Confirm password",
                key="reg_confirm"
            )
        
        submitted = st.form_submit_button("Create Account", use_container_width=True)
        
        if submitted:
            if not all([full_name, username, email, password, confirm_password]):
                st.error("Please fill in all fields")
                return
            
            if not validate_email(email):
                st.error("Please enter a valid email address")
                return
            
            valid_password, password_error = validate_password(password)
            if not valid_password:
                st.error(password_error)
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if len(username) < 3:
                st.error("Username must be at least 3 characters")
                return
            
            auth = get_auth_manager()
            success, message = auth.register_user(username, email, password, full_name)
            
            if success:
                st.success(f"{message}")
                st.info("Switch to the Login tab to sign in")
            else:
                st.error(f"{message}")


# Main page content
if check_authentication():
    # Already logged in
    user = st.session_state.get('user', {})
    user_name = user.get('full_name', user.get('username', 'User'))
    
    st.markdown(f"""
    <div class='welcome-container'>
        <p class='welcome-title'>Welcome to HomeTracker!</p>
        <p class='welcome-user'>{user_name}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style='background: #1e293b; padding: 1.5rem; border-radius: 15px; border: 1px solid #475569;'>
            <p style='color: #e2e8f0; margin-bottom: 1rem;'>
                <strong>Username:</strong> {user.get('username', 'N/A')}<br>
                <strong>Email:</strong> {user.get('email', 'N/A')}<br>
                <strong>Name:</strong> {user.get('full_name', 'N/A')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Go to Dashboard", use_container_width=True):
                try:
                    st.switch_page("pages/1_Home.py")
                except:
                    st.rerun()
        
        with col_b:
            if st.button("Logout", use_container_width=True, type="secondary"):
                logout()
                st.rerun()

else:
    # Show login/registration forms
    st.markdown("""
    <div class='login-header'>
        <p class='app-logo'>🏠 HomeTracker</p>
        <p class='app-tagline'>Smart Home Management System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs(["Sign In", "Register"])
    
    with tab1:
        render_login_form()
    
    with tab2:
        render_registration_form()
    
    # Help section
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6b7280; padding: 1rem;'>
        <p><strong>First time here?</strong></p>
        <p>Register a new account to start managing your home expenses and kitchen inventory.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class='login-footer'>
    <p>© 2025 <span class='signature'>Joseph Nderitu</span> | All rights reserved</p>
    <p>Your data is protected with secure authentication</p>
</div>
""", unsafe_allow_html=True)
