import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import data_engine as engine

# ==========================================
# 1. PAGE CONFIGURATION & AESTHETICS
# ==========================================
st.set_page_config(
    page_title="Quantitative Trading Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for spacing and aesthetic tuning
st.markdown("""
<style>
    .stMetric {
        background-color: #1E1E1E;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #333;
    }
    div[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SIDEBAR - CONTROL PANEL
# ==========================================
with st.sidebar:
    st.markdown("## ⚙️ Algo Control Panel")
    st.markdown("---")
    
    st.markdown("### 📊 Market Selection")
    asset_dict = {
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"],
        "Forex": ["EURUSD=X", "JPY=X", "GBPUSD=X"],
        "Equities / Commodities": ["AAPL", "MSFT", "TSLA", "GC=F", "CL=F"]
    }
    asset_class = st.selectbox("Asset Class", list(asset_dict.keys()))
    symbol = st.selectbox("Ticker / Pair", asset_dict[asset_class])
    
    timeframe = st.selectbox("Timeframe", ["1y", "2y", "5y", "ytd", "6m"])
    interval = st.selectbox("Interval", ["1d", "1wk"], index=0)
    
    st.markdown("---")
    st.markdown("### 🧮 Strategy Parameters")
    col1, col2 = st.columns(2)
    with col1:
        fast_ema = st.number_input("Fast EMA", min_value=1, max_value=200, value=9)
    with col2:
        slow_ema = st.number_input("Slow EMA", min_value=1, max_value=500, value=21)
    
    st.markdown("---")
    run_strategy = st.button("🚀 Execute Strategy", use_container_width=True, type="primary")

# ==========================================
# MAIN DASHBOARD LOGIC
# ==========================================
if 'results' not in st.session_state:
    st.session_state.results = None
if 'heatmap_data' not in st.session_state:
    st.session_state.heatmap_data = None

if run_strategy:
    with st.spinner("Compiling algorithmic matrix..."):
        st.session_state.results = engine.get_live_data(symbol, fast_ema, slow_ema, timeframe, interval)
        st.session_state.heatmap_data = engine.optimize_strategy(symbol, timeframe, interval)

# Main UI Rendering
if st.session_state.results:
    res = st.session_state.results
    df = res['df']
    kpi = res['kpi']
    trade_log = res['trade_log']
    
    # ------------------------------------------
    # 3. TOP KPI METRIC CARDS
    # ------------------------------------------
    st.markdown(f"## ⚡ Terminal Analysis: {symbol} ({timeframe})")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Return", f"{kpi['total_return']:.2f} %", delta=f"{kpi['total_return']:.2f}%")
    k2.metric("Win Rate", f"{kpi['win_rate']:.2f} %")
    k3.metric("Max Drawdown", f"{kpi['max_drawdown']:.2f} %", delta="-Risk", delta_color="inverse")
    k4.metric("Sharpe Ratio", f"{kpi['sharpe_ratio']:.3f}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ------------------------------------------
    # GUI TABS
    # ------------------------------------------
    tab_overview, tab_trades, tab_analytics, tab_optimization = st.tabs([
        "📈 Charting Overview", 
        "📋 Trade Log", 
        "🔬 Analytics", 
        "🔥 Optimization Heatmap"
    ])
    
    # --- TAB 1: PLOTLY DASHBOARD ---
    with tab_overview:
        # Create a 3-Row Subplot: Price, Equity, Drawdown
        fig = make_subplots(
            rows=3, cols=1, shared_xaxes=True, 
            vertical_spacing=0.05, 
            row_heights=[0.6, 0.25, 0.15],
            subplot_titles=("Price Action & Signals", "Portoflio Equity Curve", "Drawdown Profile")
        )

        # 4. CANDLESTICK & SIGNALS (ROW 1)
        fig.add_trace(go.Candlestick(x=df['Date'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_fast'], line=dict(color='#00F0FF', width=1), name=f'EMA {fast_ema}'), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date'], y=df['ema_slow'], line=dict(color='#FF0055', width=1), name=f'EMA {slow_ema}'), row=1, col=1)

        buys = df[df['trade_trigger'] == 2]
        sells = df[df['trade_trigger'] == -2]
        
        fig.add_trace(go.Scatter(
            x=buys['Date'], y=buys['close'], mode='markers',
            marker=dict(symbol='triangle-up', size=12, color='#00ff00', line=dict(width=1, color='black')),
            name='BUY'
        ), row=1, col=1)
        
        fig.add_trace(go.Scatter(
            x=sells['Date'], y=sells['close'], mode='markers',
            marker=dict(symbol='triangle-down', size=12, color='#ff0000', line=dict(width=1, color='black')),
            name='SELL'
        ), row=1, col=1)

        # 5. EQUITY CURVE (ROW 2)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['equity_curve'], 
            line=dict(color='#FFD700', width=2), name='Equity', fill='tozeroy'
        ), row=2, col=1)

        # 5. DRAWDOWN (ROW 3)
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['drawdown'], 
            line=dict(color='#ff3333', width=1), name='Drawdown %', fill='tozeroy'
        ), row=3, col=1)

        # Update Layouts for Professional UI
        fig.update_layout(
            template='plotly_dark', 
            height=900, 
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis3_rangeslider_visible=True,
            xaxis_rangeslider_visible=False,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- TAB 2: TRADE LOG ---
    with tab_trades:
        st.markdown("### 📋 Historic Execution Ledger")
        if not trade_log.empty:
            # Color coding the action column
            def color_action(val):
                color = 'green' if val == 'BUY' else 'red'
                return f'color: {color}; font-weight: bold;'
            
            st.dataframe(
                trade_log.style.applymap(color_action, subset=['Action']), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No trades executed during this timeframe.")

    # --- TAB 3: ANALYTICS ---
    with tab_analytics:
        st.markdown("### 🔬 Strategy vs Market Performance")
        
        # SQL-style analytics representation
        end_price = df['close'].iloc[-1]
        start_price = df['close'].iloc[0]
        buy_and_hold = ((end_price / start_price) - 1) * 100
        
        c_an1, c_an2 = st.columns(2)
        with c_an1:
            st.info("#### Base Market Yield (Buy & Hold)")
            st.metric("Market Return", f"{buy_and_hold:.2f}%")
            st.metric("Initial Asset Price", f"${start_price:.2f}")
            st.metric("Final Asset Price", f"${end_price:.2f}")
            
        with c_an2:
            st.success("#### Algorithmic Alpha")
            st.metric("Strategy Return", f"{kpi['total_return']:.2f}%", delta=f"{(kpi['total_return'] - buy_and_hold):.2f}% vs Market")
            st.metric("Starting Capital", "$10,000.00")
            st.metric("Ending Capital", f"${str(round(kpi['total_return']/100 * 10000 + 10000, 2))}")

    # --- TAB 4: HEATMAP ---
    with tab_optimization:
        st.markdown("### 🔥 Hyperparameter Optimization Surface (5-50 EMA matrix)")
        st.markdown("Visualizing Total Return % across various Slow and Fast moving average combinations to locate optimal parameters.")
        
        hm_data = st.session_state.heatmap_data
        if hm_data is not None and not hm_data.empty:
            fig_hm = px.imshow(
                hm_data, 
                text_auto=True, 
                aspect="auto",
                color_continuous_scale="RdYlGn",
                labels=dict(x="Fast EMA Length", y="Slow EMA Length", color="Return %")
            )
            fig_hm.update_layout(template='plotly_dark', height=600)
            st.plotly_chart(fig_hm, use_container_width=True)
        else:
            st.warning("Insufficient data to generate parameter heatmap.")

else:
    # Landing State
    st.info("👆 Configure your algorithmic constraints in the Sidebar and hit **Execute Strategy** to compile the terminal.")
