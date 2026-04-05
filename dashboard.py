import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import database_manager as dbm
import data_engine as engine

# 1. App Configuration
st.set_page_config(page_title="The Trades Setter", page_icon="🏦", layout="wide")

# 2. Database Init
dbm.init_db()

# Asset Dictionaries for Dropdowns
ASSET_CLASSES = {
    "Cryptocurrency": [
        "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", 
        "ADA-USD", "DOGE-USD", "DOT-USD", "MATIC-USD", "LTC-USD"
    ],
    "Forex": [
        "EURUSD=X", "JPY=X", "GBPUSD=X", "AUDUSD=X", "USDCAD=X", 
        "USDCHF=X", "NZDUSD=X", "EURJPY=X", "GBPJPY=X", "EURGBP=X", 
        "AUDJPY=X", "EURAUD=X", "EURCHF=X", "AUDNZD=X", "NZDJPY=X", 
        "GBPAUD=X", "GBPCAD=X", "EURNZD=X", "AUDCAD=X", "GBPCHF=X"
    ],
    "Commodities": [
        "GC=F",   # Gold
        "SI=F",   # Silver
        "CL=F",   # Crude Oil
        "NG=F",   # Natural Gas
        "HG=F",   # Copper
        "ZC=F",   # Corn
        "ZW=F"    # Wheat
    ]
}

# 3. Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'is_approved' not in st.session_state:
    st.session_state.is_approved = False

# =========================================================================
# BRANDING
# =========================================================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3229/3229871.png", width=100)
    st.title("The Trades Setter")
    st.markdown("---")
    if st.session_state.logged_in:
        st.success(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.is_approved = False
            st.rerun()
    st.markdown("---")
    st.markdown("### Platform Architect")
    st.markdown("**Pratik Manure**")
    st.markdown("📧 pratikmanure28@gmail.com")
    st.markdown("📷 Instagram: [@pratik.manure](https://instagram.com/pratik.manure)")

# =========================================================================
# PAGES LOGIC
# =========================================================================
def login_register_page():
    st.title("Welcome to The Trades Setter 🏦")
    st.markdown("Log in or create an account to access the quantitative algorithm engine.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Login")
        log_user = st.text_input("Username", key="log_user")
        log_pass = st.text_input("Password", type="password", key="log_pass")
        if st.button("Login"):
            auth = dbm.authenticate_user(log_user, log_pass)
            if auth['success']:
                st.session_state.logged_in = True
                st.session_state.username = log_user
                st.session_state.is_approved = auth['is_approved']
                st.rerun()
            else:
                st.error("Invalid credentials.")
                
    with col2:
        st.subheader("Sign Up")
        reg_user = st.text_input("New Username", key="reg_user")
        reg_pass = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register"):
            if dbm.register_user(reg_user, reg_pass):
                st.success("✅ Successfully registered! Please log in (Note: You must wait for Administrator approval to access data).")
            else:
                st.error("Username already exists!")

def not_approved_page():
    st.error("🚪 Access Denied: Account Pending Approval")
    st.warning("Please contact database and website administrator to approve your account.")
    st.info("**Administrator**: Pratik Manure\n\n**Email**: pratikmanure28@gmail.com\n\n**Instagram**: @pratik.manure")
    
def main_dashboard():
    tabs = ["📈 Backtest Engine", "💻 Upload Your Strategy"]
    if st.session_state.username == "traderpratik":
        tabs.append("👑 Admin Panel")
        
    app_tabs = st.tabs(tabs)
    
    # ---------------------------------------------------------------------
    # TAB 1: MAIN DASHBOARD & TRADING PAIRS
    # ---------------------------------------------------------------------
    with app_tabs[0]:
        st.title("📈 Quantitative Market Analysis")
        
        # Categorized Trading Pair Selector
        col_cat, col_pair, col_metric1, col_metric2 = st.columns([1,1,1,1])
        with col_cat:
            asset_class = st.selectbox("Asset Class", list(ASSET_CLASSES.keys()))
        with col_pair:
            trading_pair = st.selectbox("Trading Pair", ASSET_CLASSES[asset_class])
        
        # Load the data dynamically
        with st.spinner(f"Fetching live data and running algorithms for {trading_pair}..."):
            df = engine.get_live_data(trading_pair)
            
        if not df.empty:
            with col_metric1:
                st.metric(label="Current Date", value=str(df['Date'].iloc[-1].date()))
            with col_metric2:
                if 'signal' in df.columns:
                    st.metric(label="Latest Signal", value="BUY 🟢" if df['signal'].iloc[-1] == 1 else "SELL 🔴")
                
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df['Date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price'))
            
            if 'ema_9' in df.columns:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_9'], line=dict(color='#00F0FF', width=1.5), name='System EMA 9'))
                fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_21'], line=dict(color='#FF0055', width=1.5), name='System EMA 21'))
            
            fig.update_layout(title=f'{trading_pair} Price Action', template='plotly_dark', height=650)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error(f"❌ Yahoo Finance failed to return data for {trading_pair}. The symbol may be temporarily blocked or rate-limited by Yahoo. Try selecting a different asset!")
                
    # ---------------------------------------------------------------------
    # TAB 2: UPLOAD STRATEGY
    # ---------------------------------------------------------------------
    with app_tabs[1]:
        st.title("💻 Custom Strategy Upload (Beta)")
        st.markdown("Upload your own Python script (`.py`). It must contain a function called `apply_strategy(df)` that returns your buy/sell logic!")
        
        uploaded_file = st.file_uploader("Upload Python Implementation", type=["py"])
        
        col_cat_test, col_pair_test = st.columns(2)
        with col_cat_test:
            test_asset_class = st.selectbox("Test Asset Class:", list(ASSET_CLASSES.keys()))
        with col_pair_test:
            target_asset = st.selectbox("Select Asset to Test Against:", ASSET_CLASSES[test_asset_class])
        
        if uploaded_file is not None and st.button("Execute Backtest"):
            source_code = uploaded_file.getvalue().decode("utf-8")
            raw_data = engine.clean_data(engine.fetch_crypto_data(target_asset))
            
            st.success("Custom Python Script Injected!")
            with st.spinner("Compiling and running against data..."):
                try:
                    local_env = {"pd": pd, "np": np}
                    exec(source_code, globals(), local_env)
                    
                    if 'apply_strategy' in local_env:
                        custom_df = local_env['apply_strategy'](raw_data)
                        st.write("### Strategy Results Output")
                        st.dataframe(custom_df.tail(15))
                    else:
                        st.error("Error: Code did not contain 'apply_strategy(df)' function.")
                except Exception as e:
                    st.error(f"Execution Error in your script: {str(e)}")

    # ---------------------------------------------------------------------
    # TAB 3: ADMIN CONTROLS
    # ---------------------------------------------------------------------
    if st.session_state.username == "traderpratik":
        with app_tabs[2]:
            st.title("👑 God Mode Control Panel")
            st.markdown("As 'traderpratik', you have full authority over the database.")
            
            users_df = dbm.get_all_users()
            st.write("### Database: Registered Users")
            st.dataframe(users_df)
            
            if not users_df.empty:
                pending_users = users_df[users_df['is_approved'] == 0]['username'].tolist()
                user_to_approve = st.selectbox("Select User Account to Approve:", pending_users)
                
                if st.button("✅ Approve User Account") and user_to_approve:
                    dbm.approve_user(user_to_approve)
                    st.success(f"System access granted to user '{user_to_approve}'!")
                    st.rerun()

# =========================================================================
# ROUTING
# =========================================================================
if not st.session_state.logged_in:
    login_register_page()
elif st.session_state.logged_in and not st.session_state.is_approved:
    not_approved_page()
else:
    main_dashboard()
