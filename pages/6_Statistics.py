"""
Statistics Page - Advanced financial statistics and insights
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import sys
sys.path.insert(0, '..')

from config import DEVELOPER_NAME, CURRENCY_SYMBOL
from auth import require_authentication, get_current_user, log_page_visit
from utils import load_transactions, format_currency

# Require authentication
require_authentication()
log_page_visit("6_Statistics.py")

user = get_current_user()
user_id = user.get('id') if user else None

st.title("📊 Financial Statistics")

st.markdown("""
<div style='background: linear-gradient(135deg, rgba(20, 184, 166, 0.1) 0%, rgba(244, 63, 94, 0.1) 100%);
    padding: 1rem; border-radius: 12px; border-left: 4px solid #f43f5e; margin-bottom: 1rem;'>
    <p style='color: #e2e8f0; margin: 0;'>
        Deep dive into your financial data with advanced statistics and visualizations.
    </p>
</div>
""", unsafe_allow_html=True)

# Load data
df_data = load_transactions()

if not df_data.empty and len(df_data) > 0:
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Distribution", "🔄 Patterns", "📉 Correlations"])
    
    with tab1:
        st.markdown("### 📈 Statistical Overview")
        
        # Basic statistics
        expenses = df_data[df_data["Type"] == "Expense"]["Amount"]
        income = df_data[df_data["Type"] == "Income"]["Amount"]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 💸 Expense Statistics")
            
            if len(expenses) > 0:
                stats_data = {
                    "Metric": ["Count", "Total", "Mean", "Median", "Std Dev", "Min", "Max"],
                    "Value": [
                        f"{len(expenses):,}",
                        format_currency(expenses.sum()),
                        format_currency(expenses.mean()),
                        format_currency(expenses.median()),
                        format_currency(expenses.std()),
                        format_currency(expenses.min()),
                        format_currency(expenses.max())
                    ]
                }
                st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
            else:
                st.info("No expense data available.")
        
        with col2:
            st.markdown("#### 💰 Income Statistics")
            
            if len(income) > 0:
                stats_data = {
                    "Metric": ["Count", "Total", "Mean", "Median", "Std Dev", "Min", "Max"],
                    "Value": [
                        f"{len(income):,}",
                        format_currency(income.sum()),
                        format_currency(income.mean()),
                        format_currency(income.median()),
                        format_currency(income.std()),
                        format_currency(income.min()),
                        format_currency(income.max())
                    ]
                }
                st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
            else:
                st.info("No income data available.")
        
        st.markdown("---")
        
        # Percentiles
        st.markdown("### 📊 Expense Percentiles")
        
        if len(expenses) > 0:
            percentiles = [10, 25, 50, 75, 90, 95, 99]
            percentile_values = [np.percentile(expenses, p) for p in percentiles]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=[f"{p}th" for p in percentiles],
                y=percentile_values,
                marker_color=px.colors.sequential.Oranges[:len(percentiles)],
                text=[format_currency(v) for v in percentile_values],
                textposition='outside'
            ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title="Percentile",
                yaxis_title=f"Amount ({CURRENCY_SYMBOL})",
                margin=dict(t=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights
            st.markdown(f"""
            <div style='background: rgba(244, 63, 94, 0.1); padding: 1rem; border-radius: 12px;
                border-left: 4px solid #f43f5e;'>
                <h4 style='color: #f43f5e; margin-bottom: 0.5rem;'>💡 Percentile Insights</h4>
                <ul style='color: #e2e8f0; margin: 0;'>
                    <li>50% of your expenses are below <strong>{format_currency(np.percentile(expenses, 50))}</strong></li>
                    <li>75% of your expenses are below <strong>{format_currency(np.percentile(expenses, 75))}</strong></li>
                    <li>Only 10% of expenses exceed <strong>{format_currency(np.percentile(expenses, 90))}</strong></li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📊 Distribution Analysis")
        
        if len(expenses) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Expense Distribution")
                
                fig = px.histogram(
                    expenses,
                    nbins=30,
                    color_discrete_sequence=['#14b8a6']
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title=f"Amount ({CURRENCY_SYMBOL})",
                    yaxis_title="Frequency",
                    showlegend=False
                )
                
                # Add mean and median lines
                fig.add_vline(x=expenses.mean(), line_dash="dash", line_color="#f43f5e",
                            annotation_text=f"Mean: {format_currency(expenses.mean())}")
                fig.add_vline(x=expenses.median(), line_dash="dot", line_color="#10b981",
                            annotation_text=f"Median: {format_currency(expenses.median())}")
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Box Plot")
                
                fig = px.box(
                    df_data,
                    x="Type",
                    y="Amount",
                    color="Type",
                    color_discrete_map={"Expense": "#ef4444", "Income": "#10b981"}
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Category distribution
            st.markdown("---")
            st.markdown("#### Category Distribution")
            
            expense_df = df_data[df_data["Type"] == "Expense"]
            
            fig = px.box(
                expense_df,
                x="Category",
                y="Amount",
                color="Category",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_tickangle=-45,
                showlegend=False,
                margin=dict(b=100)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data for distribution analysis.")
    
    with tab3:
        st.markdown("### 🔄 Spending Patterns")
        
        expense_df = df_data[df_data["Type"] == "Expense"].copy()
        
        if not expense_df.empty:
            # Add time features
            expense_df["DayOfWeek"] = expense_df["Date"].dt.dayofweek
            expense_df["DayName"] = expense_df["Date"].dt.day_name()
            expense_df["Week"] = expense_df["Date"].dt.isocalendar().week
            expense_df["Month"] = expense_df["Date"].dt.month
            expense_df["MonthName"] = expense_df["Date"].dt.month_name()
            expense_df["Year"] = expense_df["Date"].dt.year
            expense_df["Quarter"] = expense_df["Date"].dt.quarter
            expense_df["DayOfMonth"] = expense_df["Date"].dt.day
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### By Day of Week")
                
                day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                day_spending = expense_df.groupby("DayName")["Amount"].mean().reindex(day_order)
                
                fig = px.bar(
                    x=day_spending.index,
                    y=day_spending.values,
                    color=day_spending.values,
                    color_continuous_scale="Oranges"
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title="",
                    yaxis_title=f"Avg Spending ({CURRENCY_SYMBOL})",
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### By Month")
                
                month_order = ["January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"]
                month_spending = expense_df.groupby("MonthName")["Amount"].sum()
                month_spending = month_spending.reindex([m for m in month_order if m in month_spending.index])
                
                fig = px.bar(
                    x=month_spending.index,
                    y=month_spending.values,
                    color=month_spending.values,
                    color_continuous_scale="Purples"
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_title="",
                    yaxis_title=f"Total Spending ({CURRENCY_SYMBOL})",
                    xaxis_tickangle=-45,
                    coloraxis_showscale=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Day of month pattern
            st.markdown("---")
            st.markdown("#### Spending by Day of Month")
            
            day_of_month_spending = expense_df.groupby("DayOfMonth")["Amount"].mean()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=day_of_month_spending.index,
                y=day_of_month_spending.values,
                mode='lines+markers',
                fill='tozeroy',
                line_color='#14b8a6',
                fillcolor='rgba(20, 184, 166, 0.2)'
            ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0'),
                xaxis_title="Day of Month",
                yaxis_title=f"Avg Spending ({CURRENCY_SYMBOL})"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Heatmap - Day vs Week
            st.markdown("---")
            st.markdown("#### Spending Heatmap (Week vs Day)")
            
            heatmap_data = expense_df.pivot_table(
                values='Amount',
                index='DayOfWeek',
                columns='Week',
                aggfunc='sum',
                fill_value=0
            )
            
            day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            
            fig = px.imshow(
                heatmap_data.values,
                labels=dict(x="Week", y="Day", color="Spending"),
                y=day_labels[:len(heatmap_data)],
                color_continuous_scale="Oranges"
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e2e8f0')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data for pattern analysis.")
    
    with tab4:
        st.markdown("### 📉 Category Correlations")
        
        expense_df = df_data[df_data["Type"] == "Expense"].copy()
        
        if not expense_df.empty:
            # Category correlation over time
            expense_df["Month"] = expense_df["Date"].dt.to_period("M").astype(str)
            
            monthly_category = expense_df.pivot_table(
                values='Amount',
                index='Month',
                columns='Category',
                aggfunc='sum',
                fill_value=0
            )
            
            if len(monthly_category.columns) > 1 and len(monthly_category) > 2:
                correlation_matrix = monthly_category.corr()
                
                st.markdown("#### Category Spending Correlation")
                
                fig = px.imshow(
                    correlation_matrix,
                    text_auto='.2f',
                    color_continuous_scale='RdBu_r',
                    aspect='auto'
                )
                
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#e2e8f0'),
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Interpretation
                st.markdown("""
                <div style='background: rgba(20, 184, 166, 0.1); padding: 1rem; border-radius: 12px;
                    border-left: 4px solid #14b8a6; margin-top: 1rem;'>
                    <h4 style='color: #14b8a6; margin-bottom: 0.5rem;'>📖 How to Read This</h4>
                    <ul style='color: #e2e8f0; margin: 0;'>
                        <li><strong>+1.0</strong>: Categories that increase together</li>
                        <li><strong>0</strong>: No relationship</li>
                        <li><strong>-1.0</strong>: When one increases, the other decreases</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Find strongest correlations
                st.markdown("---")
                st.markdown("#### 🔗 Strongest Correlations")
                
                # Get upper triangle of correlation matrix
                upper_tri = correlation_matrix.where(
                    np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
                )
                
                # Stack and sort
                correlations = upper_tri.stack().sort_values(ascending=False)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🔺 Strongest Positive**")
                    for (cat1, cat2), corr in correlations.head(5).items():
                        st.markdown(f"- {cat1} ↔ {cat2}: `{corr:.2f}`")
                
                with col2:
                    st.markdown("**🔻 Strongest Negative**")
                    for (cat1, cat2), corr in correlations.tail(5).items():
                        st.markdown(f"- {cat1} ↔ {cat2}: `{corr:.2f}`")
            else:
                st.info("Not enough data for correlation analysis. Need more categories and months of data.")
        else:
            st.info("No expense data for correlation analysis.")
else:
    st.info("No transaction data available. Start adding transactions to see statistics!")

# Footer
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #6b7280;'>
    <p>📊 Statistics help you understand your financial behavior better.</p>
    <p>© 2025 {DEVELOPER_NAME}</p>
</div>
""", unsafe_allow_html=True)
