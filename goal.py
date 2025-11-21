# goals.py
import streamlit as st

# st.title("🎯 Financial Goals")

# goal = st.text_input("Your Goal (e.g. Save for vacation)")
# target_amount = st.number_input("Target Amount", min_value=0.0, step=100.0)
# amount_saved = st.number_input("Amount Saved", min_value=0.0, step=100.0)

# if target_amount > 0:
#     progress = min(amount_saved / target_amount, 1.0)
#     st.progress(progress, text=f"{progress*100:.1f}% completed")

import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.title("🎯 Financial Goals")

# File path to store goals
GOALS_FILE = os.path.join("data", "financial_goals.csv")
os.makedirs("data", exist_ok=True)

# Load existing goals or create an empty DataFrame
def load_goals():
    if os.path.exists(GOALS_FILE):
        return pd.read_csv(GOALS_FILE, parse_dates=["Deadline"])
    else:
        return pd.DataFrame(columns=["Goal", "Target Amount", "Amount Saved", "Deadline"])

def save_goals(df):
    df.to_csv(GOALS_FILE, index=False)

goals_df = load_goals()


tab1, tab2 = st.tabs(["🎯 Add a New Goal"," 📋 Your Goals "])

with tab1: 
    st.subheader("➕ Add a New Goal")

    with st.form("goal_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        goal_name = col1.text_input("Goal Name", max_chars=50)
        target_amount = col2.number_input("Target Amount (KSH)", min_value=0.0, step=100.0)
        deadline = st.date_input("Deadline", value=datetime.today())
        amount_saved = st.number_input("Amount Saved (KSH)", min_value=0.0, step=100.0)

        submitted = st.form_submit_button("💾 Save Goal")

        if submitted:
            if not goal_name:
                st.warning("Please enter a goal name.")
            elif amount_saved > target_amount:
                st.warning("Amount saved cannot be more than target amount.")
            else:
                new_goal = pd.DataFrame([{
                    "Goal": goal_name,
                    "Target Amount": target_amount,
                    "Amount Saved": amount_saved,
                    "Deadline": pd.to_datetime(deadline)
                }])
                goals_df = pd.concat([goals_df, new_goal], ignore_index=True)
                save_goals(goals_df)
                st.success("✅ Goal saved successfully!")

with tab2: 
# ----------- GOALS OVERVIEW -----------
    st.subheader("📋 Your Goals")

    if goals_df.empty:
        st.info("No financial goals added yet.")
    else:
        # Card styles
        st.markdown(
            """
            <style>
            .goal-card {
                background: #1e1e1e;
                border-radius: 12px;
                padding: 14px 14px 10px 14px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                border: 1px solid #333;
                margin-bottom: 12px;
            }
            .goal-title { font-weight: 700; font-size: 16px; margin-bottom: 6px; color: #4da3ff; }
            .goal-line { display: flex; justify-content: space-between; font-size: 13px; margin: 2px 0; color: #e0e0e0; }
            .muted { color: #999; }
            .value { font-weight: 600; color: #fff; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Ensure proper types
        goals_df_display = goals_df.copy()
        goals_df_display["Deadline"] = pd.to_datetime(goals_df_display["Deadline"], errors="coerce")

        # Sort by nearest deadline
        goals_df_display = goals_df_display.sort_values("Deadline")

        # Show in 4-column grid with quick update/delete actions
        cols_per_row = 4
        rows = range(0, len(goals_df_display), cols_per_row)
        for start_idx in rows:
            cols = st.columns(cols_per_row)
            for offset in range(cols_per_row):
                idx = start_idx + offset
                if idx >= len(goals_df_display):
                    continue
                row = goals_df_display.iloc[idx]
                goal_name = str(row["Goal"]) if pd.notna(row["Goal"]) else "Untitled Goal"
                target_amt = float(row["Target Amount"]) if pd.notna(row["Target Amount"]) else 0.0
                saved_amt = float(row["Amount Saved"]) if pd.notna(row["Amount Saved"]) else 0.0
                remaining = max(0.0, target_amt - saved_amt)
                deadline_dt = row["Deadline"]
                deadline_str = deadline_dt.date().isoformat() if pd.notna(deadline_dt) else "—"
                progress = 0.0 if target_amt <= 0 else min(1.0, saved_amt / target_amt)

                with cols[offset]:
                    st.markdown(
                        f"""
                        <div class="goal-card">
                            <div class="goal-title">🎯 {goal_name}</div>
                            <div class="goal-line"><span class="muted">Target</span><span class="value">KSH {target_amt:,.2f}</span></div>
                            <div class="goal-line"><span class="muted">Saved</span><span class="value">KSH {saved_amt:,.2f}</span></div>
                            <div class="goal-line"><span class="muted">Remaining</span><span class="value">KSH {remaining:,.2f}</span></div>
                            <div class="goal-line"><span class="muted">Deadline</span><span class="value">{deadline_str}</span></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.progress(progress, text=f"{progress*100:.1f}%")

                    # Quick actions under each card
                    new_saved = st.number_input(
                        "Update Saved",
                        min_value=0.0,
                        value=float(saved_amt),
                        step=100.0,
                        key=f"saved_{start_idx}_{offset}"
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("💾 Save", key=f"save_{start_idx}_{offset}"):
                            goals_df.loc[goals_df_display.index[idx], "Amount Saved"] = new_saved
                            save_goals(goals_df)
                            st.rerun()
                    with c2:
                        if st.button("🗑️ Delete", key=f"del_{start_idx}_{offset}"):
                            goals_df = goals_df.drop(index=goals_df_display.index[idx]).reset_index(drop=True)
                            save_goals(goals_df)
                            st.rerun()

        st.markdown("---")
        st.markdown("#### 📋 All Goals")
        st.dataframe(goals_df_display, hide_index=True)

        # Download
        csv = goals_df_display.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Goals", data=csv, file_name="financial_goals.csv", mime="text/csv")


