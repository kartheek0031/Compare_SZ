from __future__ import annotations

import streamlit as st
import pandas as pd
import html
import re

from comlens.analysis import build_history, build_valuation, build_forecast, analyst_summary, swiggy_eternal_summary
from comlens.data import CASE_STUDY_PATH, METRIC_LABELS, load_data
from comlens.quotes import get_market_quotes
from comlens.ui import inject_styles, render_metric_cards, render_sidebar

st.set_page_config(page_title="ComLens | Swiggy vs Eternal", page_icon="◉", layout="wide")
inject_styles()

st.markdown('<div class="eyebrow">Q2 FY27 COMPANY COMPARISON · DATA CUT 9 NOV 2026</div>', unsafe_allow_html=True)
st.title("ComLens")
st.markdown("<p class='lede'>Swiggy vs Eternal, the listed parent formerly known as Zomato. Business performance, unit economics, and valuation drivers.</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='brand-mark'>◉ <span>COMLENS</span></div>", unsafe_allow_html=True)
    st.markdown("### Start with data")
    uploaded = st.file_uploader("Upload company metrics", type=["csv"], help="Use the supplied template. One row per company, period, and metric.")
    use_case_study = st.toggle("Load sourced Swiggy vs Eternal case", value=uploaded is None, help="Q2 FY27 reported results and the latest dated quote snapshot.")
    if uploaded is not None:
        frame, errors = load_data(uploaded)
    elif use_case_study:
        frame, errors = load_data(CASE_STUDY_PATH)
    else:
        frame, errors = load_data(None)
    if errors:
        st.error("Data needs attention")
        for issue in errors[:8]:
            st.caption(f"• {issue}")
    company_options = sorted(frame["company"].dropna().unique().tolist()) if not frame.empty else []
    selected = render_sidebar(company_options)

if frame.empty or len(selected) < 2:
    st.markdown("<div class='empty-state'><div class='empty-icon'>↗</div><h3>Select the company pair</h3><p>Load the sourced Swiggy and Eternal case or upload a CSV with two companies and filing references.</p></div>", unsafe_allow_html=True)
    st.info("The starter CSV is included in the project data folder.")
    st.stop()

view = frame[frame["company"].isin(selected)].copy()
st.markdown("<div class='demo-banner'><strong>FILED DATA</strong><span>Latest results are unaudited Q2 FY27 statements for the quarter ended 30 Sep 2026. Quote snapshot dated 9 Nov 2026.</span></div>", unsafe_allow_html=True)

periods = sorted(view["period"].dropna().unique().tolist())
history = build_history(view)
summary = swiggy_eternal_summary(view) or analyst_summary(history, selected, view)

tab_overview, tab_financials, tab_forecast, tab_valuation, tab_data = st.tabs(["Overview", "Financials", "Forecast", "Valuation", "Data & methods"])

with tab_overview:
    st.subheader("At a glance")
    st.caption("Calculated from the sourced rows. Period, units, and reported definitions remain visible in Data & methods.")
    latest = history[history.revenue.notna()].groupby("company", as_index=False).tail(1) if not history.empty else history
    if not latest.empty:
        cols = st.columns(2)
        for idx, company in enumerate(selected):
            row = latest[latest.company == company]
            if row.empty:
                cols[idx].metric(company, "No revenue data")
            else:
                rec = row.iloc[0]
                revenue_row = view[(view.company == company) & (view.period.astype(str) == str(rec["period"])) & (view.metric_key == "revenue")]
                unit = revenue_row.iloc[0].unit if not revenue_row.empty else "unit in source rows"
                cols[idx].metric(company, f"{rec['revenue']:,.1f}" if rec["revenue"] is not None else "n/a", f"Revenue · {rec['period']} · {unit}")
    st.markdown("#### Analyst readout")
    safe_summary = html.escape(summary)
    safe_summary = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", safe_summary).replace("\n\n", "<br><br>")
    st.markdown(f"<div class='summary-card'>{safe_summary}</div>", unsafe_allow_html=True)
    if {"Swiggy Limited", "Eternal Limited"}.issubset(set(selected)):
        st.markdown("#### Market snapshot")
        if st.button("Refresh market quotes", key="refresh_market_quotes"):
            get_market_quotes.clear()
            st.rerun()
        quotes = get_market_quotes()
        quote_cols = st.columns(2)
        for i, company in enumerate(selected):
            quote = quotes[quotes.company == company]
            if quote.empty:
                quote_cols[i].metric(company, "Quote unavailable")
            else:
                q = quote.iloc[0]
                quote_cols[i].metric(company, f"₹{q.last_price:,.2f}", f"NSE · approx. market cap ₹{q.estimated_market_cap_crore:,.0f} Cr")
                quote_time = q.observed_at.tz_convert("Asia/Kolkata").strftime("%d %b %Y %H:%M IST") if q.quote_status == "Latest market feed" else q.quote_observed
                quote_cols[i].caption(f"{q.quote_status} · {quote_time} · share count uses paid-up capital; market cap is estimated")
        st.caption("Market prices can be delayed. The comparison uses the newest market-feed observation available, with a dated source snapshot as fallback.")
    st.markdown("#### Comparison notes")
    flags = view[view["notes"].fillna("").str.strip().ne("")][["company", "period", "metric", "notes"]].drop_duplicates()
    if flags.empty:
        st.caption("No analyst notes were supplied. Confirm metric definitions, fiscal year ends, and currency before comparing companies.")
    else:
        st.dataframe(flags, hide_index=True, use_container_width=True)

with tab_financials:
    st.subheader("Reported history and calculated ratios")
    st.caption("Growth uses the prior available period. Margins use reported revenue. Missing or zero denominators display as unavailable. Values retain each company's reported units; the source table lists units by row.")
    if history.empty:
        st.info("No recognized financial metrics found. Other uploaded metrics remain available in Data & methods.")
    else:
        import plotly.express as px
        metric_choice = st.selectbox("Chart metric", ["revenue", "gross_profit", "operating_income", "net_income", "operating_cash_flow", "free_cash_flow"], format_func=lambda k: METRIC_LABELS.get(k, k))
        chart_data = history[history[metric_choice].notna()]
        if not chart_data.empty:
            unit_key = "operating_cash_flow" if metric_choice == "free_cash_flow" else metric_choice
            unit_rows = view[view.metric_key == unit_key].groupby("company").unit.agg(lambda values: ", ".join(sorted(set(values))))
            chart_data = chart_data.copy()
            chart_data["series"] = chart_data.company.map(lambda name: f"{name} · {unit_rows.get(name, 'unit not supplied')}")
            unit_label = "; ".join(f"{name}: {unit_rows.get(name, 'unit not supplied')}" for name in selected)
            fig = px.line(chart_data, x="period", y=metric_choice, color="series", markers=True, labels={metric_choice: f"{METRIC_LABELS.get(metric_choice)} · {unit_label}", "period": "Period", "series": "Company and unit"}, color_discrete_sequence=["#176b5b", "#d28a43"])
            fig.update_layout(template="plotly_white", height=340, margin=dict(l=8, r=8, t=20, b=8), legend_title_text="Company", font=dict(family="Inter, sans-serif", color="#25342f"))
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(history, hide_index=True, use_container_width=True)
    st.markdown("#### Uploaded operating metrics")
    standard = set(METRIC_LABELS)
    custom = view[~view.metric_key.isin(standard)]
    if custom.empty:
        st.caption("No company-specific metrics uploaded yet. Add any metric as a row in the CSV, with its own unit, definition, source, and notes.")
    else:
        st.dataframe(custom[["company", "period", "metric", "value", "unit", "source", "metric_definition", "notes"]], hide_index=True, use_container_width=True)

with tab_forecast:
    st.subheader("Driver-based operating forecast")
    st.caption("Forecasts start from the latest four reported quarters of revenue. Each scenario applies annual revenue growth and operating margin assumptions; other lines are linked to revenue.")
    f_years = st.slider("Forecast years", 1, 10, 5)
    assumptions, scenarios = render_metric_cards(selected, key="fc", show_forecast=True)
    scenario = st.radio("Scenario", ["Base", "Upside", "Downside"], horizontal=True)
    forecast = build_forecast(history, selected, assumptions, scenarios, f_years, scenario)
    if forecast.empty:
        st.warning("Four quarters of revenue are required to establish an annual forecast base for both companies.")
    else:
        import plotly.express as px
        fig = px.line(forecast, x="period", y="revenue", color="company", markers=True, labels={"revenue": "Revenue (reported units)", "period": "Forecast period"}, color_discrete_sequence=["#176b5b", "#d28a43"])
        fig.update_layout(template="plotly_white", height=320, margin=dict(l=8, r=8, t=20, b=8))
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(forecast, hide_index=True, use_container_width=True)
        st.caption("Forecasts are analyst assumptions, not reported results. Forecast EBITDA proxy = operating income + D&A. Tax applies only when operating income is positive.")

with tab_valuation:
    st.subheader("Valuation workspace")
    st.caption("Illustrative model outputs depend on editable inputs. This is not investment advice or a buy/sell recommendation.")
    quote_rows = get_market_quotes()
    market_inputs = {}
    for company in selected:
        quote = quote_rows[quote_rows.company == company]
        if not quote.empty:
            market_inputs[company] = {"market_cap": float(quote.iloc[0].estimated_market_cap_crore), "shares": float(quote.iloc[0].paid_up_shares_crore)}
    val_assumptions, val_scenarios = render_metric_cards(selected, key="val", show_valuation=True, market_inputs=market_inputs)
    vf = build_forecast(history, selected, val_assumptions, val_scenarios, 5, "Base")
    valuation = build_valuation(history, vf, selected, val_assumptions)
    if valuation.empty:
        st.warning("Add at least four quarters of reported revenue to calculate TTM multiples and a DCF base.")
    else:
        st.dataframe(valuation, hide_index=True, use_container_width=True)
        st.markdown("#### DCF sensitivity · implied equity value per share")
        company = st.selectbox("Sensitivity company", selected)
        import plotly.express as px
        from comlens.analysis import dcf_sensitivity
        grid = dcf_sensitivity(vf, company, val_assumptions, history)
        if not grid.empty:
            fig = px.imshow(grid.set_index("WACC"), text_auto=".2f", aspect="auto", color_continuous_scale="YlGn", labels=dict(x="Terminal growth", y="WACC", color="Value / share"))
            fig.update_layout(height=340, margin=dict(l=8, r=8, t=20, b=8))
            st.plotly_chart(fig, use_container_width=True)
    with st.expander("Valuation inputs and definitions"):
        st.markdown("- DCF discounts forecast unlevered free cash flow at WACC and uses Gordon growth for terminal value.\n- Enterprise value = present value of explicit cash flows + present value of terminal value. Equity value = enterprise value less net debt.\n- Market cap and paid-up shares are seeded from the quote snapshot. Debt, cash, and operating assumptions remain editable. Lease liabilities are excluded from the debt input.\n- TTM revenue multiples use the latest four reported quarters. P/E is unavailable when four quarters of profit data are missing, and is not meaningful when TTM earnings are nonpositive.\n- DCF is sensitive to WACC, terminal growth, and operating assumptions. Use the sensitivity grid to inspect that range.")

with tab_data:
    st.subheader("Data & methods")
    st.markdown("Download starter files, inspect the rows used in this comparison, and review what is calculated versus assumed.")
    c1, c2, c3 = st.columns(3)
    c1.download_button("CSV data template", pd.DataFrame(columns=["period", "company", "metric", "value", "unit", "source", "notes", "metric_definition"]).to_csv(index=False), "comlens_data_template.csv", "text/csv")
    c2.download_button("Swiggy vs Eternal case CSV", load_data(CASE_STUDY_PATH)[0].drop(columns=["metric_key"]).to_csv(index=False), "swiggy_eternal_q2fy27.csv", "text/csv")
    from pathlib import Path
    dictionary = Path(__file__).parent / "DATA_DICTIONARY.md"
    methodology = Path(__file__).parent / "METHODOLOGY.md"
    c3.download_button("Data dictionary", dictionary.read_text(encoding="utf-8"), "comlens_data_dictionary.md", "text/markdown")
    st.download_button("Methodology note", methodology.read_text(encoding="utf-8"), "comlens_methodology.md", "text/markdown")
    st.download_button("Market quote snapshot", get_market_quotes().to_csv(index=False), "market_quote_snapshot.csv", "text/csv")
    st.markdown("#### Source rows in this comparison")
    st.dataframe(view[["period", "company", "metric", "value", "unit", "source", "notes", "metric_definition"]], hide_index=True, use_container_width=True)
    st.caption("Calculated metrics are derived in the app and are labeled in the tables. Forecast and valuation inputs are analyst assumptions.")

st.markdown("<div class='footer-note'>ComLens · Local analysis workspace · No recommendation implied</div>", unsafe_allow_html=True)
