import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import data_engine as engine
from streamlit_cookies_manager import EncryptedCookieManager
import database_manager as dbm

st.set_page_config(page_title="Pro Terminal", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>.stMetric {background-color: #1a1a1a; padding: 10px; border-radius: 5px;} div[data-testid='stSidebarNav'] {display:none;}</style>", unsafe_allow_html=True)

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
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: white;'>🏦 The Trades Setter <span style='color: #00F0FF;'>PRO</span></h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Institutional Quantitative Backtesting Terminal</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container(border=True):
            tabs = st.tabs(["🔐 Secure Login", "📝 Request Access"])
            with tabs[0]:
                st.markdown("<br>", unsafe_allow_html=True)
                u = st.text_input("Username", key="login_user")
                p = st.text_input("Password", type="password", key="login_pass")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Authenticate System", use_container_width=True, type="primary"):
                    auth = dbm.authenticate_user(u, p)
                    if auth['success'] and auth['is_approved']:
                        cookies["login"] = "true"
                        cookies["username"] = u
                        cookies.save()
                        st.session_state.logged_in, st.session_state.username, st.session_state.is_approved = True, u, True
                        st.rerun()
                    else:
                        st.error("❌ Access Denied: Invalid credentials or account pending administrator approval.")
            with tabs[1]:
                st.markdown("<br>", unsafe_allow_html=True)
                reg_u = st.text_input("Desired Username", key="reg_user")
                reg_p = st.text_input("Secure Password", type="password", key="reg_pass")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Submit Registration", use_container_width=True):
                    if dbm.register_user(reg_u, reg_p):
                        st.success("✅ Registration Successful! Please contact Administrator Pratik Manure for database approval.")
                    else:
                        st.error("Username already exists!")
    st.stop()

# ================= SIDEBAR =================
with st.sidebar:
    st.title("⚡ Pro Terminal")
    st.markdown("---")
    st.success(f"Verified Identity: **{st.session_state.username}**")
    if st.button("Logout System", use_container_width=True):
        cookies["login"] = "false"
        cookies.save()
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("---")
    
    symbol = st.selectbox("Market Asset", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AAPL", "EURUSD=X", "GC=F"])
    tfs = {"1 Minute": "1m", "5 Minute": "5m", "15 Minute": "15m", "1 Hour": "1h", "4 Hour": "4h", "1 Day": "1d"}
    tf = tfs[st.selectbox("Timeframe (1 Year History)", list(tfs.keys()), index=5)]
    emas = st.multiselect("Mathematical EMA Matrix", [5, 9, 13, 21, 50, 100, 200], default=[9, 21])
    
    st.markdown("<br>", unsafe_allow_html=True)
    run_btn = st.button("🚀 Compile Algorithm", use_container_width=True, type="primary")

# ================= MAIN TERMINAL =================
if run_btn or 'res' not in st.session_state:
    st.session_state.res = load_data(symbol, tf, tuple(emas))

res = st.session_state.res
df, kpi = res['df'], res['kpi']

if df.empty:
    st.error(f"❌ Market Data unavailable for {symbol} on the {tf} timeframe. API limit reached or invalid ticker.")
    st.stop()

# KPI CARDS
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Return (1yr)", f"{kpi['total_return']:.2f}%")
k2.metric("System Win Rate", f"{kpi['win_rate']:.2f}%")
k3.metric("Max Drawdown limit", f"{kpi['max_drawdown']:.2f}%", delta="-Risk", delta_color="inverse")
k4.metric("Sharpe Ratio", f"{kpi['sharpe_ratio']:.2f}")

# TradingView-style Chart
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price'))

colors = ['#00F0FF', '#FF0055', '#FFD700', '#00ff00', '#ff0000', '#ffffff', '#cccccc']
for i, ema in enumerate(emas):
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df[f'ema_{ema}'], mode='lines', name=f'EMA {ema}', line=dict(width=1.5, color=colors[i%len(colors)])))

buys, sells = df[df['trade_trigger'] == 2], df[df['trade_trigger'] == -2]
fig.add_trace(go.Scatter(x=buys['timestamp'], y=buys['close'], mode='markers', marker=dict(symbol='triangle-up', size=16, color='#00ff00', line=dict(width=1, color='black')), name='Execute BUY'))
fig.add_trace(go.Scatter(x=sells['timestamp'], y=sells['close'], mode='markers', marker=dict(symbol='triangle-down', size=16, color='#ff0000', line=dict(width=1, color='black')), name='Execute SELL'))

fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=650, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig, use_container_width=True)

# Sub charts
c1, c2 = st.columns(2)
with c1:
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(x=df['timestamp'], y=df['equity_curve'], fill='tozeroy', name='Equity', line=dict(color="#FFD700")))
    fig_eq.update_layout(title="Simulated Portfolio Equity Curve", template="plotly_dark", height=350, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_eq, use_container_width=True)
    
with c2:
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name='RSI', line=dict(color='#00F0FF')))
    fig_rsi.add_hline(y=70, line_dash="dot", line_color="#ff0000")
    fig_rsi.add_hline(y=30, line_dash="dot", line_color="#00ff00")
    fig_rsi.update_layout(title="RSI Momentum Oscillator", template="plotly_dark", height=350, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_rsi, use_container_width=True)
