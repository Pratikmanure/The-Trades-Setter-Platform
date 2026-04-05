import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import data_engine as engine
from streamlit_cookies_manager import EncryptedCookieManager
import database_manager as dbm


st.set_page_config(
    page_title="Apex Quant Terminal",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

    :root {
        --bg: #07111f;
        --panel: rgba(8, 20, 38, 0.78);
        --panel-strong: rgba(11, 27, 51, 0.96);
        --panel-soft: rgba(18, 40, 72, 0.52);
        --border: rgba(120, 167, 255, 0.20);
        --text: #ebf2ff;
        --muted: #8ea6c9;
        --accent: #4cc9f0;
        --accent-2: #7c5cff;
        --success: #18c29c;
        --danger: #ff6b6b;
        --warning: #ffb703;
        --shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
        --radius: 22px;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(76, 201, 240, 0.16), transparent 28%),
            radial-gradient(circle at top right, rgba(124, 92, 255, 0.15), transparent 24%),
            linear-gradient(180deg, #08101c 0%, #07111f 42%, #050b13 100%);
        color: var(--text);
        font-family: 'IBM Plex Sans', sans-serif;
    }

    #MainMenu, header, footer {
        visibility: hidden;
    }

    div[data-testid='stSidebarNav'] {
        display: none;
    }

    [data-testid="stAppViewContainer"] > .main {
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(6, 15, 28, 0.98) 0%, rgba(10, 21, 39, 0.98) 100%);
        border-right: 1px solid rgba(135, 167, 235, 0.12);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif;
        letter-spacing: -0.03em;
        color: var(--text);
    }

    .hero-card {
        background:
            linear-gradient(135deg, rgba(15, 31, 58, 0.96), rgba(7, 18, 34, 0.98));
        border: 1px solid var(--border);
        border-radius: 28px;
        padding: 1.6rem 1.8rem;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
        margin-bottom: 1.1rem;
    }

    .hero-card::before {
        content: "";
        position: absolute;
        inset: auto -40px -60px auto;
        width: 180px;
        height: 180px;
        background: radial-gradient(circle, rgba(76, 201, 240, 0.20), transparent 68%);
    }

    .eyebrow {
        color: #8fb9ff;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    .hero-title {
        font-size: 2.3rem;
        line-height: 1;
        margin: 0;
    }

    .hero-subtitle {
        color: var(--muted);
        margin-top: 0.75rem;
        font-size: 1rem;
        max-width: 880px;
    }

    .top-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin-top: 1.2rem;
    }

    .strip-card, .glass-card, .login-shell, .section-card {
        background: var(--panel);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        backdrop-filter: blur(14px);
    }

    .strip-card {
        padding: 1rem 1.1rem;
    }

    .strip-label {
        color: var(--muted);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }

    .strip-value {
        margin-top: 0.45rem;
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--text);
    }

    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.1rem;
        margin-bottom: 0.75rem;
    }

    .section-card {
        padding: 1rem 1.1rem 1.25rem;
        margin-bottom: 1rem;
    }

    .metric-shell {
        background: linear-gradient(180deg, rgba(10, 25, 48, 0.92), rgba(7, 17, 31, 0.94));
        border: 1px solid rgba(114, 164, 255, 0.22);
        border-radius: 20px;
        padding: 0.95rem 1rem;
        min-height: 132px;
        box-shadow: var(--shadow);
    }

    .metric-shell [data-testid="stMetric"] {
        background: transparent;
        border: none;
        padding: 0;
    }

    .metric-shell label {
        color: var(--muted) !important;
        font-size: 0.76rem !important;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .metric-shell [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        color: var(--text);
    }

    .metric-footnote {
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 0.4rem;
    }

    .chart-shell {
        background: linear-gradient(180deg, rgba(9, 23, 43, 0.94), rgba(5, 14, 26, 0.96));
        border: 1px solid rgba(110, 160, 255, 0.18);
        border-radius: 24px;
        padding: 1rem 1rem 0.2rem;
        box-shadow: var(--shadow);
    }

    .mini-stat-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.9rem;
    }

    .mini-stat {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(145, 182, 255, 0.14);
        border-radius: 18px;
        padding: 0.9rem 1rem;
    }

    .mini-stat-label {
        color: var(--muted);
        font-size: 0.78rem;
        margin-bottom: 0.35rem;
    }

    .mini-stat-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.35rem;
        font-weight: 600;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        border-radius: 999px;
        padding: 0.45rem 0.8rem;
        border: 1px solid rgba(139, 191, 255, 0.18);
        background: rgba(255, 255, 255, 0.04);
        color: var(--text);
        font-size: 0.84rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }

    .login-shell {
        padding: 1.5rem;
        background:
            linear-gradient(145deg, rgba(10, 23, 42, 0.98), rgba(5, 12, 22, 0.98));
    }

    .login-title {
        margin: 0.2rem 0 0.45rem;
        font-size: 2.1rem;
    }

    .login-subtitle {
        color: var(--muted);
        margin-bottom: 1rem;
    }

    .sidebar-brand {
        padding: 1rem 1rem 1.15rem;
        border-radius: 22px;
        background: linear-gradient(145deg, rgba(18, 44, 82, 0.95), rgba(6, 15, 28, 0.98));
        border: 1px solid rgba(120, 177, 255, 0.16);
        margin-bottom: 1rem;
    }

    .sidebar-brand h3 {
        margin: 0;
    }

    .sidebar-brand p {
        color: var(--muted);
        margin: 0.45rem 0 0;
        font-size: 0.92rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.6rem;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(133, 170, 240, 0.14);
        border-radius: 18px;
        padding: 0.4rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 14px;
        padding: 0.7rem 1rem;
        color: var(--muted);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(76, 201, 240, 0.18), rgba(124, 92, 255, 0.18));
        color: var(--text) !important;
    }

    .stButton > button {
        border-radius: 14px;
        border: 1px solid rgba(130, 177, 255, 0.22);
        background: linear-gradient(135deg, #183760, #1b5fa7);
        color: white;
        font-weight: 600;
        min-height: 2.95rem;
    }

    .stDownloadButton > button,
    .stFormSubmitButton > button {
        border-radius: 14px;
    }

    .stSelectbox label, .stMultiSelect label, .stTextInput label {
        color: #d5e5ff !important;
        font-size: 0.88rem;
        font-weight: 600;
    }

    [data-baseweb="select"] > div,
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(132, 169, 235, 0.16);
        border-radius: 14px;
        color: var(--text);
    }

    .dataframe {
        border-radius: 16px;
        overflow: hidden;
    }

    @media (max-width: 1100px) {
        .top-strip, .mini-stat-grid {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 1.8rem;
        }
    }
</style>
""",
    unsafe_allow_html=True,
)

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


def pct_color(value):
    if value > 0:
        return "#18c29c"
    if value < 0:
        return "#ff6b6b"
    return "#8ea6c9"


def render_metric_card(column, label, value, footnote):
    with column:
        st.markdown("<div class='metric-shell'>", unsafe_allow_html=True)
        st.metric(label, value)
        st.markdown(f"<div class='metric-footnote'>{footnote}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ================= AUTHENTICATION =================
if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Institutional Trading Workspace</div>
            <h1 class="hero-title">Apex Quant Terminal</h1>
            <div class="hero-subtitle">
                A professional command surface for strategy analysis, operator authentication, and algorithmic execution oversight.
            </div>
            <div class="top-strip">
                <div class="strip-card">
                    <div class="strip-label">Signal Engine</div>
                    <div class="strip-value">EMA crossovers, RSI regime, portfolio simulation</div>
                </div>
                <div class="strip-card">
                    <div class="strip-label">Asset Coverage</div>
                    <div class="strip-value">Crypto, forex, commodities, and equities</div>
                </div>
                <div class="strip-card">
                    <div class="strip-label">Operator Access</div>
                    <div class="strip-value">Secure login, approval workflow, and session control</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([0.9, 1.4, 0.9])
    with col2:
        st.markdown("<div class='login-shell'>", unsafe_allow_html=True)
        st.markdown("<div class='eyebrow'>Secure Access</div>", unsafe_allow_html=True)
        st.markdown("<h2 class='login-title'>Operator Gateway</h2>", unsafe_allow_html=True)
        st.markdown(
            "<div class='login-subtitle'>Access the trading workspace or submit a registration request for administrator approval.</div>",
            unsafe_allow_html=True,
        )
        with st.container():
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
                        st.error("Access denied. The credentials are invalid or the account is still awaiting approval.")
            with tabs[1]:
                reg_u = st.text_input("Desired Operator ID", key="reg_user")
                reg_p = st.text_input("Secure Access Key", type="password", key="reg_pass")
                if st.button("Submit Node Registration", use_container_width=True):
                    if dbm.register_user(reg_u, reg_p):
                        st.success("Registration submitted successfully. An administrator will review the account shortly.")
                    else:
                        st.error("That operator ID already exists in the registry.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ================= SIDEBAR & ADMIN CONTROLS =================
with st.sidebar:
    st.markdown(
        f"""
        <div class="sidebar-brand">
            <div class="eyebrow">Apex Quant</div>
            <h3>Execution Console</h3>
            <p>Live strategy workspace for {st.session_state.username}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Market Controls")
    symbol = st.selectbox("Market Asset", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AAPL", "EURUSD=X", "GC=F"])
    tfs = {"1 Minute": "1m", "5 Minute": "5m", "15 Minute": "15m", "1 Hour": "1h", "4 Hour": "4h", "1 Day": "1d"}
    tf = tfs[st.selectbox("Data Timeframe", list(tfs.keys()), index=5)]
    emas = st.multiselect("EMA Matrix Computation", [5, 9, 13, 21, 50, 100, 200], default=[9, 21])

    st.markdown(
        """
        <div class="section-card">
            <div class="section-title">Session Snapshot</div>
            <div class="status-pill"><span class="status-dot" style="background:#18c29c;"></span> Authentication Active</div>
            <div class="status-pill"><span class="status-dot" style="background:#4cc9f0;"></span> Data Engine Cached</div>
            <div class="status-pill"><span class="status-dot" style="background:#ffb703;"></span> Manual Execution Trigger</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    run_btn = st.button("Execute Algorithm", use_container_width=True, type="primary")

    if st.session_state.username == "traderpratik":
        st.markdown("### Administrator Console")
        users_df = dbm.get_all_users()
        if not users_df.empty:
            pending_users = users_df[users_df['is_approved'] == 0]['username'].tolist()
            user_to_approve = st.selectbox("Pending Role Approvals", ["Select User"] + pending_users)
            if st.button("Grant Network Access") and user_to_approve != "Select User":
                dbm.approve_user(user_to_approve)
                st.success(f"Access granted to {user_to_approve}")
                st.rerun()
            st.caption(f"Pending approvals: {len(pending_users)}")
        else:
            st.caption("No pending operator approvals.")

    st.caption(f"Active session: {st.session_state.username}")
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

latest_close = float(df['close'].iloc[-1])
starting_close = float(df['close'].iloc[0])
price_change = ((latest_close / starting_close) - 1) * 100 if starting_close else 0.0
latest_signal = df['signal'].iloc[-1]
signal_label = "Bullish Bias" if latest_signal > 0 else "Defensive Bias"
signal_color = "#18c29c" if latest_signal > 0 else "#ff6b6b"
trigger_count = int((df['trade_trigger'].abs() == 2).sum())
latest_rsi = float(df['rsi'].dropna().iloc[-1]) if df['rsi'].notna().any() else 0.0
latest_timestamp = pd.to_datetime(df['timestamp'].iloc[-1]).strftime("%d %b %Y %H:%M")

st.markdown(
    f"""
    <div class="hero-card">
        <div class="eyebrow">Professional Trading Dashboard</div>
        <h1 class="hero-title">{symbol} Strategy Intelligence</h1>
        <div class="hero-subtitle">
            Monitoring <strong>{tf}</strong> execution conditions with an EMA stack of <strong>{", ".join(map(str, emas))}</strong>. 
            Last synchronized candle: <strong>{latest_timestamp}</strong>.
        </div>
        <div class="top-strip">
            <div class="strip-card">
                <div class="strip-label">Last Traded Price</div>
                <div class="strip-value">{latest_close:,.2f}</div>
            </div>
            <div class="strip-card">
                <div class="strip-label">Market Move</div>
                <div class="strip-value" style="color:{pct_color(price_change)};">{price_change:+.2f}% since window start</div>
            </div>
            <div class="strip-card">
                <div class="strip-label">Current Regime</div>
                <div class="strip-value" style="color:{signal_color};">{signal_label}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Quantitative Performance Metrics")
k1, k2, k3, k4 = st.columns(4)
render_metric_card(k1, "Gross Alpha Return", f"{kpi['total_return']:.2f}%", "Strategy return across the loaded history window.")
render_metric_card(k2, "Execution Win Rate", f"{kpi['win_rate']:.2f}%", "Positive return candles while the system is in market.")
render_metric_card(k3, "Max Capital Drawdown", f"{kpi['max_drawdown']:.2f}%", "Deepest simulated equity pullback from a local peak.")
render_metric_card(k4, "Sharpe Index", f"{kpi['sharpe_ratio']:.2f}", "Risk-adjusted efficiency of the simulated strategy stream.")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="section-card">
        <div class="section-title">Operational Snapshot</div>
        <div class="mini-stat-grid">
            <div class="mini-stat">
                <div class="mini-stat-label">Signal Transitions</div>
                <div class="mini-stat-value">{trigger_count}</div>
            </div>
            <div class="mini-stat">
                <div class="mini-stat-label">Latest RSI</div>
                <div class="mini-stat-value">{latest_rsi:.1f}</div>
            </div>
            <div class="mini-stat">
                <div class="mini-stat-label">Rows Analyzed</div>
                <div class="mini-stat-value">{len(df):,}</div>
            </div>
            <div class="mini-stat">
                <div class="mini-stat-label">Account Status</div>
                <div class="mini-stat-value">Approved</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

app_tabs = st.tabs(["Market Command", "Analytics Lab", "Signal Ledger"])

with app_tabs[0]:
    st.markdown("<div class='chart-shell'>", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price Action',
            increasing_line_color="#2dd4bf",
            decreasing_line_color="#ff6b6b",
        )
    )

    color_matrix = ['#2962FF', '#FF6D00', '#FFD700', '#00E676', '#D50000', '#FFFFFF', '#9E9E9E']
    for i, ema in enumerate(emas):
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df[f'ema_{ema}'],
                mode='lines',
                name=f'EMA {ema}',
                line=dict(width=1.8, color=color_matrix[i % len(color_matrix)]),
            )
        )

    buys, sells = df[df['trade_trigger'] == 2], df[df['trade_trigger'] == -2]
    fig.add_trace(
        go.Scatter(
            x=buys['timestamp'],
            y=buys['low'] * 0.99,
            mode='markers',
            marker=dict(symbol='triangle-up', size=12, color='#18c29c'),
            name='Algorithm BUY',
        )
    )
    fig.add_trace(
        go.Scatter(
            x=sells['timestamp'],
            y=sells['high'] * 1.01,
            mode='markers',
            marker=dict(symbol='triangle-down', size=12, color='#ff6b6b'),
            name='Algorithm SELL',
        )
    )

    fig.update_layout(
        template="plotly_dark",
        xaxis_rangeslider_visible=False,
        height=650,
        margin=dict(l=0, r=0, t=14, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis_title="Price",
        title="Price Action, EMA Structure, and Entry Markers",
        font=dict(family="IBM Plex Sans, sans-serif", color="#ebf2ff"),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(138, 166, 201, 0.12)", zeroline=False)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with app_tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='chart-shell'>", unsafe_allow_html=True)
        fig_eq = go.Figure()
        fig_eq.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['equity_curve'],
                fill='tozeroy',
                name='Equity',
                line=dict(color="#ffd166", width=2),
            )
        )
        fig_eq.update_layout(
            title="Simulated Portfolio Growth",
            template="plotly_dark",
            height=350,
            margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="IBM Plex Sans, sans-serif", color="#ebf2ff"),
        )
        fig_eq.update_xaxes(showgrid=False)
        fig_eq.update_yaxes(gridcolor="rgba(138, 166, 201, 0.12)")
        st.plotly_chart(fig_eq, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='chart-shell'>", unsafe_allow_html=True)
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df['timestamp'], y=df['rsi'], name='RSI', line=dict(color='#4cc9f0', width=2)))
        fig_rsi.add_hline(y=70, line_dash="dot", line_color="#D50000", line_width=1)
        fig_rsi.add_hline(y=30, line_dash="dot", line_color="#00E676", line_width=1)
        fig_rsi.update_layout(
            title="RSI Momentum Oscillation",
            template="plotly_dark",
            height=350,
            margin=dict(l=10, r=10, t=40, b=10),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family="IBM Plex Sans, sans-serif", color="#ebf2ff"),
        )
        fig_rsi.update_xaxes(showgrid=False)
        fig_rsi.update_yaxes(gridcolor="rgba(138, 166, 201, 0.12)")
        st.plotly_chart(fig_rsi, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with app_tabs[2]:
    trade_log = df.loc[df['trade_trigger'].abs() == 2, ['timestamp', 'close', 'trade_trigger', 'signal', 'rsi']].copy()
    if trade_log.empty:
        st.info("No signal transitions were generated for the current market window.")
    else:
        trade_log['event'] = np.where(trade_log['trade_trigger'] > 0, 'BUY transition', 'SELL transition')
        trade_log['bias'] = np.where(trade_log['signal'] > 0, 'Bullish', 'Bearish')
        trade_log['rsi'] = trade_log['rsi'].round(2)
        trade_log['close'] = trade_log['close'].round(2)
        trade_log = trade_log[['timestamp', 'event', 'bias', 'close', 'rsi']].sort_values('timestamp', ascending=False)

        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Signal Transition Ledger</div>", unsafe_allow_html=True)
        st.dataframe(trade_log, use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)
