import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import data_engine as engine
from streamlit_cookies_manager import EncryptedCookieManager
import database_manager as dbm

# ================= PAGE CONFIG & AVOID 'IDIOTIC' UI ELEMENTS =================
st.set_page_config(page_title="Algorithmic Trading Terminal", layout="wide", initial_sidebar_state="expanded")

# Inject minimal, professional institutional CSS (remove streamliot fluff)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stMetric {
        background-color: #121212; 
        padding: 10px; 
        border-right: 2px solid #292929;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid='stSidebarNav'] {display:none;}
    
    /* Sleek container for the login */
    .login-container {
        border: 1px solid #333333;
        border-radius: 8px;
        padding: 40px;
        background-color: #0E1117;
    }
</style>
""", unsafe_allow_html=True)

dbm.init_db()
cookies = EncryptedCookieManager(prefix="trading_app", password="dummy_cookie_password_secret")
if not cookies.ready(): st.stop()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = True if cookies.get("login") == "true" else False
    st.session_state.username = cookies.get("username") if cookies.get("login") == "true" else ""
    st.session_state.is_approved = True if cookies.get("login") == "true" else False

@st.cache_data(ttl=60)
def load_data(sym, tf, emas_tuple):
    return engine.apply_strategy(engine.fetch_data(sym, tf), list(emas_tuple))

# ================= AUTHENTICATION MODAL =================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-weight: 300; letter-spacing: 2px;'>CORE TRADING TERMINAL</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            tabs = st.tabs(["Secure Gateway", "Request API Access"])
            with tabs[0]:
                u = st.text_input("Operator ID", key="login_user")
                p = st.text_input("Access Key", type="password", key="login_pass")
                if st.button("Establish Connection", use_container_width=True, type="primary"):
                    auth = dbm.authenticate_user(u, p)
                    if auth['success'] and auth['is_approved']:
                        cookies["login"] = "true"
                        cookies["username"] = u
                        cookies.save()
                        st.session_state.logged_in, st.session_state.username, st.session_state.is_approved = True, u, True
                        st.rerun()
                    else:
                        st.error("System Override: Unapproved Account or Invalid Credentials.")
            with tabs[1]:
                reg_u = st.text_input("Desired Operator ID", key="reg_user")
                reg_p = st.text_input("Secure Access Key", type="password", key="reg_pass")
                if st.button("Submit Node Registration", use_container_width=True):
                    if dbm.register_user(reg_u, reg_p):
                        st.success("Registration Sent. Pending Database Administrator Approval.")
                    else:
                        st.error("Operator ID already exists in the registry.")
    st.stop()

# ================= SIDEBAR & ADMIN CONTROLS =================
with st.sidebar:
    st.markdown("### SYSTEM PARAMETERS")
    st.markdown("---")
    
    symbol = st.selectbox("Market Asset", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AAPL", "EURUSD=X", "GC=F"])
    tfs = {"1 Minute": "1m", "5 Minute": "5m", "15 Minute": "15m", "1 Hour": "1h", "4 Hour": "4h", "1 Day": "1d"}
    tf = tfs[st.selectbox("Data Timeframe", list(tfs.keys()), index=5)]
    emas = st.multiselect("EMA Matrix Computation", [5, 9, 13, 21, 50, 100, 200], default=[9, 21])
    
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("Execute Algorithm", use_container_width=True, type="primary")
    
    st.markdown("---")
    
    # MISSING ADMIN PANEL RESTORED HERE
    if st.session_state.username == "traderpratik":
        st.markdown("### ADMINISTRATOR CONSOLE")
        users_df = dbm.get_all_users()
        if not users_df.empty:
            pending_users = users_df[users_df['is_approved'] == 0]['username'].tolist()
            user_to_approve = st.selectbox("Pending Role Approvals", ["Select User"] + pending_users)
            if st.button("Grant Network Access") and user_to_approve != "Select User":
                dbm.approve_user(user_to_approve)
                st.success(f"Access granted to {user_to_approve}")
                st.rerun()
        st.markdown("---")
    
    st.caption(f"Active Session: {st.session_state.username}")
    if st.button("Terminate Session", use_container_width=True):
        cookies["login"] = "false"
        cookies.save()
        st.session_state.logged_in = False
        st.rerun()

# ================= MAIN TERMINAL =================
if run_btn or 'res' not in st.session_state:
    with st.spinner("Fetching execution data..."):
        st.session_state.res = load_data(symbol, tf, tuple(emas))

res = st.session_state.res
df, kpi = res['df'], res['kpi']

if df.empty:
    st.error("Market Data unavailable or blocked by API rate limits for the selected configuration.")
    st.stop()

# SERIOUS KPI CARDS
st.markdown("### QUANTITATIVE PERFORMANCE METRICS")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Gross Alpha Return", f"{kpi['total_return']:.2f}%")
k2.metric("Execution Win Rate", f"{kpi['win_rate']:.2f}%")
k3.metric("Max Capital Drawdown", f"{kpi['max_drawdown']:.2f}%")
k4.metric("Sharpe Index", f"{kpi['sharpe_ratio']:.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# TRADINGVIEW STYLE TABS
app_tabs = st.tabs(["Market Action", "Analytics & Oscillators"])

# Main Price Chart
with app_tabs[0]:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price Action'))

    color_matrix = ['#2962FF', '#FF6D00', '#FFD700', '#00E676', '#D50000', '#FFFFFF', '#9E9E9E']
    for i, ema in enumerate(emas):
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df[f'ema_{ema}'], mode='lines', name=f'EMA {ema}', line=dict(width=1.5, color=color_matrix[i%len(color_matrix)])))

    buys, sells = df[df['trade_trigger'] == 2], df[df['trade_trigger'] == -2]
    fig.add_trace(go.Scatter(x=buys['timestamp'], y=buys['low'] * 0.99, mode='markers', marker=dict(symbol='triangle-up', size=12, color='#00E676'), name='Algorithm BUY'))
    fig.add_trace(go.Scatter(x=sells['timestamp'], y=sells['high'] * 1.01, mode='markers', marker=dict(symbol='triangle-down', size=12, color='#D50000'), name='Algorithm SELL'))

    fig.update_layout(
        template="plotly_dark", 
        xaxis_rangeslider_visible=False, 
        height=650, 
        margin=dict(l=0, r=0, t=10, b=0), 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='#0E1117',
        paper_bgcolor='#0E1117',
        yaxis_title="Price"
    )
    st.plotly_chart(fig, use_container_width=True)

# Secondary Charts (Analytics)
with app_tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(x=df['timestamp'], y=df['equity_curve'], fill='tozeroy', name='Equity', line=dict(color="#FFD700", width=1)))
        fig_eq.update_layout(title="Simulated Portfolio Growth", template="plotly_dark", height=350, margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor='#0E1117', paper_bgcolor='#0E1117')
        st.plotly_chart(fig_eq, use_container_width=True)
        
    with c2:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name='RSI', line=dict(color='#2962FF', width=1.5)))
        fig_rsi.add_hline(y=70, line_dash="dot", line_color="#D50000", line_width=1)
        fig_rsi.add_hline(y=30, line_dash="dot", line_color="#00E676", line_width=1)
        fig_rsi.update_layout(title="RSI Momentum Oscillation", template="plotly_dark", height=350, margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor='#0E1117', paper_bgcolor='#0E1117')
        st.plotly_chart(fig_rsi, use_container_width=True)
