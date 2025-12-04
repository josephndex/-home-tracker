"""
Financial Goals Page - Set and track your financial goals
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, CURRENCY_SYMBOL
from auth import require_authentication, get_current_user, log_page_visit
from utils import (
    load_transactions, format_currency, 
    load_goals, add_goal, update_goal_progress, delete_goal
)

# Require authentication
require_authentication()
log_page_visit("7_Goals.py")

user = get_current_user()
user_id = user.get('id') if user else None

st.title("🎯 Financial Goals")

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
    padding: 1rem; border-radius: 12px; border-left: 4px solid #14b8a6; margin-bottom: 1rem;'>
    <p style='color: #e2e8f0; margin: 0;'>
        Set financial goals and track your progress towards achieving them.
    </p>
</div>
""", unsafe_allow_html=True)

# Load data
df_data = load_transactions()
goals_df = load_goals(user_id)

# Convert DataFrame to list of dicts for easier handling
goals = goals_df.to_dict('records') if not goals_df.empty else []

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 My Goals", "➕ Add Goal", "📈 Progress"])

with tab1:
    st.markdown("### 🎯 Active Goals")
    
    if len(goals) > 0:
        for goal in goals:
            goal_id = goal.get('id', 0)
            goal_name = goal.get('goal_name', goal.get('name', 'Unnamed Goal'))
            target_amount = float(goal.get('target_amount', 0) or 0)
            current_amount = float(goal.get('current_amount', 0) or 0)
            deadline = goal.get('deadline')
            priority = goal.get('priority', 'medium')
            status = goal.get('status', 'active')
            notes = goal.get('notes', '')
            
            progress = (current_amount / target_amount * 100) if target_amount > 0 else 0
            remaining = target_amount - current_amount
            
            # Calculate days remaining
            days_remaining = None
            deadline_str = "No deadline"
            if deadline:
                try:
                    if isinstance(deadline, str):
                        deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
                    else:
                        deadline_date = deadline
                    days_remaining = (deadline_date - datetime.now()).days
                    deadline_str = deadline_date.strftime("%b %d, %Y")
                except:
                    deadline_str = str(deadline)
            
            # Determine status color based on progress
            if progress >= 100:
                status_color = "#14b8a6"
                status_emoji = "✅"
                status_text = "Completed"
            elif progress >= 75:
                status_color = "#14b8a6"
                status_emoji = "🔥"
                status_text = "Almost There!"
            elif progress >= 50:
                status_color = "#06b6d4"
                status_emoji = "📈"
                status_text = "Halfway"
            elif progress >= 25:
                status_color = "#f43f5e"
                status_emoji = "🚀"
                status_text = "In Progress"
            else:
                status_color = "#64748b"
                status_emoji = "🎯"
                status_text = "Just Started"
            
            # Priority badge color
            priority_colors = {
                'low': '#64748b',
                'medium': '#06b6d4', 
                'high': '#f43f5e',
                'critical': '#ef4444'
            }
            priority_color = priority_colors.get(str(priority).lower(), '#64748b')
            
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
                padding: 1.5rem; border-radius: 16px; margin-bottom: 1rem;
                border: 1px solid rgba(20, 184, 166, 0.2);'>
                <div style='display: flex; justify-content: space-between; align-items: start;'>
                    <div>
                        <h3 style='color: #14b8a6; margin: 0;'>{status_emoji} {goal_name}</h3>
                        <p style='color: #67e8f9; margin: 0.3rem 0; font-size: 0.9rem;'>📅 {deadline_str}</p>
                    </div>
                    <div style='text-align: right;'>
                        <span style='background: {status_color}; padding: 0.3rem 0.8rem; 
                            border-radius: 20px; color: white; font-size: 0.8rem;'>{status_text}</span>
                        <br>
                        <span style='background: {priority_color}; padding: 0.2rem 0.6rem; 
                            border-radius: 20px; color: white; font-size: 0.7rem; margin-top: 0.3rem; display: inline-block;'>
                            {str(priority).title()} Priority
                        </span>
                    </div>
                </div>
                <div style='margin-top: 1rem;'>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <span style='color: #e2e8f0;'>Progress</span>
                        <span style='color: #14b8a6; font-weight: bold;'>{progress:.1f}%</span>
                    </div>
                    <div style='background: rgba(255,255,255,0.1); border-radius: 10px; height: 12px; overflow: hidden;'>
                        <div style='background: linear-gradient(90deg, #14b8a6, #06b6d4, #f43f5e); 
                            width: {min(progress, 100)}%; height: 100%; border-radius: 10px;
                            box-shadow: 0 0 15px rgba(20, 184, 166, 0.5);'></div>
                    </div>
                </div>
                <div style='display: flex; justify-content: space-between; margin-top: 1rem;'>
                    <div>
                        <p style='color: #64748b; margin: 0; font-size: 0.85rem;'>Current</p>
                        <p style='color: #14b8a6; margin: 0; font-weight: bold;'>{format_currency(current_amount)}</p>
                    </div>
                    <div style='text-align: center;'>
                        <p style='color: #64748b; margin: 0; font-size: 0.85rem;'>Target</p>
                        <p style='color: #06b6d4; margin: 0; font-weight: bold;'>{format_currency(target_amount)}</p>
                    </div>
                    <div style='text-align: right;'>
                        <p style='color: #64748b; margin: 0; font-size: 0.85rem;'>Remaining</p>
                        <p style='color: #f43f5e; margin: 0; font-weight: bold;'>{format_currency(remaining)}</p>
                    </div>
                </div>
                {f"<p style='color: #94a3b8; margin-top: 0.75rem; font-size: 0.85rem; font-style: italic;'>📝 {notes}</p>" if notes else ""}
            </div>
            """, unsafe_allow_html=True)
            
            # Actions
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                add_amount = st.number_input(
                    "Add savings",
                    min_value=0.0,
                    step=100.0,
                    key=f"add_{goal_id}",
                    label_visibility="collapsed",
                    placeholder="Amount to add..."
                )
            
            with col2:
                if st.button("💰 Add Funds", key=f"add_btn_{goal_id}", type="primary"):
                    if add_amount > 0:
                        new_amount = current_amount + add_amount
                        success, msg = update_goal_progress(goal_id, new_amount)
                        if success:
                            st.success(f"Added {format_currency(add_amount)} to goal!")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Enter an amount to add")
            
            with col3:
                if st.button("🗑️ Delete", key=f"del_{goal_id}", type="secondary"):
                    success, msg = delete_goal(goal_id, user_id)
                    if success:
                        st.success("Goal deleted!")
                        st.rerun()
                    else:
                        st.error(msg)
            
            st.markdown("---")
    else:
        st.info("🎯 No goals set yet. Create your first financial goal in the 'Add Goal' tab!")
        
        # Suggested goals
        st.markdown("### 💡 Suggested Goals")
        
        suggestions = [
            {"name": "Emergency Fund", "target": 50000, "desc": "3-6 months of expenses"},
            {"name": "Kitchen Upgrade", "target": 30000, "desc": "New appliances or renovation"},
            {"name": "Vacation Fund", "target": 25000, "desc": "For your next holiday"},
            {"name": "Monthly Savings", "target": 10000, "desc": "Build savings habit"},
        ]
        
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 2]:
                st.markdown(f"""
                <div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.05) 0%, rgba(244, 63, 94, 0.05) 100%); 
                    padding: 1rem; border-radius: 12px; margin-bottom: 0.5rem;
                    border: 1px solid rgba(20, 184, 166, 0.2);'>
                    <h4 style='color: #14b8a6; margin: 0;'>🎯 {suggestion['name']}</h4>
                    <p style='color: #67e8f9; margin: 0.3rem 0;'>Target: {format_currency(suggestion['target'])}</p>
                    <p style='color: #64748b; margin: 0; font-size: 0.85rem;'>{suggestion['desc']}</p>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.markdown("### ➕ Create New Goal")
    
    with st.form("new_goal_form"):
        goal_name = st.text_input("Goal Name", placeholder="e.g., Emergency Fund, New Appliance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            target_amount = st.number_input(
                f"Target Amount ({CURRENCY_SYMBOL})",
                min_value=0.0,
                step=1000.0,
                value=10000.0
            )
        
        with col2:
            initial_amount = st.number_input(
                f"Initial Savings ({CURRENCY_SYMBOL})",
                min_value=0.0,
                step=100.0,
                value=0.0
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            deadline = st.date_input(
                "Target Date",
                value=datetime.now() + timedelta(days=90)
            )
        
        with col2:
            priority = st.selectbox(
                "Priority",
                options=["low", "medium", "high", "critical"],
                index=1
            )
        
        notes = st.text_area("Notes (Optional)", placeholder="Describe your goal...")
        
        # Calculate monthly contribution needed
        days_to_deadline = max((deadline - datetime.now().date()).days, 1)
        months_to_deadline = days_to_deadline / 30
        amount_needed = target_amount - initial_amount
        monthly_contribution = amount_needed / max(months_to_deadline, 1) if amount_needed > 0 else 0
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(20, 184, 166, 0.1) 100%);
            padding: 1rem; border-radius: 12px; margin: 1rem 0;'>
            <p style='color: #67e8f9; margin: 0; font-size: 0.9rem;'>
                💡 Monthly contribution needed: <strong style='color: #14b8a6;'>{format_currency(monthly_contribution)}</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🎯 Create Goal", use_container_width=True, type="primary")
        
        if submitted:
            if goal_name and target_amount > 0:
                success, msg = add_goal(
                    goal_name=goal_name,
                    target_amount=target_amount,
                    deadline=deadline.strftime("%Y-%m-%d"),
                    priority=priority,
                    notes=notes,
                    user_id=user_id
                )
                
                if success:
                    # If there's initial amount, update progress
                    if initial_amount > 0:
                        # Get latest goal ID and update
                        updated_goals = load_goals(user_id)
                        if not updated_goals.empty:
                            latest_goal_id = updated_goals.iloc[-1]['id']
                            update_goal_progress(latest_goal_id, initial_amount)
                    
                    st.success("🎉 Goal created successfully!")
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.error("Please provide a goal name and target amount.")

with tab3:
    st.markdown("### 📈 Goal Progress Overview")
    
    if len(goals) > 0:
        # Summary metrics
        total_goals = len(goals)
        completed_goals = len([g for g in goals if float(g.get('current_amount', 0) or 0) >= float(g.get('target_amount', 1) or 1)])
        active_goals = total_goals - completed_goals
        
        total_target = sum(float(g.get('target_amount', 0) or 0) for g in goals)
        total_saved = sum(float(g.get('current_amount', 0) or 0) for g in goals)
        overall_progress = (total_saved / total_target * 100) if total_target > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎯 Total Goals", total_goals)
        
        with col2:
            st.metric("✅ Completed", completed_goals)
        
        with col3:
            st.metric("🔥 Active", active_goals)
        
        with col4:
            st.metric("📈 Overall Progress", f"{overall_progress:.1f}%")
        
        st.markdown("---")
        
        # Progress chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Goal Progress Comparison")
            
            goal_names = [g.get('goal_name', g.get('name', 'Unnamed')) for g in goals]
            progress_values = [
                min((float(g.get('current_amount', 0) or 0) / float(g.get('target_amount', 1) or 1)) * 100, 100)
                for g in goals
            ]
            
            fig = px.bar(
                y=goal_names,
                x=progress_values,
                orientation='h',
                color=progress_values,
                color_continuous_scale=[[0, '#f43f5e'], [0.5, '#06b6d4'], [1, '#14b8a6']]
            )
            
            fig.add_vline(x=100, line_dash="dash", line_color="white",
                         annotation_text="Target")
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title="Progress %",
                yaxis_title="",
                coloraxis_showscale=False,
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Target vs Saved")
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Target',
                y=goal_names,
                x=[float(g.get('target_amount', 0) or 0) for g in goals],
                orientation='h',
                marker_color='#06b6d4'
            ))
            
            fig.add_trace(go.Bar(
                name='Saved',
                y=goal_names,
                x=[float(g.get('current_amount', 0) or 0) for g in goals],
                orientation='h',
                marker_color='#14b8a6'
            ))
            
            fig.update_layout(
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title=f"Amount ({CURRENCY_SYMBOL})",
                yaxis_title="",
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Savings summary
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💰 Savings Summary")
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(6, 182, 212, 0.1) 100%);
                padding: 1.5rem; border-radius: 16px; border: 1px solid rgba(20, 184, 166, 0.2);'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 1rem;'>
                    <span style='color: #94a3b8;'>Total Target</span>
                    <span style='color: #06b6d4; font-weight: bold;'>{format_currency(total_target)}</span>
                </div>
                <div style='display: flex; justify-content: space-between; margin-bottom: 1rem;'>
                    <span style='color: #94a3b8;'>Total Saved</span>
                    <span style='color: #14b8a6; font-weight: bold;'>{format_currency(total_saved)}</span>
                </div>
                <div style='display: flex; justify-content: space-between;'>
                    <span style='color: #94a3b8;'>Still Needed</span>
                    <span style='color: #f43f5e; font-weight: bold;'>{format_currency(total_target - total_saved)}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📅 Upcoming Deadlines")
            
            upcoming = []
            for goal in goals:
                deadline = goal.get('deadline')
                if deadline and float(goal.get('current_amount', 0) or 0) < float(goal.get('target_amount', 1) or 1):
                    try:
                        if isinstance(deadline, str):
                            deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
                        else:
                            deadline_date = deadline
                        days_left = (deadline_date - datetime.now()).days
                        upcoming.append({
                            'name': goal.get('goal_name', goal.get('name', 'Unnamed')),
                            'days_left': days_left,
                            'deadline': deadline_date.strftime("%b %d, %Y")
                        })
                    except:
                        pass
            
            upcoming.sort(key=lambda x: x['days_left'])
            
            if upcoming:
                for item in upcoming[:5]:
                    urgency_color = "#ef4444" if item['days_left'] < 30 else (
                        "#eab308" if item['days_left'] < 90 else "#14b8a6"
                    )
                    days_text = f"{item['days_left']} days" if item['days_left'] >= 0 else "Overdue!"
                    
                    st.markdown(f"""
                    <div style='background: rgba(255,255,255,0.03); padding: 0.8rem;
                        border-radius: 8px; margin-bottom: 0.5rem;
                        border-left: 3px solid {urgency_color};'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='color: #e2e8f0;'>{item['name']}</span>
                            <span style='color: {urgency_color}; font-weight: bold;'>{days_text}</span>
                        </div>
                        <span style='color: #64748b; font-size: 0.85rem;'>{item['deadline']}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No upcoming deadlines.")
    else:
        st.info("🎯 Create goals to see progress tracking!")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #64748b;'>
    <p>🎯 Setting goals is the first step to achieving them!</p>
    <p>© 2025 {DEVELOPER_NAME}</p>
</div>
""", unsafe_allow_html=True)
