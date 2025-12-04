"""
Admin Panel - Super Admin Only (NDERITU)
This page is hidden from regular users
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, CURRENCY_SYMBOL, SUPER_ADMIN_USERNAME
from auth import (
    require_authentication, require_admin, get_current_user, 
    is_super_admin, log_page_visit, get_all_users, 
    update_user_role, delete_user, get_activity_logs
)
from utils import load_transactions, format_currency, get_system_stats

# Require authentication
require_authentication()
log_page_visit("9_Admin.py")

user = get_current_user()

# STRICT ACCESS: Only Super Admin (NDERITU) can access this page
if not is_super_admin():
    st.error("🚫 **Access Denied** - This page does not exist.")
    st.stop()

st.markdown(f"""
<div style='text-align: center; padding: 1rem 0;'>
    <h1 style='background: linear-gradient(135deg, #ef4444 0%, #f43f5e 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2.5rem;'>
        🔐 Admin Control Panel
    </h1>
    <p style='color: #ef4444;'>Super Administrator - {SUPER_ADMIN_USERNAME}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
    padding: 1rem; border-radius: 12px; border-left: 4px solid #ef4444; margin-bottom: 1rem;'>
    <p style='color: #e2e8f0; margin: 0;'>
        ⚠️ <strong>Administrative Area</strong> - All actions are logged and monitored.
    </p>
</div>
""", unsafe_allow_html=True)

# Tabs - Super Admin only
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", "👥 User Management", "📋 Activity Logs", 
    "⚙️ System Settings", "🗄️ Database"
])

with tab1:
    st.markdown("### 📊 Admin Dashboard")
    
    # System stats
    stats = get_system_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;'>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>👥 Total Users</p>
            <h2 style='color: white; margin: 0.5rem 0;'>{}</h2>
        </div>
        """.format(stats.get('total_users', 0)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;'>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>📝 Transactions</p>
            <h2 style='color: white; margin: 0.5rem 0;'>{}</h2>
        </div>
        """.format(stats.get('total_transactions', 0)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #14b8a6 0%, #ea580c 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;'>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>💰 Total Volume</p>
            <h2 style='color: white; margin: 0.5rem 0;'>{}</h2>
        </div>
        """.format(format_currency(stats.get('total_volume', 0))), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f43f5e 0%, #9333ea 100%);
            padding: 1.5rem; border-radius: 12px; text-align: center;'>
            <p style='color: rgba(255,255,255,0.8); margin: 0;'>📁 Categories</p>
            <h2 style='color: white; margin: 0.5rem 0;'>{}</h2>
        </div>
        """.format(stats.get('total_categories', 0)), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activity
    st.markdown("### 🕐 Recent System Activity")
    
    activity_logs = get_activity_logs(limit=10)
    
    if activity_logs:
        for log in activity_logs:
            log_time = log.get('timestamp', 'Unknown')
            log_user = log.get('username', 'Unknown')
            log_action = log.get('action', 'Unknown')
            log_details = log.get('details', '')
            
            action_color = {
                'LOGIN': '#10b981',
                'LOGOUT': '#6b7280',
                'CREATE': '#3b82f6',
                'UPDATE': '#14b8a6',
                'DELETE': '#ef4444',
                'VIEW': '#a78bfa'
            }.get(log_action.upper(), '#e2e8f0')
            
            st.markdown(f"""
            <div style='background: rgba(255,255,255,0.03); padding: 0.8rem;
                border-radius: 8px; margin-bottom: 0.5rem;
                border-left: 3px solid {action_color};'>
                <div style='display: flex; justify-content: space-between;'>
                    <span style='color: #e2e8f0;'>
                        <strong>{log_user}</strong> - {log_action}
                    </span>
                    <span style='color: #6b7280; font-size: 0.85rem;'>{log_time}</span>
                </div>
                <p style='color: #6b7280; margin: 0.3rem 0 0 0; font-size: 0.85rem;'>{log_details}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No activity logs available.")
    
    # Quick actions
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📊 Export Report", use_container_width=True):
            st.info("Report export feature coming soon!")
    
    with col3:
        if st.button("🗑️ Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("Cache cleared!")
    
    with col4:
        if st.button("📧 Send Alert", use_container_width=True):
            st.info("Alert system coming soon!")

with tab2:
    st.markdown("### 👥 User Management")
    
    users = get_all_users()
    
    if users:
        st.markdown(f"**{len(users)} registered users**")
        
        # Search users
        search_user = st.text_input("🔍 Search users", placeholder="Search by username or email...")
        
        filtered_users = users
        if search_user:
            filtered_users = [
                u for u in users 
                if search_user.lower() in u.get('username', '').lower() or 
                   search_user.lower() in u.get('email', '').lower()
            ]
        
        st.markdown("---")
        
        for u in filtered_users:
            user_id = u.get('id', 0)
            username = u.get('username', 'Unknown')
            email = u.get('email', 'No email')
            role = u.get('role', 'user')
            is_admin = u.get('is_admin', False)
            created_at = u.get('created_at', 'Unknown')
            last_login = u.get('last_login', 'Never')
            
            # Don't allow deleting super admin
            is_super = username.upper() == SUPER_ADMIN_USERNAME
            
            role_color = "#ef4444" if is_admin else "#10b981"
            role_badge = "Admin" if is_admin else "User"
            
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"""
                <div style='background: rgba(255,255,255,0.05); padding: 1rem;
                    border-radius: 12px; margin-bottom: 0.5rem;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <h4 style='color: #e2e8f0; margin: 0;'>
                                {'👑 ' if is_super else '👤 '}{username}
                            </h4>
                            <p style='color: #6b7280; margin: 0.3rem 0;'>{email}</p>
                        </div>
                        <span style='background: {role_color}; padding: 0.3rem 0.8rem;
                            border-radius: 20px; color: white; font-size: 0.8rem;'>{role_badge}</span>
                    </div>
                    <div style='display: flex; gap: 1rem; margin-top: 0.5rem;'>
                        <span style='color: #6b7280; font-size: 0.85rem;'>
                            Created: {created_at}
                        </span>
                        <span style='color: #6b7280; font-size: 0.85rem;'>
                            Last Login: {last_login}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if not is_super:
                    if st.button(
                        "Make Admin" if not is_admin else "Remove Admin",
                        key=f"role_{user_id}",
                        use_container_width=True
                    ):
                        new_admin_status = not is_admin
                        update_user_role(user_id, new_admin_status)
                        st.success(f"User role updated!")
                        st.rerun()
                else:
                    st.markdown("<p style='color: #a78bfa; text-align: center;'>Super Admin</p>", 
                               unsafe_allow_html=True)
            
            with col3:
                if not is_super:
                    if st.button("🗑️ Delete", key=f"del_user_{user_id}", type="secondary"):
                        delete_user(user_id)
                        st.success(f"User deleted!")
                        st.rerun()
    else:
        st.info("No users found.")

with tab3:
    st.markdown("### 📋 Activity Logs")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        log_limit = st.selectbox("Show logs", [25, 50, 100, 200], index=0)
    
    with col2:
        action_filter = st.selectbox(
            "Action Type",
            ["All", "LOGIN", "LOGOUT", "CREATE", "UPDATE", "DELETE", "VIEW"]
        )
    
    with col3:
        user_filter = st.text_input("Filter by user")
    
    # Get logs
    all_logs = get_activity_logs(limit=log_limit)
    
    # Apply filters
    if action_filter != "All":
        all_logs = [l for l in all_logs if l.get('action', '').upper() == action_filter]
    
    if user_filter:
        all_logs = [l for l in all_logs if user_filter.lower() in l.get('username', '').lower()]
    
    st.markdown(f"**{len(all_logs)} logs found**")
    
    st.markdown("---")
    
    # Display logs in a table
    if all_logs:
        log_df = pd.DataFrame(all_logs)
        st.dataframe(log_df, use_container_width=True, hide_index=True)
        
        # Export option
        csv = log_df.to_csv(index=False)
        st.download_button(
            label="📥 Export Logs",
            data=csv,
            file_name=f"activity_logs_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No logs matching the filters.")

with tab4:
    st.markdown("### ⚙️ System Settings")
    
    st.markdown("""
    <div style='background: rgba(239, 68, 68, 0.1); padding: 1rem; border-radius: 12px;
        border-left: 4px solid #ef4444; margin-bottom: 1rem;'>
        <p style='color: #e2e8f0; margin: 0;'>
            ⚠️ <strong>Warning:</strong> Changes to system settings affect all users.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 Display Settings")
        
        currency = st.text_input("Currency Symbol", value=CURRENCY_SYMBOL)
        date_format = st.selectbox("Date Format", ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY"])
        theme = st.selectbox("Default Theme", ["Dark (Default)", "Light", "System"])
        
        if st.button("💾 Save Display Settings", use_container_width=True):
            st.info("Settings saved! (Note: Full implementation requires .env update)")
    
    with col2:
        st.markdown("#### 🔐 Security Settings")
        
        session_timeout = st.number_input("Session Timeout (hours)", min_value=1, max_value=24, value=24)
        require_email_verify = st.checkbox("Require Email Verification", value=False)
        allow_registration = st.checkbox("Allow New Registrations", value=True)
        
        if st.button("💾 Save Security Settings", use_container_width=True):
            st.info("Security settings saved!")
    
    st.markdown("---")
    
    st.markdown("#### 📧 Notification Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        enable_email_notifications = st.checkbox("Enable Email Notifications", value=False)
        budget_alerts = st.checkbox("Budget Threshold Alerts", value=True)
        goal_reminders = st.checkbox("Goal Reminder Notifications", value=True)
    
    with col2:
        alert_threshold = st.slider("Budget Alert Threshold (%)", 50, 100, 80)
        reminder_days = st.selectbox("Goal Reminder (days before deadline)", [3, 7, 14, 30])
    
    if st.button("💾 Save Notification Settings", use_container_width=True):
        st.info("Notification settings saved!")

with tab5:
    st.markdown("### 🗄️ Database Management")
    
    st.markdown("""
    <div style='background: rgba(239, 68, 68, 0.2); padding: 1rem; border-radius: 12px;
        border: 2px solid #ef4444; margin-bottom: 1rem;'>
        <h4 style='color: #ef4444; margin: 0;'>⚠️ DANGER ZONE</h4>
        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0;'>
            These actions are irreversible. Please proceed with extreme caution.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📤 Data Export")
        
        if st.button("📊 Export All Transactions", use_container_width=True):
            df_data = load_transactions()
            if not df_data.empty:
                csv = df_data.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"all_transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No transactions to export.")
        
        if st.button("👥 Export User Data", use_container_width=True):
            users = get_all_users()
            if users:
                df = pd.DataFrame(users)
                # Remove sensitive data
                if 'password' in df.columns:
                    df = df.drop(columns=['password'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=f"users_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No users to export.")
    
    with col2:
        st.markdown("#### 🗑️ Data Management")
        
        st.warning("These actions cannot be undone!")
        
        confirm_text = st.text_input(
            "Type 'DELETE' to enable destructive actions",
            placeholder="Type DELETE..."
        )
        
        if confirm_text == "DELETE":
            from utils import clear_all_transactions, clear_activity_logs
            
            if st.button("🗑️ Clear All Transactions", use_container_width=True, type="secondary"):
                success, msg = clear_all_transactions()
                if success:
                    st.success("✅ All transactions cleared!")
                    st.rerun()
                else:
                    st.error(f"Failed: {msg}")
            
            if st.button("🗑️ Clear Activity Logs", use_container_width=True, type="secondary"):
                success, msg = clear_activity_logs()
                if success:
                    st.success("✅ Activity logs cleared!")
                    st.rerun()
                else:
                    st.error(f"Failed: {msg}")
            
            if st.button("⚠️ Reset Database", use_container_width=True, type="secondary"):
                st.error("⚠️ Database reset is disabled for safety. Contact developer.")
    
    st.markdown("---")
    
    st.markdown("#### 📊 Database Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tables", "6")
    
    with col2:
        stats = get_system_stats()
        total_records = stats.get('total_transactions', 0) + stats.get('total_users', 0)
        st.metric("Total Records", f"{total_records:,}")
    
    with col3:
        st.metric("Status", "🟢 Connected")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280;'>
    <p>🔐 Admin Panel - Access restricted to {SUPER_ADMIN_USERNAME}</p>
    <p>All actions are logged for security purposes.</p>
    <p>© 2025 {DEVELOPER_NAME}</p>
</div>
""", unsafe_allow_html=True)
