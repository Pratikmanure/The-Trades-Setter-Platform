import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import data_engine as engine
from streamlit_cookies_manager import EncryptedCookieManager
import database_manager as dbm

st.set_page_config(page_title="Pro Terminal", layout="wide", initial_sidebar_state="expanded")
st.markdown("<style>.stMetric {background-color: #1a1a1a; padding: 10px; border-radius: 5px;} div[data-testid='stSidebarNav'] {display:none;}</style>", unsafe_allow_html=True)

# Auth Cookies & SQLite DB Init
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

# ================= SIDEBAR =================
with st.sidebar:
    st.title("⚡ Pro Terminal")
    st.markdown("---")
    if st.session_state.logged_in:
        st.success(f"Logged in: {st.session_state.username}")
        if st.button("Logout"):
            cookies["login"] = "false"
            cookies.save()
            st.session_state.logged_in = False
            st.rerun()
        st.markdown("---")
    
    symbol = st.selectbox("Asset", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AAPL", "EURUSD=X"])
    tfs = {"1 Minute": "1m", "5 Minute": "5m", "15 Minute": "15m", "1 Hour": "1h", "4 Hour": "4h", "1 Day": "1d"}
    tf = tfs[st.selectbox("Timeframe", list(tfs.keys()), index=5)]
    
    emas = st.multiselect("EMA Periods (First 2 used for signals)", [5, 9, 13, 21, 50, 100, 200], default=[9, 21])
    
    run_btn = st.button("🚀 Run Strategy", use_container_width=True)

# ================= AUTHENTICATION =================
if not st.session_state.logged_in:
    c1, c2 = st.columns(2)
    with c1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            auth = dbm.authenticate_user(u, p)
            if auth['success'] and auth['is_approved']:
                cookies["login"] = "true"
                cookies["username"] = u
                cookies.save()
                st.session_state.logged_in, st.session_state.username, st.session_state.is_approved = True, u, True
                st.rerun()
            else:
                st.error("Invalid credentials or unapproved account.")
    st.stop()

# ================= MAIN TERMINAL =================
if run_btn or 'res' not in st.session_state:
    st.session_state.res = load_data(symbol, tf, tuple(emas))

res = st.session_state.res
df, kpi = res['df'], res['kpi']

if df.empty:
    st.error("Data unavailable for this timeframe/symbol.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Return", f"{kpi['total_return']:.2f}%")
k2.metric("Win Rate", f"{kpi['win_rate']:.2f}%")
k3.metric("Max Drawdown", f"{kpi['max_drawdown']:.2f}%", delta="-Risk", delta_color="inverse")
k4.metric("Sharpe Ratio", f"{kpi['sharpe_ratio']:.2f}")

# TradingView-style Chart
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price'))

colors = ['#00F0FF', '#FF0055', '#FFD700', '#00ff00', '#ff0000', '#ffffff', '#cccccc']
for i, ema in enumerate(emas):
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df[f'ema_{ema}'], mode='lines', name=f'EMA {ema}', line=dict(width=1, color=colors[i%len(colors)])))

buys, sells = df[df['trade_trigger'] == 2], df[df['trade_trigger'] == -2]
fig.add_trace(go.Scatter(x=buys['timestamp'], y=buys['close'], mode='markers', marker=dict(symbol='triangle-up', size=14, color='#00ff00', line=dict(width=1, color='black')), name='Buy'))
fig.add_trace(go.Scatter(x=sells['timestamp'], y=sells['close'], mode='markers', marker=dict(symbol='triangle-down', size=14, color='#ff0000', line=dict(width=1, color='black')), name='Sell'))

fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False, height=650, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    fig_eq = go.Figure()
    fig_eq.add_trace(go.Scatter(x=df['timestamp'], y=df['equity_curve'], fill='tozeroy', name='Equity'))
    fig_eq.update_layout(title="Equity Curve", template="plotly_dark", height=300, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_eq, use_container_width=True)
with c2:
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name='RSI', line=dict(color='yellow')))
    fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
    fig_rsi.update_layout(title="RSI Oscillator", template="plotly_dark", height=300, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_rsi, use_container_width=True)
