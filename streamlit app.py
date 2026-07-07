"""
JCB 215 NXT FUEL MASTER — Live Fleet Fuel Savings
Deploy: push to GitHub with requirements.txt, then share via Streamlit Community Cloud.
"""

import datetime as dt
import time

import streamlit as st

# ----------------------------- config -----------------------------

st.set_page_config(
    page_title="JCB 215 NXT Fuel Master — Fleet Savings",
    page_icon="🟡",
    layout="wide",
)

JCB_YELLOW = "#F5A800"
INK = "#16191C"
PANEL = "#1E2226"
HAIRLINE = "#34373B"
OFF_WHITE = "#EDEBE4"
DIM = "#85878A"
GOOD = "#6FCF97"

COUNTRIES = [
    # name, units, ccy code, symbol, decimals, default USD rate (None = USD only)
    ("Indonesia", 271, "IDR", "Rp", 0, 16200.0),
    ("Philippines", 241, "PHP", "₱", 0, 58.0),
    ("Cambodia", 91, "KHR", "៛", 0, 4100.0),
    ("Thailand", 79, "THB", "฿", 2, 36.2),
    ("Papua New Guinea", 66, "PGK", "K", 2, 3.9),
    ("Malaysia", 63, "MYR", "RM", 2, 4.47),
    ("Vietnam", 37, "VND", "₫", 0, 25500.0),
    ("Taiwan", 28, "TWD", "NT$", 0, 32.3),
    ("Laos", 15, "LAK", "₭", 0, 21700.0),
    ("Other markets", 78, None, None, 0, None),
]

# ----------------------------- styling -----------------------------

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
    .stApp {{ background-color: {INK}; }}
    h1, h2, h3 {{ font-family: 'Oswald', sans-serif !important; text-transform: uppercase; color: {OFF_WHITE}; }}
    .fm-eyebrow {{
        font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.2em;
        text-transform: uppercase; color: {JCB_YELLOW}; margin-bottom: 4px;
    }}
    .fm-hero {{
        background: {PANEL}; border: 1px solid {HAIRLINE}; border-radius: 12px;
        padding: 26px; margin-bottom: 8px;
    }}
    .fm-big {{
        font-family: 'IBM Plex Mono', monospace; font-weight: 600;
        font-size: 64px; line-height: 1; color: {JCB_YELLOW};
    }}
    .fm-usd {{ font-family: 'IBM Plex Mono', monospace; font-size: 22px; color: {GOOD}; font-weight: 600; margin-top: 6px; }}
    .fm-label {{ font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: 0.14em;
        text-transform: uppercase; color: {DIM}; margin-bottom: 10px; }}
    .fm-card {{
        background: {PANEL}; border: 1px solid {HAIRLINE}; border-radius: 10px;
        padding: 14px 16px; margin-bottom: 10px;
    }}
    .fm-card .name {{ font-family: 'Oswald', sans-serif; font-weight: 700; text-transform: uppercase;
        font-size: 15px; color: {OFF_WHITE}; margin-bottom: 6px; }}
    .fm-card .row {{ font-family: 'IBM Plex Mono', monospace; font-size: 13px; color: {DIM};
        display: flex; justify-content: space-between; }}
    .fm-card .row b {{ color: {OFF_WHITE}; }}
    .fm-card .row.usd b {{ color: {GOOD}; }}
    .fm-pillars {{ font-family: 'Oswald', sans-serif; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.3em; color: {JCB_YELLOW}; font-size: 14px; text-align: center; margin: 18px 0; }}
    .fm-note {{ color: {DIM}; font-size: 12px; font-family: 'IBM Plex Mono', monospace; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------- sidebar: assumptions -----------------------------

with st.sidebar:
    st.markdown("### Assumptions")
    diesel_price = st.number_input("Diesel (USD / L)", value=1.00, min_value=0.0, step=0.01)
    l_per_hour = st.number_input("Litres saved / hr / unit", value=3.0, min_value=0.0, step=0.1)
    hours_per_day = st.number_input("Hours running / day", value=8.0, min_value=0.0, step=0.5)
    since_date = st.date_input("Fleet ramp start date", value=dt.date(2022, 1, 1))

    st.markdown("### Fleet units by market")
    units = {}
    for name, default_units, *_ in COUNTRIES:
        units[name] = st.number_input(name, value=default_units, min_value=0, step=1, key=f"u_{name}")

    st.markdown("### USD exchange rates")
    fx = {}
    for name, _, ccy, _, _, default_rate in COUNTRIES:
        if ccy:
            fx[name] = st.number_input(f"USD → {ccy}", value=float(default_rate), min_value=0.0, key=f"fx_{name}")

    auto_refresh = st.toggle("Auto-refresh (live ticker)", value=True)
    if st.button("↺ Reset live counter"):
        st.session_state.session_start = time.time()

# ----------------------------- state -----------------------------

if "session_start" not in st.session_state:
    st.session_state.session_start = time.time()

fleet_units = sum(units.values())
elapsed_hours = (time.time() - st.session_state.session_start) / 3600.0

# live session savings
session_litres = elapsed_hours * l_per_hour * fleet_units
session_usd = session_litres * diesel_price

# lifetime savings: linear sales ramp 0 -> fleet_units since start date
days_since = max(0.0, (dt.datetime.now() - dt.datetime.combine(since_date, dt.time())).total_seconds() / 86400.0)
daily_burn_per_unit = l_per_hour * hours_per_day
lifetime_litres = 0.5 * daily_burn_per_unit * fleet_units * days_since
lifetime_usd = lifetime_litres * diesel_price

# ----------------------------- layout -----------------------------

st.markdown('<div class="fm-eyebrow">JCB 215 NXT Fuel Master · Live</div>', unsafe_allow_html=True)
st.title("Fuel Master. Do more for less.")
st.markdown(
    '<p class="fm-note">JCB Inteli control ensures the best work done to fuel used ratio — '
    "saving 3.0 L/hr against the standard-cycle baseline, across every Fuel Master at work.</p>",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="fm-hero">
            <div class="fm-label">Live session savings — {fleet_units} units</div>
            <div class="fm-big">{session_litres:,.3f} <span style="font-size:24px;color:{DIM}">L</span></div>
            <div class="fm-usd">${session_usd:,.2f} USD equivalent</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="fm-hero">
            <div class="fm-label">Lifetime savings — since {since_date.strftime('%b %Y')}</div>
            <div class="fm-big">{lifetime_litres:,.0f} <span style="font-size:24px;color:{DIM}">L</span></div>
            <div class="fm-usd">${lifetime_usd:,.2f} USD equivalent</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f'<p class="fm-note">Lifetime figure assumes fleet sales ramped linearly from 0 units on the start date '
    f"to today's {fleet_units} units, each running {hours_per_day:g} hrs/day since its estimated sale date.</p>",
    unsafe_allow_html=True,
)

st.markdown("## Savings by market")

cols = st.columns(5)
for i, (name, _, ccy, symbol, decimals, _) in enumerate(COUNTRIES):
    u = units[name]
    c_litres = 0.5 * daily_burn_per_unit * u * days_since
    c_usd = c_litres * diesel_price
    local_row = ""
    if ccy:
        local_val = c_usd * fx[name]
        local_row = (
            f'<div class="row"><span>{ccy}</span>'
            f"<b>{symbol} {local_val:,.{decimals}f}</b></div>"
        )
    with cols[i % 5]:
        st.markdown(
            f"""
            <div class="fm-card">
                <div class="name">{name}</div>
                <div class="row"><span>Units</span><b>{u}</b></div>
                <div class="row"><span>Litres</span><b>{c_litres:,.0f}</b></div>
                {local_row}
                <div class="row usd"><span>USD</span><b>${c_usd:,.0f}</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div class="fm-pillars">Tough &nbsp;·&nbsp; Efficient &nbsp;·&nbsp; Connected</div>', unsafe_allow_html=True)
st.markdown(
    '<p class="fm-note" style="text-align:center">Fleet counts from Asia serial-number distribution. '
    "Diesel prices and FX rates are editable assumptions in the sidebar, not live market feeds.</p>",
    unsafe_allow_html=True,
)

# ----------------------------- live refresh -----------------------------

if auto_refresh:
    time.sleep(1)
    st.rerun()
