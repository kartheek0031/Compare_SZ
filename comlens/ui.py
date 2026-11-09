from __future__ import annotations

import streamlit as st

DEFAULTS = {
    "growth": 0.08, "op_margin": 0.10, "tax": 0.25, "da_pct": 0.04,
    "capex_pct": 0.05, "nwc_pct": 0.02, "wacc": 0.10,
    "terminal_growth": 0.025, "shares": 0.0, "debt": 0.0,
    "cash": 0.0, "market_cap": 0.0,
}

def inject_styles() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --ink:#1c302a; --muted:#6d7b75; --line:#e4e9e5; --paper:#f7f9f6; --green:#176b5b; --amber:#d28a43; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
    .stApp { background:var(--paper); }
    [data-testid="stHeader"] { background:transparent; }
    [data-testid="stSidebar"] { background:#f0f4f0; border-right:1px solid var(--line); }
    [data-testid="stSidebar"] > div:first-child { padding-top:1.5rem; }
    h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; color:var(--ink); }
    h1 { font-size:2.65rem !important; font-weight:800 !important; margin-bottom:.2rem !important; }
    h2 { font-size:1.45rem !important; font-weight:700 !important; }
    h3 { font-size:1.08rem !important; font-weight:700 !important; }
    .eyebrow { color:var(--green); font-size:.67rem; font-weight:700; letter-spacing:.15em; margin:1.1rem 0 .35rem; }
    .lede { color:var(--muted); font-size:1rem; margin:0 0 1.3rem; }
    .brand-mark { color:var(--green); font-family:'Manrope',sans-serif; font-weight:800; letter-spacing:.12em; font-size:1rem; border-bottom:1px solid var(--line); padding-bottom:1.2rem; margin-bottom:1.4rem; }
    .brand-mark span { margin-left:.35rem; }
    .demo-banner { display:flex; gap:1rem; align-items:center; padding:.8rem 1rem; background:#fff6e8; border:1px solid #f0ddb9; border-radius:9px; color:#664718; font-size:.85rem; margin:.3rem 0 1.1rem; }
    .demo-banner strong { font-size:.68rem; letter-spacing:.1em; }
    .summary-card { white-space:pre-line; line-height:1.75; padding:1.2rem 1.35rem; background:#fff; border:1px solid var(--line); border-left:3px solid var(--green); border-radius:8px; margin:.4rem 0 1.2rem; }
    .empty-state { text-align:center; background:white; border:1px solid var(--line); border-radius:12px; padding:3rem 1.2rem; margin:2rem 0; }
    .empty-icon { font-size:2rem; color:var(--green); }
    .empty-state p { color:var(--muted); }
    .footer-note { color:#88948e; font-size:.75rem; border-top:1px solid var(--line); padding:1.2rem 0 2rem; margin-top:2rem; }
    [data-testid="stMetric"] { background:white; border:1px solid var(--line); padding:1rem; border-radius:8px; }
    [data-testid="stMetricLabel"] { color:var(--muted); }
    [data-testid="stTabs"] button { font-weight:600; }
    [data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:8px; overflow:hidden; }
    .stButton button, .stDownloadButton button { border-radius:7px; }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar(companies: list[str]) -> list[str]:
    defaults = companies[:2]
    if len(companies) < 2:
        st.caption("The comparison view needs at least two companies.")
    return st.multiselect("Companies", companies, default=defaults, max_selections=2, help="Choose exactly two companies to compare.")

def render_metric_cards(companies: list[str], key: str = "assumption", show_forecast: bool = False, show_valuation: bool = False, market_inputs: dict | None = None) -> tuple[dict, dict]:
    assumptions = {}
    if not companies:
        return assumptions, {}
    if show_forecast or show_valuation:
        with st.expander("Edit analyst assumptions", expanded=True):
            st.caption("These editable values are analyst assumptions. Enter market cap and share count, or provide them as sourced rows in the CSV. Keep market cap, debt, cash, and forecast amounts in the same currency and scale as the financial rows. Enter shares as a share count.")
            cols = st.columns(2)
            for i, company in enumerate(companies):
                with cols[i]:
                    st.markdown(f"**{company}**")
                    p = {}
                    market = (market_inputs or {}).get(company, {})
                    p["growth"] = st.number_input(f"Annual revenue growth · {company} (%)", -100.0, 300.0, DEFAULTS["growth"] * 100, 1.0, key=f"{key}_{i}_growth") / 100
                    p["op_margin"] = st.number_input(f"Operating margin · {company} (%)", -100.0, 100.0, DEFAULTS["op_margin"] * 100, 1.0, key=f"{key}_{i}_margin") / 100
                    p["tax"] = st.number_input(f"Tax rate · {company} (%)", 0.0, 100.0, DEFAULTS["tax"] * 100, 1.0, key=f"{key}_{i}_tax") / 100
                    p["da_pct"] = st.number_input(f"D&A / revenue · {company} (%)", 0.0, 100.0, DEFAULTS["da_pct"] * 100, 0.5, key=f"{key}_{i}_da") / 100
                    p["capex_pct"] = st.number_input(f"Capex / revenue · {company} (%)", 0.0, 200.0, DEFAULTS["capex_pct"] * 100, 0.5, key=f"{key}_{i}_capex") / 100
                    p["nwc_pct"] = st.number_input(f"Change in NWC / revenue · {company} (%)", -100.0, 100.0, DEFAULTS["nwc_pct"] * 100, 0.5, key=f"{key}_{i}_nwc") / 100
                    if show_valuation:
                        p["wacc"] = st.number_input(f"WACC · {company} (%)", 0.1, 100.0, DEFAULTS["wacc"] * 100, 0.5, key=f"{key}_{i}_wacc") / 100
                        p["terminal_growth"] = st.number_input(f"Terminal growth · {company} (%)", -10.0, 50.0, DEFAULTS["terminal_growth"] * 100, 0.25, key=f"{key}_{i}_tg") / 100
                        p["shares"] = st.number_input(f"Paid-up shares · {company} (crore shares)", 0.0, 1e12, float(market.get("shares", DEFAULTS["shares"])), 1.0, key=f"{key}_{i}_shares")
                        p["debt"] = st.number_input(f"Total debt · {company}", 0.0, 1e15, DEFAULTS["debt"], 1.0, key=f"{key}_{i}_debt")
                        p["cash"] = st.number_input(f"Cash · {company}", 0.0, 1e15, DEFAULTS["cash"], 1.0, key=f"{key}_{i}_cash")
                        p["market_cap"] = st.number_input(f"Market cap · {company} (₹ crore)", 0.0, 1e15, float(market.get("market_cap", DEFAULTS["market_cap"])), 1.0, key=f"{key}_{i}_marketcap")
                    else:
                        p.update({k: DEFAULTS[k] for k in ["wacc", "terminal_growth", "shares", "debt", "cash", "market_cap"]})
                    assumptions[company] = p
    else:
        assumptions = {c: DEFAULTS.copy() for c in companies}
    scenarios = {"Base": (1.0, 0.0), "Upside": (1.25, 0.03), "Downside": (0.7, -0.04)}
    if show_forecast:
        with st.expander("Scenario adjustments", expanded=False):
            st.caption("Multipliers apply to entered annual growth. Margin changes are percentage points added to the entered operating margin.")
            c1, c2, c3, c4 = st.columns(4)
            scenarios["Upside"] = (
                c1.number_input("Upside growth factor", 0.0, 5.0, 1.25, 0.05, key=f"{key}_up_growth"),
                c2.number_input("Upside margin change (pp)", -100.0, 100.0, 3.0, 0.5, key=f"{key}_up_margin") / 100,
            )
            scenarios["Downside"] = (
                c3.number_input("Downside growth factor", 0.0, 5.0, 0.70, 0.05, key=f"{key}_down_growth"),
                c4.number_input("Downside margin change (pp)", -100.0, 100.0, -4.0, 0.5, key=f"{key}_down_margin") / 100,
            )
    return assumptions, scenarios
