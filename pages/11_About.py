"""
About Page - Information about the application
"""
import streamlit as st
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, APP_TITLE, APP_VERSION
from auth import log_page_visit

log_page_visit("11_About.py")

st.markdown("""
<style>
    .about-header {
        text-align: center;
        padding: 3rem 0;
    }
    .feature-card {
        background: rgba(255,255,255,0.05);
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        border: 1px solid rgba(244, 63, 94, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Hero section
st.markdown(f"""
<div style='text-align: center; padding: 3rem 0;'>
    <h1 style='background: linear-gradient(135deg, #14b8a6 0%, #f43f5e 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 3.5rem; margin-bottom: 0.5rem;'>
        🏠 {APP_TITLE}
    </h1>
    <p style='color: #a78bfa; font-size: 1.3rem; margin-bottom: 0.5rem;'>
        Smart Home Management System
    </p>
    <p style='color: #6b7280;'>Version {APP_VERSION}</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.15) 0%, rgba(244, 63, 94, 0.15) 100%);
    padding: 2rem; border-radius: 20px; text-align: center; margin-bottom: 2rem;
    border: 1px solid rgba(244, 63, 94, 0.3);'>
    <p style='color: #e2e8f0; font-size: 1.1rem; margin: 0; line-height: 1.8;'>
        HomeTracker is your all-in-one solution for managing household finances,
        with a special focus on kitchen and food expenses. Track spending, set budgets,
        achieve financial goals, and gain insights into your home management.
    </p>
</div>
""", unsafe_allow_html=True)

# Features
st.markdown("## ✨ Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class='feature-card'>
        <h3 style='color: #14b8a6; margin: 0;'>📊 Dashboard</h3>
        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0;'>
            Beautiful, real-time overview of your finances with interactive charts 
            and quick insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h3 style='color: #10b981; margin: 0;'>💰 Budget Management</h3>
        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0;'>
            Set monthly budgets for each category and track your progress with 
            visual indicators.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h3 style='color: #6366f1; margin: 0;'>🎯 Financial Goals</h3>
        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0;'>
            Set savings goals, track progress, and celebrate when you achieve 
            your financial milestones.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='feature-card'>
        <h3 style='color: #f43f5e; margin: 0;'>🍳 Kitchen Central</h3>
        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0;'>
            Dedicated kitchen management with grocery tracking, meal planning insights, 
            and smart shopping lists.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h3 style='color: #eab308; margin: 0;'>📈 Analytics</h3>
        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0;'>
            Deep dive into your spending patterns with advanced statistics, 
            trends, and correlations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='feature-card'>
        <h3 style='color: #ef4444; margin: 0;'>📊 Reports</h3>
        <p style='color: #e2e8f0; margin: 0.5rem 0 0 0;'>
            Generate comprehensive reports for any time period with export 
            functionality.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Kitchen Focus
st.markdown("## 🍳 Kitchen Focus")

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.2) 0%, rgba(234, 88, 12, 0.2) 100%);
    padding: 2rem; border-radius: 20px; margin-bottom: 2rem;
    border: 1px solid rgba(20, 184, 166, 0.3);'>
    <div style='text-align: center; margin-bottom: 1rem;'>
        <span style='font-size: 4rem;'>👨‍🍳</span>
    </div>
    <h3 style='color: #14b8a6; text-align: center; margin: 0 0 1rem 0;'>
        Why Kitchen Focus?
    </h3>
    <p style='color: #e2e8f0; text-align: center; margin: 0; line-height: 1.8;'>
        The kitchen is the heart of every home. Food and kitchen expenses often account for 
        the largest portion of household spending. HomeTracker provides specialized tools to 
        track groceries, meal ingredients, kitchen supplies, and utilities - helping you 
        manage your kitchen budget more effectively.
    </p>
</div>
""", unsafe_allow_html=True)

# Kitchen categories showcase
st.markdown("### 🥘 Kitchen Categories")

kitchen_items = [
    ("🥬", "Vegetables"), ("🍖", "Meat & Poultry"), ("🐟", "Fish & Seafood"),
    ("🥛", "Dairy & Eggs"), ("🍎", "Fruits"), ("🛒", "Groceries"),
    ("🥤", "Beverages"), ("🍪", "Snacks"), ("🫒", "Cooking Oil"),
    ("🧂", "Spices"), ("🧁", "Baking Supplies"), ("🧹", "Cleaning"),
    ("🍳", "Kitchen Supplies"), ("🔥", "Cooking Gas")
]

cols = st.columns(7)
for i, (emoji, name) in enumerate(kitchen_items):
    with cols[i % 7]:
        st.markdown(f"""
        <div style='text-align: center; padding: 0.5rem;'>
            <span style='font-size: 1.5rem;'>{emoji}</span>
            <p style='color: #6b7280; margin: 0; font-size: 0.7rem;'>{name}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Technology Stack
st.markdown("## 🛠️ Technology Stack")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 1.5rem;
        border-radius: 12px; text-align: center;'>
        <span style='font-size: 2.5rem;'>🐍</span>
        <h4 style='color: #e2e8f0; margin: 0.5rem 0;'>Python</h4>
        <p style='color: #6b7280; margin: 0; font-size: 0.9rem;'>Core Language</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 1.5rem;
        border-radius: 12px; text-align: center;'>
        <span style='font-size: 2.5rem;'>📊</span>
        <h4 style='color: #e2e8f0; margin: 0.5rem 0;'>Streamlit</h4>
        <p style='color: #6b7280; margin: 0; font-size: 0.9rem;'>Web Framework</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 1.5rem;
        border-radius: 12px; text-align: center;'>
        <span style='font-size: 2.5rem;'>🗄️</span>
        <h4 style='color: #e2e8f0; margin: 0.5rem 0;'>MySQL</h4>
        <p style='color: #6b7280; margin: 0; font-size: 0.9rem;'>Database</p>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 1.5rem;
        border-radius: 12px; text-align: center;'>
        <span style='font-size: 2.5rem;'>📈</span>
        <h4 style='color: #e2e8f0; margin: 0.5rem 0;'>Plotly</h4>
        <p style='color: #6b7280; margin: 0; font-size: 0.9rem;'>Visualizations</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 1.5rem;
        border-radius: 12px; text-align: center;'>
        <span style='font-size: 2.5rem;'>🐼</span>
        <h4 style='color: #e2e8f0; margin: 0.5rem 0;'>Pandas</h4>
        <p style='color: #6b7280; margin: 0; font-size: 0.9rem;'>Data Processing</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background: rgba(255,255,255,0.05); padding: 1.5rem;
        border-radius: 12px; text-align: center;'>
        <span style='font-size: 2.5rem;'>🔐</span>
        <h4 style='color: #e2e8f0; margin: 0.5rem 0;'>bcrypt</h4>
        <p style='color: #6b7280; margin: 0; font-size: 0.9rem;'>Security</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Developer Info
st.markdown("## 👨‍💻 Developer")

st.markdown(f"""
<div style='background: linear-gradient(135deg, rgba(244, 63, 94, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
    padding: 2rem; border-radius: 20px; text-align: center;
    border: 1px solid rgba(244, 63, 94, 0.3);'>
    <div style='background: linear-gradient(135deg, #f43f5e 0%, #6366f1 100%);
        width: 100px; height: 100px; border-radius: 50%; 
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 1rem;'>
        <span style='font-size: 2.5rem; color: white;'>👨‍💻</span>
    </div>
    <h2 style='color: #f43f5e; margin: 0;'>{DEVELOPER_NAME}</h2>
    <p style='color: #e2e8f0; margin: 0.5rem 0;'>Full Stack Developer</p>
    <p style='color: #6b7280; margin: 1rem 0 0 0;'>
        Passionate about creating beautiful, functional applications that make 
        everyday life easier.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Quick Links
st.markdown("## 🔗 Quick Links")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Dashboard", use_container_width=True):
        st.switch_page("pages/1_Home.py")

with col2:
    if st.button("🍳 Kitchen", use_container_width=True):
        st.switch_page("pages/5_Kitchen.py")

with col3:
    if st.button("💰 Budget", use_container_width=True):
        st.switch_page("pages/3_Budget.py")

with col4:
    if st.button("📊 Reports", use_container_width=True):
        st.switch_page("pages/4_Reports.py")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 2rem 0;'>
    <p style='color: #6b7280; margin: 0;'>
        Made with ❤️ by {DEVELOPER_NAME}
    </p>
    <p style='color: #6b7280; margin: 0.5rem 0 0 0;'>
        © 2025 {APP_TITLE}. All rights reserved.
    </p>
    <p style='color: #4b5563; margin: 0.5rem 0 0 0; font-size: 0.85rem;'>
        Version {APP_VERSION}
    </p>
</div>
""", unsafe_allow_html=True)
