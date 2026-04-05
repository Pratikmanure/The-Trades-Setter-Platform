import os
from datetime import datetime

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

import database_manager as dbm
from data import DEFAULT_SYMBOLS, TIMEFRAME_OPTIONS, load_market_data
from strategy import compare_strategies, optimize_strategy, run_portfolio_mode, run_strategy
from ui import (
    apply_theme,
    render_analytics_tab,
    render_candles_chart,
    render_empty_state,
    render_equity_chart,
    render_header,
    render_kpi_cards,
    render_login_screen,
    render_logs_tab,
    render_trades_tab,
)


st.set_page_config(
    page_title="QuantView Terminal",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()
dbm.init_db()

COOKIE_SECRET = os.getenv("TRADING_APP_COOKIE_SECRET", "change-me-in-production")
cookies = EncryptedCookieManager(prefix="quantview", password=COOKIE_SECRET)
if not cookies.ready():
    st.stop()

if "logged_in" not in st.session_state:
    persisted_login = cookies.get("login") == "true"
    st.session_state.logged_in = persisted_login
    st.session_state.username = cookies.get("username") if persisted_login else ""

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "activity_log" not in st.session_state:
    st.session_state.activity_log = []


def append_log(message: str) -> None:
    st.session_state.activity_log.append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "message": message,
        }
    )
    st.session_state.activity_log = st.session_state.activity_log[-200:]


if not st.session_state.logged_in:
    auth_action = render_login_screen()
    if auth_action["action"] == "login":
        auth = dbm.authenticate_user(auth_action["username"], auth_action["password"])
        if auth.get("success") and auth.get("is_approved"):
            cookies["login"] = "true"
            cookies["username"] = auth_action["username"]
            cookies.save()
            st.session_state.logged_in = True
            st.session_state.username = auth_action["username"]
            append_log(f"Operator {auth_action['username']} authenticated successfully.")
            st.rerun()
        st.error("Invalid credentials or account awaiting approval.")
    elif auth_action["action"] == "register":
        if dbm.register_user(auth_action["username"], auth_action["password"]):
            st.success("Registration submitted. Please wait for administrator approval.")
        else:
            st.error("That operator ID already exists.")
    st.stop()

with st.sidebar:
    st.markdown("### Market")
    portfolio_mode = st.toggle("Portfolio Mode", value=False)
    comparison_mode = st.toggle("Strategy Comparison", value=False)
    optimization_mode = st.toggle("Optimization Engine", value=False)
    replay_mode = st.toggle("Trade Replay", value=False)

    if portfolio_mode:
        selected_assets = st.multiselect(
            "Assets",
            DEFAULT_SYMBOLS,
            default=["BTC/USDT", "ETH/USDT", "SOL/USDT"],
        )
    else:
        selected_asset = st.selectbox("Asset", DEFAULT_SYMBOLS, index=0)
        selected_assets = [selected_asset]

    timeframe_label = st.selectbox("Timeframe", list(TIMEFRAME_OPTIONS.keys()), index=2)
    timeframe = TIMEFRAME_OPTIONS[timeframe_label]

    indicators = st.multiselect(
        "Indicators",
        ["RSI", "MACD"],
        default=["RSI", "MACD"],
    )
    ema_periods = st.multiselect(
        "EMA Overlay",
        [5, 8, 9, 13, 20, 21, 34, 50, 100, 200],
        default=[9, 21, 50],
    )

    st.markdown("### Strategy Parameters")
    col_a, col_b = st.columns(2)
    with col_a:
        fast_ema = st.number_input("Fast EMA", min_value=3, max_value=100, value=9, step=1)
        fee_bps = st.number_input("Fee (bps)", min_value=0.0, max_value=100.0, value=7.5, step=0.5)
        initial_capital = st.number_input("Capital", min_value=1000.0, max_value=1000000.0, value=10000.0, step=1000.0)
    with col_b:
        slow_ema = st.number_input("Slow EMA", min_value=5, max_value=250, value=21, step=1)
        slippage_bps = st.number_input("Slippage (bps)", min_value=0.0, max_value=100.0, value=2.0, step=0.5)
        benchmark = st.selectbox("Benchmark", ["Buy & Hold", "Flat"], index=0)

    comparison_fast = st.number_input("Compare Fast EMA", min_value=3, max_value=100, value=13, step=1)
    comparison_slow = st.number_input("Compare Slow EMA", min_value=5, max_value=250, value=34, step=1)

    optimization_short = st.slider("Optimize Fast EMA Range", min_value=3, max_value=30, value=(5, 15))
    optimization_long = st.slider("Optimize Slow EMA Range", min_value=16, max_value=120, value=(20, 60))

    run_clicked = st.button("Run Analysis", use_container_width=True, type="primary")

if run_clicked:
    append_log(
        f"Run started for {', '.join(selected_assets)} on {timeframe} with primary EMA pair {fast_ema}/{slow_ema}."
    )
    show_rsi = "RSI" in indicators
    show_macd = "MACD" in indicators

    if portfolio_mode:
        portfolio = run_portfolio_mode(
            symbols=selected_assets,
            timeframe=timeframe,
            ema_periods=ema_periods,
            fast_ema=fast_ema,
            slow_ema=slow_ema,
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            show_rsi=show_rsi,
            show_macd=show_macd,
        )
        primary_symbol = selected_assets[0] if selected_assets else DEFAULT_SYMBOLS[0]
        market_df = load_market_data(primary_symbol, timeframe)
        primary = run_strategy(
            df=market_df,
            symbol=primary_symbol,
            timeframe=timeframe,
            ema_periods=ema_periods,
            fast_ema=fast_ema,
            slow_ema=slow_ema,
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            show_rsi=show_rsi,
            show_macd=show_macd,
            benchmark=benchmark,
        )
    else:
        market_df = load_market_data(selected_assets[0], timeframe)
        primary = run_strategy(
            df=market_df,
            symbol=selected_assets[0],
            timeframe=timeframe,
            ema_periods=ema_periods,
            fast_ema=fast_ema,
            slow_ema=slow_ema,
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            show_rsi=show_rsi,
            show_macd=show_macd,
            benchmark=benchmark,
        )
        portfolio = None

    comparison = None
    if comparison_mode and not market_df.empty:
        comparison = compare_strategies(
            df=market_df,
            symbol=selected_assets[0],
            timeframe=timeframe,
            ema_periods=ema_periods,
            left_pair=(fast_ema, slow_ema),
            right_pair=(comparison_fast, comparison_slow),
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
            show_rsi=show_rsi,
            show_macd=show_macd,
            benchmark=benchmark,
        )

    optimization = None
    if optimization_mode and not market_df.empty:
        optimization = optimize_strategy(
            df=market_df,
            symbol=selected_assets[0],
            timeframe=timeframe,
            short_range=range(optimization_short[0], optimization_short[1] + 1),
            long_range=range(optimization_long[0], optimization_long[1] + 1),
            initial_capital=initial_capital,
            fee_bps=fee_bps,
            slippage_bps=slippage_bps,
        )

    st.session_state.analysis_results = {
        "primary": primary,
        "comparison": comparison,
        "optimization": optimization,
        "portfolio": portfolio,
        "portfolio_mode": portfolio_mode,
        "replay_mode": replay_mode,
        "selected_assets": selected_assets,
        "timeframe": timeframe,
    }
    append_log("Analysis completed and cached in session state.")

render_header(st.session_state.username)

results = st.session_state.analysis_results
if not results:
    render_empty_state()
    st.stop()

primary = results["primary"]
if primary["data"].empty:
    st.error("No market data returned from the exchange for the selected configuration.")
    st.stop()

render_kpi_cards(primary["kpis"], primary["summary"])
render_equity_chart(primary, results["portfolio"])
render_candles_chart(primary, replay_mode=results["replay_mode"])

tab_trades, tab_analytics, tab_logs = st.tabs(["Trades", "Analytics", "Logs"])
with tab_trades:
    render_trades_tab(primary, results["replay_mode"])
with tab_analytics:
    render_analytics_tab(
        primary=primary,
        comparison=results["comparison"],
        optimization=results["optimization"],
        portfolio=results["portfolio"],
    )
with tab_logs:
    render_logs_tab(st.session_state.activity_log, primary)

logout_col_a, logout_col_b = st.columns([8, 1])
with logout_col_b:
    if st.button("Logout", use_container_width=True):
        cookies["login"] = "false"
        cookies["username"] = ""
        cookies.save()
        st.session_state.logged_in = False
        st.session_state.username = ""
        append_log("Operator logged out.")
        st.rerun()
