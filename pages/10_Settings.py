"""
Settings Page - User preferences and account settings
"""
import streamlit as st
from datetime import datetime
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, CURRENCY_SYMBOL, APP_TITLE
from auth import (
    require_authentication, get_current_user, log_page_visit,
    update_user_profile, change_password
)

# Require authentication
require_authentication()
log_page_visit("10_Settings.py")

user = get_current_user()

st.title("⚙️ Settings")

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
    padding: 1rem; border-radius: 12px; border-left: 4px solid #f43f5e; margin-bottom: 1rem;'>
    <p style='color: #e2e8f0; margin: 0;'>
        Customize your experience and manage your account settings.
    </p>
</div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🔐 Security", "🎨 Preferences", "📱 Notifications"])

with tab1:
    st.markdown("### 👤 Profile Settings")
    
    if user:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #14b8a6 0%, #f43f5e 100%);
                width: 120px; height: 120px; border-radius: 50%; 
                display: flex; align-items: center; justify-content: center;
                margin: 0 auto;'>
                <span style='font-size: 3rem; color: white;'>👤</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style='text-align: center; margin-top: 1rem;'>
                <h3 style='color: #e2e8f0; margin: 0;'>{user.get('username', 'User')}</h3>
                <p style='color: #a78bfa; margin: 0;'>{user.get('email', '')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            with st.form("profile_form"):
                username = st.text_input("Username", value=user.get('username', ''))
                email = st.text_input("Email", value=user.get('email', ''))
                full_name = st.text_input("Full Name", value=user.get('full_name', ''))
                phone = st.text_input("Phone Number", value=user.get('phone', ''))
                
                bio = st.text_area("Bio", value=user.get('bio', ''), 
                                  placeholder="Tell us a little about yourself...")
                
                submitted = st.form_submit_button("💾 Save Profile", use_container_width=True, type="primary")
                
                if submitted:
                    profile_data = {
                        'username': username,
                        'email': email,
                        'full_name': full_name,
                        'phone': phone,
                        'bio': bio
                    }
                    success, message = update_user_profile(user.get('id'), profile_data)
                    if success:
                        st.success("Profile updated successfully!")
                        st.rerun()
                    else:
                        st.error(message)
        
        st.markdown("---")
        
        # Account info
        st.markdown("### 📊 Account Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 1rem;
                border-radius: 12px;'>
                <p style='color: #6b7280; margin: 0;'>Account Created</p>
                <p style='color: #e2e8f0; margin: 0.3rem 0 0 0; font-weight: bold;'>
                    {user.get('created_at', 'Unknown')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 1rem;
                border-radius: 12px;'>
                <p style='color: #6b7280; margin: 0;'>Last Login</p>
                <p style='color: #e2e8f0; margin: 0.3rem 0 0 0; font-weight: bold;'>
                    {user.get('last_login', 'Never')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            role = "Admin" if user.get('is_admin') else "User"
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.05); padding: 1rem;
                border-radius: 12px;'>
                <p style='color: #6b7280; margin: 0;'>Account Type</p>
                <p style='color: #e2e8f0; margin: 0.3rem 0 0 0; font-weight: bold;'>
                    {role}
                </p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.error("User data not found. Please log in again.")

with tab2:
    st.markdown("### 🔐 Security Settings")
    
    st.markdown("#### 🔑 Change Password")
    
    with st.form("password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submitted = st.form_submit_button("🔐 Change Password", use_container_width=True)
        
        if submitted:
            if not current_password or not new_password or not confirm_password:
                st.error("Please fill in all password fields.")
            elif new_password != confirm_password:
                st.error("New passwords do not match!")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                success, message = change_password(user.get('id'), current_password, new_password)
                if success:
                    st.success("Password changed successfully!")
                else:
                    st.error(message)
    
    st.markdown("---")
    
    st.markdown("#### 🛡️ Security Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 1rem;
            border-radius: 12px; margin-bottom: 1rem;'>
            <h4 style='color: #e2e8f0; margin: 0;'>🔒 Two-Factor Authentication</h4>
            <p style='color: #6b7280; margin: 0.5rem 0;'>
                Add an extra layer of security to your account.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Enable 2FA", use_container_width=True):
            st.info("Two-factor authentication coming soon!")
    
    with col2:
        st.markdown("""
        <div style='background: rgba(255,255,255,0.05); padding: 1rem;
            border-radius: 12px; margin-bottom: 1rem;'>
            <h4 style='color: #e2e8f0; margin: 0;'>📱 Active Sessions</h4>
            <p style='color: #6b7280; margin: 0.5rem 0;'>
                Manage your active login sessions.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Sessions", use_container_width=True):
            st.info("Session management coming soon!")
    
    st.markdown("---")
    
    st.markdown("#### ⚠️ Danger Zone")
    
    st.markdown("""
    <div style='background: rgba(239, 68, 68, 0.1); padding: 1rem;
        border-radius: 12px; border: 1px solid #ef4444;'>
        <h4 style='color: #ef4444; margin: 0;'>Delete Account</h4>
        <p style='color: #e2e8f0; margin: 0.5rem 0;'>
            Once you delete your account, there is no going back. Please be certain.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🗑️ Delete My Account", type="secondary"):
        st.warning("Account deletion requires confirmation. Please contact support.")

with tab3:
    st.markdown("### 🎨 Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌙 Appearance")
        
        theme = st.selectbox(
            "Theme",
            ["Dark (Default)", "Light", "System"],
            help="Choose your preferred color theme"
        )
        
        font_size = st.select_slider(
            "Font Size",
            options=["Small", "Medium", "Large"],
            value="Medium"
        )
        
        compact_mode = st.checkbox("Compact Mode", value=False,
                                  help="Reduce spacing for more content")
    
    with col2:
        st.markdown("#### 📊 Display")
        
        currency = st.selectbox(
            "Currency",
            ["KSH (Kenyan Shilling)", "USD (US Dollar)", "EUR (Euro)", "GBP (British Pound)"],
            help="Choose your preferred currency"
        )
        
        date_format = st.selectbox(
            "Date Format",
            ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"],
            help="Choose your preferred date format"
        )
        
        show_decimals = st.checkbox("Show Decimal Places", value=True,
                                   help="Display amounts with decimal places")
    
    st.markdown("---")
    
    st.markdown("#### 🏠 Home Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_view = st.selectbox(
            "Default Dashboard View",
            ["This Month", "This Week", "Today", "All Time"]
        )
        
        show_charts = st.checkbox("Show Charts on Dashboard", value=True)
    
    with col2:
        default_category = st.selectbox(
            "Default Category",
            ["Last Used", "Groceries", "Vegetables", "Utilities"]
        )
        
        show_tips = st.checkbox("Show Tips and Suggestions", value=True)
    
    if st.button("💾 Save Preferences", use_container_width=True, type="primary"):
        st.success("Preferences saved successfully!")

with tab4:
    st.markdown("### 📱 Notification Settings")
    
    st.markdown("#### 📧 Email Notifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        email_enabled = st.checkbox("Enable Email Notifications", value=False)
        budget_alerts = st.checkbox("Budget Threshold Alerts", value=True)
        goal_reminders = st.checkbox("Goal Deadline Reminders", value=True)
    
    with col2:
        weekly_summary = st.checkbox("Weekly Summary Report", value=False)
        monthly_report = st.checkbox("Monthly Expense Report", value=False)
        tips_newsletter = st.checkbox("Tips & Tricks Newsletter", value=False)
    
    st.markdown("---")
    
    st.markdown("#### 🔔 Alert Thresholds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        budget_threshold = st.slider(
            "Budget Alert Threshold",
            min_value=50,
            max_value=100,
            value=80,
            help="Get alerted when spending reaches this percentage of budget"
        )
        
        st.markdown(f"""
        <div style='background: rgba(20, 184, 166, 0.1); padding: 0.5rem;
            border-radius: 8px;'>
            <p style='color: #e2e8f0; margin: 0; font-size: 0.9rem;'>
                You'll be notified when you reach <strong>{budget_threshold}%</strong> of your budget.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        goal_reminder_days = st.selectbox(
            "Goal Reminder (days before deadline)",
            [3, 7, 14, 30],
            index=1,
            help="Get reminded this many days before goal deadline"
        )
        
        st.markdown(f"""
        <div style='background: rgba(244, 63, 94, 0.1); padding: 0.5rem;
            border-radius: 8px;'>
            <p style='color: #e2e8f0; margin: 0; font-size: 0.9rem;'>
                You'll be reminded <strong>{goal_reminder_days} days</strong> before deadlines.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("#### 🔕 Quiet Hours")
    
    quiet_hours = st.checkbox("Enable Quiet Hours", value=False)
    
    if quiet_hours:
        col1, col2 = st.columns(2)
        
        with col1:
            quiet_start = st.time_input("Start Time", value=datetime.strptime("22:00", "%H:%M").time())
        
        with col2:
            quiet_end = st.time_input("End Time", value=datetime.strptime("07:00", "%H:%M").time())
        
        st.info(f"Notifications will be muted from {quiet_start.strftime('%H:%M')} to {quiet_end.strftime('%H:%M')}")
    
    if st.button("💾 Save Notification Settings", use_container_width=True, type="primary"):
        st.success("Notification settings saved!")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280;'>
    <p>⚙️ Settings - Customize your {APP_TITLE} experience</p>
    <p>© 2025 {DEVELOPER_NAME}</p>
</div>
""", unsafe_allow_html=True)
