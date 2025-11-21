import streamlit as st
from config import *

st.title("📘 Guidelines & Help")

st.markdown(r"""
### 🚀 Quick Start
- Add Entry: record your first expense or income
- Transactions: filter, search, and delete a row if needed
- Import/Export: download sample CSV, upload your data, then merge
- Reports: explore charts for the current month or year
- Budgets: set per‑category monthly limits
- Goals: create a goal and update the saved amount inline

---

Welcome to your Personal Finance Tracker! Follow these tips to get the most out of it.

---

### ➕ Add Expense or Income
- Use the **Add Entry** tab to quickly record items
- Pick **Type** (Income/Expense), select **Category**, enter **Amount** and **Date**
- Add an optional **Description** to remember details

---

### 📄 Transactions
- Filter by predefined ranges (This Week/Month/Year) or a **Custom Range**
- Use the search box to find entries by description
- Download filtered results as CSV
- Delete a selected row directly from this tab

---

### 📁 Import/Export
- Download the sample CSV to see the required format
- Upload your CSV to preview and validate
- Click **Merge** to add valid rows to your data (duplicates removed automatically)

---

### 📊 Reports
- Explore **Pie**, **Bar**, and **Line** charts to analyze spending and cash flow
- Filter by month/year for focused insights

---

### 💰 Budgets
- Set per‑category monthly budgets
- Track spending vs budget with progress indicators
- Budgets are saved locally and persist between sessions

---

### 🎯 Goals
- Create goals with target amount and deadline
- Each goal shows a progress bar; update saved amount inline
- Delete a goal directly from the card

---

### 🧾 Data & Backup
- All data is stored locally in `data/`
- You can export CSVs anytime for backup

---

### Tips
- Keep category names consistent for cleaner reports
- Enter dates in `YYYY-MM-DD` format
- Avoid zero amounts; they're filtered out on import

---

**Happy Tracking! 💰 | © 2025 Personal Finance Tracker**
""")
