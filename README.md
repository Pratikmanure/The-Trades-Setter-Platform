# The Trades Setter 🏦 - Quantitative Algo Trading Backtester

**Built by:** Pratik Manure
**Live Demo:** [Streamlit Cloud Deployment]

## 📌 Project Overview
The Trades Setter is a full-stack Software-as-a-Service (SaaS) platform designed for quantitative traders and financial data analysts. The platform provides a closed-ecosystem environment to backtest algorithmic trading strategies against real-world historical market data.

It features a Role-Based Access Control (RBAC) authentication system, interactive Plotly visualization, and a proprietary Python sandboxing environment that allows users to upload and execute their custom strategy code dynamically.

---

## 🛠️ System Architecture

This project was built using a classic **ETL (Extract, Transform, Load)** Data Engineering architecture, decoupled into three highly cohesive modules:

### 1. Data Extraction & Transformation Engine (`data_engine.py`)
- **Extraction:** Leverages the `yfinance` API to fetch highly-accurate, historical, and live financial data across 37 unique assets spanning Cryptocurrency, Forex, and physical Commodities.
- **Transformation:** Utilizes vectorized Pandas and NumPy logic to clean missing data, normalize columns, and calculate financial technical indicators (defaulting to the Exponential Moving Average 9/21 Crossover).
- **Graceful Failure:** Implements exception-handling safeguards to protect the user interface against API rate limits and network degradation.

### 2. Database & Identity Management (`database_manager.py`)
- Engineered a programmatic relational SQL database (`trading_system.db`) utilizing the `sqlite3` engine.
- Implemented a custom Role-Based Identity Access system. Web users can register accounts, but access is completely strictly "Default Deny". 
- Administrators have access to a distinct God-Mode panel where they must securely update user approval schemas (`is_approved = 1`) before users can request financial data.

### 3. Reactive UI & Visualization (`dashboard.py`)
- Built a multi-tab Software-as-a-Service dashboard completely in Python using the `Streamlit` framework.
- **Dynamic Charting:** Integrated `Plotly` to render interactive candlestick charts that superimpose algorithmic trading logic (buy/sell triggers) directly onto real price action.
- **Code Sandboxing:** Architected a "Custom Strategy Upload" module. The Streamlit backend captures user-uploaded `.py` files, instantiates a secure variable dictionary, and utilizes Python `exec()` logic to backtest user-written functions against the system's live market data.

---

## 💻 Tech Stack
* **Language:** Python 3.10+
* **Data Engineering:** Pandas, NumPy
* **Financial APIs:** yfinance
* **Databases:** SQLite3 (SQL)
* **Frontend UI:** Streamlit, Plotly Graph Objects
* **Deployment:** Streamlit Community Cloud & GitHub

---

## 🚀 How to Run Locally

1. Create a virtual environment and load the `requirements.txt`:
```bash
pip install -r requirements.txt
```

2. Start the local Streamlit server:
```bash
python -m streamlit run dashboard.py
```

3. **Login Details:** The database will initialize on the first boot. 
   - Default Admin Username: `traderpratik`
   - Default Admin Password: `traderpratik`
