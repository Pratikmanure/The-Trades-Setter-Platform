from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');
            :root {
                --bg: #0a0f18;
                --panel: #0f1724;
                --panel-2: #111c2d;
                --line: rgba(120, 145, 185, 0.18);
                --text: #edf3ff;
                --muted: #8a9bb8;
                --green: #16c784;
                --red: #ff5c5c;
                --blue: #2f81f7;
                --yellow: #ffcc66;
                --shadow: 0 22px 60px rgba(0,0,0,0.38);
            }
            .stApp {
                background: radial-gradient(circle at top right, rgba(47,129,247,0.08), transparent 20%), linear-gradient(180deg, #0a0f18 0%, #08111d 100%);
                color: var(--text);
                font-family: 'IBM Plex Sans', sans-serif;
            }
            footer {visibility: hidden;}
            div[data-testid='stSidebarNav'] {display: none;}
            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0c1320 0%, #101926 100%);
                border-right: 1px solid var(--line);
            }
            [data-testid="stSidebar"] .block-container {padding-top: 1.2rem;}
            .hero {
                padding: 1.5rem 1.75rem;
                border-radius: 24px;
                background: linear-gradient(135deg, rgba(18,29,47,0.98), rgba(10,16,28,0.98));
                border: 1px solid var(--line);
                box-shadow: var(--shadow);
                margin-bottom: 1rem;
            }
            .eyebrow {
                color: #79a8ff;
                letter-spacing: 0.18em;
                text-transform: uppercase;
                font-size: 0.72rem;
                font-weight: 700;
            }
            .hero h1, h2, h3 {font-family: 'Space Grotesk', sans-serif; color: var(--text);}
            .hero-title {font-size: 2.25rem; margin: 0.35rem 0;}
            .hero-subtitle {color: var(--muted); max-width: 850px;}
            .kpi-card {
                background: linear-gradient(180deg, #101a2a 0%, #0e1624 100%);
                border: 1px solid var(--line);
                border-radius: 20px;
                padding: 0.95rem 1rem;
                box-shadow: var(--shadow);
            }
            .kpi-note {color: var(--muted); font-size: 0.82rem; margin-top: 0.35rem;}
            .panel {
                background: linear-gradient(180deg, rgba(14,22,36,0.96), rgba(11,18,30,0.96));
                border-radius: 22px;
                border: 1px solid var(--line);
                box-shadow: var(--shadow);
                padding: 1rem 1rem 0.25rem;
                margin-bottom: 1rem;
            }
            .mini-grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.8rem;
                margin-top: 1rem;
            }
            .mini-box {
                padding: 0.9rem 1rem;
                border-radius: 18px;
                background: rgba(255,255,255,0.02);
                border: 1px solid var(--line);
            }
            .mini-label {color: var(--muted); font-size: 0.78rem;}
            .mini-value {font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; margin-top: 0.3rem;}
            .stButton > button {
                background: linear-gradient(135deg, #18355f, #285ea8);
                border: 1px solid rgba(109,146,216,0.28);
                color: white;
                border-radius: 14px;
                min-height: 2.9rem;
                font-weight: 700;
            }
            [data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
                background: rgba(255,255,255,0.03);
                border: 1px solid var(--line);
                border-radius: 14px;
                color: var(--text);
            }
            .stTabs [data-baseweb="tab-list"] {
                background: rgba(255,255,255,0.03);
                border: 1px solid var(--line);
                border-radius: 18px;
                padding: 0.35rem;
                gap: 0.45rem;
            }
            .stTabs [data-baseweb="tab"] {border-radius: 14px; color: var(--muted);}
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, rgba(47,129,247,0.18), rgba(95,162,255,0.10));
                color: var(--text) !important;
            }
            @media (max-width: 1100px) {
                .mini-grid {grid-template-columns: 1fr;}
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_login_screen() -> dict:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Quantitative Trading Platform</div>
            <h1 class="hero-title">QuantView Terminal</h1>
            <div class="hero-subtitle">Professional-grade market analytics, strategy research, and execution intelligence for systematic traders.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1.25, 1])
    action = {"action": None, "username": "", "password": ""}
    with col2:
        tabs = st.tabs(["Login", "Register"])
        with tabs[0]:
            username = st.text_input("Operator ID", key="login_user")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Access Platform", use_container_width=True, type="primary"):
                action = {"action": "login", "username": username, "password": password}
        with tabs[1]:
            username = st.text_input("New Operator ID", key="register_user")
            password = st.text_input("New Password", type="password", key="register_password")
            if st.button("Request Access", use_container_width=True):
                action = {"action": "register", "username": username, "password": password}
    return action


def render_header(username: str) -> None:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">TradingView-Style Quant Analytics</div>
            <h1 class="hero-title">QuantView Terminal</h1>
            <div class="hero-subtitle">Built for systematic traders who need clean signal research, high-density charting, portfolio diagnostics, and institutional-style analytics. Active operator: <strong>{username}</strong>.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="panel">
            <h3 style="margin-top:0;">Ready to Analyze</h3>
            <p style="color:#8a9bb8;">Choose an asset, timeframe, indicators, and strategy parameters from the sidebar, then run the analysis to populate the platform.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _metric_card(col, label: str, value: str, note: str) -> None:
    with col:
        st.markdown("<div class='kpi-card'>", unsafe_allow_html=True)
        st.metric(label, value)
        st.markdown(f"<div class='kpi-note'>{note}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def render_kpi_cards(kpis: dict, summary: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    _metric_card(c1, "Total Return", f"{kpis['total_return']:.2f}%", "Net strategy performance over the loaded sample.")
    _metric_card(c2, "Win Rate", f"{kpis['win_rate']:.2f}%", f"{summary.get('trade_count', 0)} completed trades.")
    _metric_card(c3, "Max Drawdown", f"{kpis['max_drawdown']:.2f}%", "Worst peak-to-trough equity decline.")
    _metric_card(c4, "Sharpe Ratio", f"{kpis['sharpe_ratio']:.2f}", f"Benchmark: {summary.get('benchmark_return', 0.0):.2f}%")

    st.markdown(
        f"""
        <div class="panel">
            <div class="mini-grid">
                <div class="mini-box"><div class="mini-label">Last Close</div><div class="mini-value">{summary.get('last_close', 0.0):,.2f}</div></div>
                <div class="mini-box"><div class="mini-label">Avg Profit</div><div class="mini-value">{summary.get('avg_profit', 0.0):.2f}%</div></div>
                <div class="mini-box"><div class="mini-label">Max Loss</div><div class="mini-value">{summary.get('max_loss', 0.0):.2f}%</div></div>
                <div class="mini-box"><div class="mini-label">Win / Loss Streak</div><div class="mini-value">{summary.get('max_win_streak', 0)} / {summary.get('max_loss_streak', 0)}</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_equity_chart(primary: dict, portfolio: dict | None) -> None:
    df = primary["data"]
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["equity_curve"], mode="lines", name="Strategy Equity", line=dict(color="#2f81f7", width=2.2), fill="tozeroy", fillcolor="rgba(47,129,247,0.14)"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["benchmark_curve"], mode="lines", name="Benchmark", line=dict(color="#7b8ba7", width=1.4, dash="dot")), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["drawdown"], mode="lines", name="Drawdown", line=dict(color="#ff5c5c", width=1.8), fill="tozeroy", fillcolor="rgba(255,92,92,0.16)"), row=2, col=1)
    if portfolio is not None and not portfolio["equity"].empty:
        fig.add_trace(go.Scatter(x=portfolio["equity"]["timestamp"], y=portfolio["equity"]["portfolio_equity"], mode="lines", name="Portfolio Equity", line=dict(color="#ffcc66", width=2.0)), row=1, col=1)
    fig.update_layout(title="Equity Curve and Drawdown", template="plotly_dark", height=520, margin=dict(l=10, r=10, t=48, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis=dict(showspikes=True, spikemode="across", spikesnap="cursor", spikethickness=1))
    fig.update_yaxes(gridcolor="rgba(138,155,184,0.12)")
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_candles_chart(primary: dict, replay_mode: bool = False) -> None:
    df = primary["data"].copy()
    if replay_mode and len(df) > 50:
        replay_idx = st.slider("Replay Position", min_value=50, max_value=len(df), value=len(df), step=1)
        df = df.iloc[:replay_idx].copy()

    has_rsi = df["rsi"].notna().any()
    has_macd = df["macd"].notna().any()
    rows = 2 + int(has_rsi) + int(has_macd)
    heights = [0.58, 0.16]
    if has_rsi:
        heights.append(0.14)
    if has_macd:
        heights.append(0.12)

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=heights, specs=[[{"secondary_y": False}] for _ in range(rows)])
    fig.add_trace(go.Candlestick(x=df["timestamp"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], name="Price", increasing_line_color="#16c784", decreasing_line_color="#ff5c5c"), row=1, col=1)

    ema_cols = [col for col in df.columns if col.startswith("ema_")]
    palette = ["#2f81f7", "#f4c542", "#14b8a6", "#a78bfa", "#f97316", "#94a3b8"]
    for idx, ema_col in enumerate(ema_cols):
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df[ema_col], mode="lines", name=ema_col.upper().replace("_", " "), line=dict(width=1.4, color=palette[idx % len(palette)])), row=1, col=1)

    buys = df[df["trade_trigger"] > 0]
    sells = df[df["trade_trigger"] < 0]
    fig.add_trace(go.Scatter(x=buys["timestamp"], y=buys["low"] * 0.995, mode="markers", name="Buy", marker=dict(symbol="triangle-up", size=11, color="#16c784")), row=1, col=1)
    fig.add_trace(go.Scatter(x=sells["timestamp"], y=sells["high"] * 1.005, mode="markers", name="Sell", marker=dict(symbol="triangle-down", size=11, color="#ff5c5c")), row=1, col=1)

    volume_colors = np.where(df["close"] >= df["open"], "#1f9d6a", "#b34747")
    fig.add_trace(go.Bar(x=df["timestamp"], y=df["volume"], marker_color=volume_colors, name="Volume", opacity=0.7), row=2, col=1)

    current_row = 3
    if has_rsi:
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["rsi"], mode="lines", name="RSI", line=dict(color="#2f81f7", width=1.7)), row=current_row, col=1)
        fig.add_hline(y=70, line=dict(color="#ff5c5c", dash="dot", width=1), row=current_row, col=1)
        fig.add_hline(y=30, line=dict(color="#16c784", dash="dot", width=1), row=current_row, col=1)
        current_row += 1
    if has_macd:
        hist_colors = np.where(df["macd_hist"] >= 0, "#16c784", "#ff5c5c")
        fig.add_trace(go.Bar(x=df["timestamp"], y=df["macd_hist"], marker_color=hist_colors, name="MACD Hist"), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["macd"], mode="lines", name="MACD", line=dict(color="#ffcc66", width=1.5)), row=current_row, col=1)
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["macd_signal"], mode="lines", name="Signal", line=dict(color="#c084fc", width=1.4)), row=current_row, col=1)

    fig.update_layout(title="TradingView-Style Market Structure", template="plotly_dark", height=860, margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hovermode="x unified", xaxis_rangeslider_visible=False, legend=dict(orientation="h", yanchor="bottom", y=1.01, xanchor="right", x=1))
    fig.update_xaxes(showgrid=False, showspikes=True, spikemode="across", spikesnap="cursor", spikethickness=1)
    fig.update_yaxes(gridcolor="rgba(138,155,184,0.12)", zeroline=False)
    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


def render_trades_tab(primary: dict, replay_mode: bool) -> None:
    trades = primary["trades"]
    if replay_mode:
        st.info("Replay mode is active. Use the replay slider above to simulate strategy evolution candle-by-candle.")
    col1, col2 = st.columns([1.4, 1])
    with col1:
        st.markdown("#### Trade Log")
        if trades.empty:
            st.info("No closed trades for the selected configuration.")
        else:
            display = trades.copy()
            display["entry_time"] = pd.to_datetime(display["entry_time"]).dt.strftime("%Y-%m-%d %H:%M")
            display["exit_time"] = pd.to_datetime(display["exit_time"]).dt.strftime("%Y-%m-%d %H:%M")
            numeric_cols = ["entry_price", "exit_price", "net_return_pct", "duration_minutes"]
            display[numeric_cols] = display[numeric_cols].round(3)
            st.dataframe(display, use_container_width=True, hide_index=True)
    with col2:
        st.markdown("#### SQL Insights")
        if primary["sql_insights"].empty:
            st.info("Trade insight queries will appear after completed trades are available.")
        else:
            st.dataframe(primary["sql_insights"], use_container_width=True, hide_index=True)


def render_analytics_tab(primary: dict, comparison: dict | None, optimization: dict | None, portfolio: dict | None) -> None:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Drawdown Distribution")
        drawdown_fig = go.Figure()
        drawdown_fig.add_trace(go.Histogram(x=primary["data"]["drawdown"], marker_color="#ff5c5c", nbinsx=40, opacity=0.8))
        drawdown_fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(drawdown_fig, use_container_width=True)
    with c2:
        st.markdown("#### Trade Return Distribution")
        trade_fig = go.Figure()
        returns = primary["trades"]["net_return_pct"] if not primary["trades"].empty else []
        trade_fig.add_trace(go.Histogram(x=returns, marker_color="#2f81f7", nbinsx=30, opacity=0.8))
        trade_fig.update_layout(template="plotly_dark", height=320, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(trade_fig, use_container_width=True)

    if comparison is not None:
        st.markdown("#### Strategy Comparison Mode")
        left_name = f"Primary EMA {comparison['left']['summary']['fast_ema']}/{comparison['left']['summary']['slow_ema']}"
        right_name = f"Comparison EMA {comparison['right']['summary']['fast_ema']}/{comparison['right']['summary']['slow_ema']}"
        left_col, right_col = st.columns(2)
        with left_col:
            st.markdown(f"**{left_name}**")
            st.dataframe(pd.DataFrame([comparison["left"]["kpis"]]), use_container_width=True, hide_index=True)
        with right_col:
            st.markdown(f"**{right_name}**")
            st.dataframe(pd.DataFrame([comparison["right"]["kpis"]]), use_container_width=True, hide_index=True)
        st.dataframe(comparison["diff"].round(3), use_container_width=True, hide_index=True)

    if optimization is not None:
        st.markdown("#### Strategy Optimization Engine")
        if optimization["pivot"].empty:
            st.info("Optimization did not produce valid EMA combinations.")
        else:
            heatmap = go.Figure(data=go.Heatmap(z=optimization["pivot"].values, x=optimization["pivot"].columns, y=optimization["pivot"].index, colorscale="RdYlGn", colorbar=dict(title="Return %")))
            heatmap.update_layout(template="plotly_dark", height=440, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(heatmap, use_container_width=True)
            st.dataframe(optimization["raw"].sort_values("total_return", ascending=False).head(20).round(3), use_container_width=True, hide_index=True)

    if portfolio is not None:
        st.markdown("#### Portfolio Mode")
        if portfolio["summary"].empty:
            st.info("Portfolio results are unavailable for the selected assets.")
        else:
            st.dataframe(portfolio["summary"].round(3), use_container_width=True, hide_index=True)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=portfolio["equity"]["timestamp"], y=portfolio["equity"]["portfolio_equity"], mode="lines", line=dict(color="#ffcc66", width=2), name="Portfolio Equity"))
            fig.add_trace(go.Scatter(x=portfolio["equity"]["timestamp"], y=portfolio["equity"]["portfolio_drawdown"], mode="lines", line=dict(color="#ff5c5c", width=1.7), name="Portfolio Drawdown", yaxis="y2"))
            fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=30, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis2=dict(overlaying="y", side="right", showgrid=False))
            st.plotly_chart(fig, use_container_width=True)


def render_logs_tab(activity_log: list[dict], primary: dict) -> None:
    st.markdown("#### System Activity")
    if activity_log:
        st.dataframe(pd.DataFrame(activity_log[::-1]), use_container_width=True, hide_index=True)
    else:
        st.info("No application events logged in this session yet.")

    st.markdown("#### Strategy Events")
    if primary["event_log"].empty:
        st.info("No strategy events available.")
    else:
        st.dataframe(primary["event_log"], use_container_width=True, hide_index=True)
