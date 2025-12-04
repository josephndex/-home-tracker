"""
HomeTracker - Smart Home Management System
Main Application Entry Point
A comprehensive home management application with focus on kitchen management
"""
import streamlit as st
from datetime import datetime, timedelta
from config import APP_TITLE, APP_ICON, PAGE_LAYOUT, DEVELOPER_NAME, THEME_COLORS

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded"
)

# Import auth after page config
from auth import check_authentication, get_current_user, logout, get_auth_manager, log_page_visit, is_admin, is_super_admin

# Get current user
current_user = get_current_user()
auth_manager = get_auth_manager()

# Custom CSS for STUNNING dark theme - TEAL/CYAN/ROSE
st.markdown("""
<style>
    /* ============================================== */
    /* 🌟 STUNNING TEAL/CYAN/ROSE PREMIUM THEME 🌟    */
    /* ============================================== */
    
    /* Animated background with gradient */
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #042f2e, #0f172a, #1c1917);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Glowing particles overlay effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(20, 184, 166, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(244, 63, 94, 0.04) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(6, 182, 212, 0.03) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    /* METRIC CARDS - Glassmorphism effect */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(4, 47, 46, 0.8) 100%);
        border: 1px solid rgba(20, 184, 166, 0.3);
        border-radius: 20px;
        padding: 1.5rem !important;
        box-shadow: 
            0 10px 40px rgba(0, 0, 0, 0.5),
            0 0 30px rgba(20, 184, 166, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #14b8a6, #06b6d4, #f43f5e);
        animation: borderGlow 3s ease-in-out infinite;
    }
    
    @keyframes borderGlow {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: rgba(6, 182, 212, 0.5);
        box-shadow: 
            0 25px 60px rgba(20, 184, 166, 0.25),
            0 15px 40px rgba(244, 63, 94, 0.15),
            0 0 50px rgba(6, 182, 212, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stMetric"] label {
        color: #67e8f9 !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-size: 0.8rem !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 2rem !important;
        text-shadow: 0 0 30px rgba(20, 184, 166, 0.4);
    }
    
    /* Fix text visibility */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, 
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #f1f5f9 !important;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    /* Main title with gradient text */
    .stMarkdown h1 {
        background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 40%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* General text */
    .stMarkdown > div > p {
        color: #e2e8f0 !important;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 50%, #f43f5e 100%);
        padding: 2.5rem;
        border-radius: 24px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 
            0 20px 50px rgba(20, 184, 166, 0.3),
            0 10px 30px rgba(244, 63, 94, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            45deg,
            transparent 30%,
            rgba(255, 255, 255, 0.15) 50%,
            transparent 70%
        );
        animation: headerShine 3s ease-in-out infinite;
    }
    
    @keyframes headerShine {
        0% { transform: translateX(-100%) rotate(45deg); }
        100% { transform: translateX(100%) rotate(45deg); }
    }
    
    .main-header h1, .main-header p {
        color: white !important;
        position: relative;
        z-index: 1;
    }
    
    /* STUNNING TABS */
    .stTabs [data-baseweb="tab-list"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(4, 47, 46, 0.7) 100%);
        border-radius: 20px;
        padding: 0.5rem;
        gap: 0.5rem;
        border: 1px solid rgba(20, 184, 166, 0.25);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #67e8f9 !important;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 14px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.15) 0%, rgba(244, 63, 94, 0.1) 100%);
        color: #14b8a6 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 60%, #f43f5e 100%) !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(20, 184, 166, 0.4);
    }
    
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    
    /* SIDEBAR STYLING */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #042f2e 0%, #0f172a 50%, #1c1917 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] nav a {
        display: block;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0.5rem;
        border-radius: 14px;
        text-decoration: none;
        color: #5eead4 !important;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: transparent;
        border: 1px solid transparent;
    }
    
    section[data-testid="stSidebar"] nav a:hover {
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.15) 0%, rgba(244, 63, 94, 0.1) 100%) !important;
        border-color: rgba(20, 184, 166, 0.3);
        color: #14b8a6 !important;
        transform: translateX(5px);
    }
    
    section[data-testid="stSidebar"] nav a[aria-current="page"] {
        background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 60%, #f43f5e 100%) !important;
        color: white !important;
        font-weight: 700;
        box-shadow: 0 8px 25px rgba(20, 184, 166, 0.4);
    }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #14b8a6 0%, #06b6d4 60%, #f43f5e 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 14px;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 8px 25px rgba(20, 184, 166, 0.35),
            0 4px 15px rgba(244, 63, 94, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 
            0 15px 40px rgba(20, 184, 166, 0.4),
            0 8px 25px rgba(244, 63, 94, 0.3);
    }
    
    /* INPUT FIELDS */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea textarea {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(4, 47, 46, 0.8) 100%) !important;
        border: 2px solid rgba(20, 184, 166, 0.25) !important;
        border-radius: 14px !important;
        color: #f1f5f9 !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #14b8a6 !important;
        box-shadow: 0 0 0 3px rgba(20, 184, 166, 0.25) !important;
    }
    
    /* SELECT BOXES */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(4, 47, 46, 0.8) 100%) !important;
        border: 2px solid rgba(20, 184, 166, 0.25) !important;
        border-radius: 14px !important;
    }
    
    /* DATA FRAMES */
    [data-testid="stDataFrame"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(4, 47, 46, 0.7) 100%);
        border-radius: 20px;
        border: 1px solid rgba(20, 184, 166, 0.25);
        overflow: hidden;
    }
    
    /* ALERTS */
    .stSuccess {
        background: linear-gradient(135deg, rgba(20, 184, 166, 0.15) 0%, rgba(5, 150, 105, 0.1) 100%) !important;
        border-left: 4px solid #14b8a6 !important;
        border-radius: 14px !important;
    }
    
    .stError {
        background: linear-gradient(135deg, rgba(244, 63, 94, 0.15) 0%, rgba(225, 29, 72, 0.1) 100%) !important;
        border-left: 4px solid #f43f5e !important;
        border-radius: 14px !important;
    }
    
    .stWarning {
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.15) 0%, rgba(245, 158, 11, 0.1) 100%) !important;
        border-left: 4px solid #fbbf24 !important;
        border-radius: 14px !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.15) 0%, rgba(8, 145, 178, 0.1) 100%) !important;
        border-left: 4px solid #06b6d4 !important;
        border-radius: 14px !important;
    }
    
    /* EXPANDER */
    [data-testid="stExpander"] {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(4, 47, 46, 0.7) 100%);
        border: 1px solid rgba(20, 184, 166, 0.25);
        border-radius: 20px;
        overflow: hidden;
    }
    
    /* SCROLLBAR */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f172a;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #14b8a6 0%, #f43f5e 100%);
        border-radius: 5px;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2.5rem;
        color: #64748b;
        border-top: 2px solid transparent;
        border-image: linear-gradient(90deg, transparent, #14b8a6, #06b6d4, #f43f5e, transparent) 1;
        margin-top: 3rem;
    }
    
    /* ADDITIONAL FLAIR - Floating orbs effect */
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-20px) rotate(180deg); }
    }
    
    /* Progress bars with glow */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #14b8a6, #06b6d4, #f43f5e) !important;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(20, 184, 166, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Create navigation pages based on authentication
login_page = st.Page("pages/0_Login.py", title="Login")
home_page = st.Page("pages/1_Home.py", title="🏠 Home", default=True)
add_expense_page = st.Page("pages/2_Add_Transaction.py", title="➕ Add Transaction")
budget_page = st.Page("pages/3_Budget.py", title="💰 Budget")
report_page = st.Page("pages/4_Reports.py", title="📊 Reports")
kitchen_page = st.Page("pages/5_Kitchen.py", title="🍳 Kitchen")
statistics_page = st.Page("pages/6_Statistics.py", title="📈 Statistics")
goals_page = st.Page("pages/7_Goals.py", title="🎯 Goals")
categories_page = st.Page("pages/8_Categories.py", title="📂 Categories")
admin_page = st.Page("pages/9_Admin.py", title="🔐 Admin")
settings_page = st.Page("pages/10_Settings.py", title="⚙️ Settings")
about_page = st.Page("pages/11_About.py", title="ℹ️ About")

# Create navigation based on authentication status
if check_authentication():
    user = get_current_user()
    
    # Build page list - base pages for all users
    pages = [
        home_page,
        add_expense_page,
        budget_page,
        report_page,
        kitchen_page,
        statistics_page,
        goals_page,
        categories_page,
        settings_page,
        about_page
    ]
    
    # Admin page is HIDDEN - only visible to super admin (NDERITU)
    if is_super_admin(user):
        pages.append(admin_page)
    
    pg = st.navigation(pages=pages)
else:
    pg = st.navigation(pages=[login_page])

# Sidebar configuration - only show if authenticated
if check_authentication():
    with st.sidebar:
        # User info section
        if current_user:
            st.markdown(f"""
            <div style='text-align: center; padding: 0.5rem; background: linear-gradient(135deg, rgba(20, 184, 166, 0.15) 0%, rgba(244, 63, 94, 0.1) 100%); 
                        border-radius: 12px; margin-bottom: 1rem; border: 1px solid rgba(20, 184, 166, 0.3);'>
                <p style='margin: 0; font-size: 0.85rem; color: #67e8f9;'>Logged in as</p>
                <p style='margin: 0; font-weight: 600; color: #e2e8f0;'>{current_user.get('full_name', current_user.get('username', 'User'))}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center; padding: 1rem;'>
            <h2 style='color: #14b8a6; margin-bottom: 0.5rem;'>🏠 HomeTracker</h2>
            <p style='color: #64748b; font-size: 0.9rem;'>Smart Home Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick Stats
        try:
            from utils import load_transactions, get_total_balance, format_currency
            df = load_transactions()
            if not df.empty:
                balance = get_total_balance(df)
                st.metric("💰 Current Balance", format_currency(balance))
        except:
            pass
        
        # Quick actions
        st.markdown("### Quick Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add", use_container_width=True, type="secondary"):
                try:
                    st.switch_page("pages/2_Add_Transaction.py")
                except:
                    pass
        with col2:
            if st.button("📊 Reports", use_container_width=True, type="secondary"):
                try:
                    st.switch_page("pages/4_Reports.py")
                except:
                    pass
        
        st.markdown("---")
        
        # Kitchen alerts
        try:
            from utils import get_low_stock_items, get_expiring_items
            low_stock = get_low_stock_items()
            expiring = get_expiring_items(days=3)
            
            if not low_stock.empty:
                st.warning(f"🔔 {len(low_stock)} items low in stock")
            if not expiring.empty:
                st.warning(f"⏰ {len(expiring)} items expiring soon")
        except:
            pass
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.caption(f"© 2025 {DEVELOPER_NAME}")
        st.caption("All rights reserved")

# Run the selected page
pg.run()
