from __future__ import annotations

import math
import re
import pandas as pd
from .data import METRIC_LABELS, normalize_metric

FINANCIAL_KEYS = list(METRIC_LABELS)

def build_history(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()
    financial = data[data.metric_key.isin(FINANCIAL_KEYS)]
    wide = financial.pivot_table(index=["company", "period"], columns="metric_key", values="value", aggfunc="first").reset_index()
    wide.columns.name = None
    for key in FINANCIAL_KEYS:
        if key not in wide:
            wide[key] = float("nan")
    wide["gross_margin_pct"] = (wide.gross_profit / wide.revenue * 100).where(wide.revenue.notna() & (wide.revenue != 0))
    wide["operating_margin_pct"] = (wide.operating_income / wide.revenue * 100).where(wide.revenue.notna() & (wide.revenue != 0))
    wide["net_margin_pct"] = (wide.net_income / wide.revenue * 100).where(wide.revenue.notna() & (wide.revenue != 0))
    wide["free_cash_flow"] = wide.operating_cash_flow - wide.capital_expenditure
    wide = wide.sort_values(["company", "period"], kind="stable")
    wide["revenue_growth_pct"] = float("nan")
    quarterly = wide[wide.revenue.notna()].copy()
    previous_revenue = quarterly.groupby("company").revenue.shift(1)
    wide.loc[quarterly.index, "revenue_growth_pct"] = ((quarterly.revenue / previous_revenue - 1) * 100).where(previous_revenue > 0)
    wide["period"] = wide.period.astype(str)
    ordered = ["company", "period", "revenue", "revenue_growth_pct", "gross_profit", "gross_margin_pct", "operating_income", "operating_margin_pct", "net_income", "net_margin_pct", "operating_cash_flow", "capital_expenditure", "free_cash_flow", "consolidated_adjusted_ebitda", "cash_and_equivalents", "total_debt", "shares_outstanding", "market_cap"]
    return wide[ordered].sort_values(["company", "period"], kind="stable").reset_index(drop=True)

def analyst_summary(history: pd.DataFrame, companies: list[str], source_data: pd.DataFrame) -> str:
    if history.empty:
        return "Add sourced financial rows to produce a comparison."
    lines = []
    stats = {}
    for company in companies:
        subset = history[history.company == company].sort_values("period")
        rev = subset[subset.revenue.notna()]
        op = subset[subset.operating_income.notna()]
        if rev.empty:
            lines.append(f"**{company}:** no revenue rows are available, so growth and scale cannot be assessed.")
            continue
        latest = rev.iloc[-1]
        first = rev.iloc[0]
        growth = latest.revenue / first.revenue - 1 if len(rev) > 1 and first.revenue > 0 else None
        margin = latest.operating_margin_pct if pd.notna(latest.operating_margin_pct) else None
        stats[company] = (latest.revenue, margin)
        bits = [f"latest reported revenue is {latest.revenue:,.2f} ({latest.period})"]
        if growth is not None:
            bits.append(f"revenue changed {growth:+.1%} across the available periods")
        else:
            bits.append("a multi-period growth rate is unavailable")
        bits.append(f"operating margin is {margin:.1f}%" if margin is not None else "operating margin is unavailable")
        lines.append(f"**{company}:** " + "; ".join(bits) + ".")
    if len(stats) == 2:
        a, b = companies
        if stats[a][0] != stats[b][0]:
            lines.append(f"Reported revenue scale differs ({a}: {stats[a][0]:,.2f}; {b}: {stats[b][0]:,.2f}). Confirm currency, fiscal period length, and metric definitions before treating the values as directly comparable.")
        if stats[a][1] is not None and stats[b][1] is not None:
            lines.append(f"Operating margin spread is {stats[a][1] - stats[b][1]:+.1f} percentage points ({a} less {b}).")
    missing = []
    for key, label in [("operating_cash_flow", "operating cash flow"), ("capital_expenditure", "capital expenditure"), ("total_debt", "debt"), ("cash_and_equivalents", "cash"), ("market_cap", "market capitalization"), ("shares_outstanding", "shares outstanding")]:
        if not (source_data.metric_key == key).any():
            missing.append(label)
    if missing:
        lines.append("Open questions: provide " + ", ".join(missing) + " to assess cash generation and net debt more fully.")
    return "\n\n".join(lines)

def swiggy_eternal_summary(data: pd.DataFrame) -> str:
    """Build a filing-based readout for the preloaded Swiggy and Eternal case."""
    if data.empty:
        return "No sourced rows are available for the selected companies."
    companies = set(data.company.unique())
    swiggy, eternal = "Swiggy Limited", "Eternal Limited"
    if not {swiggy, eternal}.issubset(companies):
        return ""

    def value(company: str, period: str, metric: str) -> float | None:
        rows = data[(data.company == company) & (data.period == period) & (data.metric.map(normalize_metric) == normalize_metric(metric))]
        return float(rows.iloc[0].value) if not rows.empty else None

    def money(amount: float) -> str:
        return f"-₹{abs(amount):,.0f}" if amount < 0 else f"₹{amount:,.0f}"

    q2_26, q1_27, q2_27 = "2025-09-30 Q2 FY26", "2026-06-30 Q1 FY27", "2026-09-30 Q2 FY27"
    s_rev_old, s_rev = value(swiggy, q2_26, "Revenue"), value(swiggy, q2_27, "Revenue")
    e_rev_old, e_rev = value(eternal, q2_26, "Revenue"), value(eternal, q2_27, "Revenue")
    s_pat_old, s_pat = value(swiggy, q2_26, "Net income"), value(swiggy, q2_27, "Net income")
    e_pat_old, e_pat = value(eternal, q2_26, "Net income"), value(eternal, q2_27, "Net income")
    e_adj_rev_old, e_adj_rev = value(eternal, q2_26, "Adjusted Revenue"), value(eternal, q2_27, "Adjusted Revenue")
    e_lfl_growth = value(eternal, q2_27, "Adjusted Revenue LFL growth")
    if None in [s_rev_old, s_rev, e_rev_old, e_rev, s_pat_old, s_pat, e_pat_old, e_pat]:
        return "The Q2 FY27 case data is incomplete. Review the source rows before relying on the comparison."

    s_growth, e_growth = s_rev / s_rev_old - 1, e_rev / e_rev_old - 1
    e_profit_growth = e_pat / e_pat_old - 1
    s_loss_yoy = abs(s_pat_old) - abs(s_pat)
    s_q1_pat = value(swiggy, q1_27, "Net income")
    s_loss_qoq = abs(s_pat) - abs(s_q1_pat) if s_q1_pat is not None else 0
    instamart_nov = value(swiggy, q2_27, "Instamart NOV")
    blinkit_nov = value(eternal, q2_27, "Quick Commerce NOV")
    instamart_ebitda = value(swiggy, q2_27, "Instamart Adjusted EBITDA")
    blinkit_ebitda = value(eternal, q2_27, "Quick Commerce Adjusted EBITDA")
    s_food = value(swiggy, q2_27, "Food Delivery Adjusted EBITDA")
    e_food = value(eternal, q2_27, "Food Delivery Adjusted EBITDA")
    s_food_margin = value(swiggy, q2_27, "Food Delivery Adjusted EBITDA margin")
    e_food_margin = value(eternal, q2_27, "Food Delivery Adjusted EBITDA margin")
    s_cfo = value(swiggy, "H1 FY27 ended 2026-09-30", "Operating cash flow")
    e_cfo = value(eternal, "H1 FY27 ended 2026-09-30", "Operating cash flow")

    if e_adj_rev_old not in (None, 0) and e_adj_rev is not None and e_lfl_growth is not None:
        adjusted_note = f" Eternal's company-defined adjusted revenue grew {(e_adj_rev / e_adj_rev_old - 1):.1%}; like-for-like adjusted revenue growth was {e_lfl_growth:.0f}%. The company attributes the gap to moving quick commerce toward inventory ownership."
    else:
        adjusted_note = " Eternal says quick commerce moving toward inventory ownership affects reported revenue comparability."
    result = [
        f"**Top line:** Q2 FY27 revenue from operations grew {s_growth:.1%} year over year at Swiggy and {e_growth:.1%} at Eternal.{adjusted_note}",
        f"**Earnings:** Eternal reported profit of ₹{e_pat:,.0f} crore, up {e_profit_growth:.0%} year over year. Swiggy's net loss narrowed by ₹{s_loss_yoy:,.0f} crore year over year to ₹{abs(s_pat):,.0f} crore, but widened by ₹{s_loss_qoq:,.0f} crore from Q1 FY27.",
    ]
    if None not in [instamart_nov, blinkit_nov, instamart_ebitda, blinkit_ebitda]:
        result.append(f"**Quick commerce:** Blinkit reported NOV of {money(blinkit_nov)} crore and adjusted EBITDA of {money(blinkit_ebitda)} crore. Instamart reported NOV of {money(instamart_nov)} crore and adjusted EBITDA of {money(instamart_ebitda)} crore. The NOV figures are company-defined operating metrics; review the source definitions before treating them as directly comparable.")
    if s_food is not None and e_food is not None and s_food_margin is not None and e_food_margin is not None:
        result.append(f"**Food delivery:** Swiggy reported adjusted EBITDA of ₹{s_food:,.0f} crore at {s_food_margin:.1f}% of GOV. Eternal reported ₹{e_food:,.0f} crore at {e_food_margin:.1f}% of NOV. Their margin denominators differ, so the percentage margins are not directly comparable.")
    if s_cfo is not None and e_cfo is not None:
        result.append(f"**Cash conversion:** first-half operating cash flow was {money(s_cfo)} crore at Swiggy and {money(e_cfo)} crore at Eternal. The period is six months, not a single quarter. Eternal's filing shows sizeable working-capital movements, so the positive figure merits a closer bridge from earnings to cash.")
    result.append("**Open checks:** compare order-value definitions, the impact of inventory ownership on reported revenue, quick-commerce unit economics after store maturation, working-capital requirements, and the basis of each company's adjusted EBITDA. These results describe operating performance and do not imply a buy or sell view.")
    return "\n\n".join(result)

def build_forecast(history: pd.DataFrame, companies: list[str], assumptions: dict, scenarios: dict, years: int, scenario: str) -> pd.DataFrame:
    rows = []
    mods = scenarios or {"Base": (1.0, 0.0), "Upside": (1.25, 0.03), "Downside": (0.7, -0.04)}
    growth_mult, margin_delta = mods[scenario]
    for company in companies:
        subset = history[(history.company == company) & history.revenue.notna()].sort_values("period")
        if subset.empty:
            continue
        quarterly = subset.period.astype(str).str.contains(r"Q[1-4] FY", case=False).all()
        if quarterly:
            if len(subset) < 4:
                continue
            base = float(subset.tail(4).revenue.sum())
            base_period = "LTM through " + str(subset.iloc[-1].period)
        else:
            base = float(subset.iloc[-1].revenue)
            base_period = str(subset.iloc[-1].period)
        p = assumptions[company]
        for year in range(1, years + 1):
            revenue = base * (1 + p["growth"] * growth_mult) ** year
            margin = max(-1.0, min(1.0, p["op_margin"] + margin_delta))
            op_income = revenue * margin
            da = revenue * p["da_pct"]
            ebitda = op_income + da
            tax = max(op_income, 0) * p["tax"]
            capex = revenue * p["capex_pct"]
            nwc_investment = revenue * p["nwc_pct"]
            fcff = op_income - tax + da - capex - nwc_investment
            rows.append({"company": company, "period": f"{base_period} + {year}Y", "scenario": scenario, "revenue": revenue, "revenue_growth_pct": growth_mult * p["growth"] * 100, "operating_margin_pct": margin * 100, "operating_income": op_income, "depreciation_amortization": da, "ebitda_proxy": ebitda, "cash_taxes": tax, "capital_expenditure": capex, "change_in_nwc": nwc_investment, "unlevered_free_cash_flow": fcff, "classification": "Analyst assumption"})
    return pd.DataFrame(rows)

def _dcf(forecast: pd.DataFrame, p: dict, wacc: float | None = None, terminal_growth: float | None = None) -> tuple[float, float]:
    if forecast.empty:
        return math.nan, math.nan
    r = p["wacc"] if wacc is None else wacc
    g = p["terminal_growth"] if terminal_growth is None else terminal_growth
    if r <= g or r <= 0:
        return math.nan, math.nan
    cashflows = forecast.unlevered_free_cash_flow.astype(float).tolist()
    pv = sum(cf / ((1 + r) ** i) for i, cf in enumerate(cashflows, 1))
    terminal = cashflows[-1] * (1 + g) / (r - g)
    ev = pv + terminal / ((1 + r) ** len(cashflows))
    equity = ev - (p["debt"] - p["cash"])
    per_share = equity / p["shares"] if p["shares"] > 0 else math.nan
    return ev, per_share

def build_valuation(history: pd.DataFrame, forecast: pd.DataFrame, companies: list[str], assumptions: dict) -> pd.DataFrame:
    rows = []
    for company in companies:
        hist = history[(history.company == company)].sort_values("period")
        fc = forecast[forecast.company == company]
        p = assumptions[company].copy()
        for input_key, metric_key in [("shares", "shares_outstanding"), ("debt", "total_debt"), ("cash", "cash_and_equivalents"), ("market_cap", "market_cap")]:
            reported = hist[metric_key].dropna() if metric_key in hist else pd.Series(dtype=float)
            if p[input_key] <= 0 and not reported.empty:
                p[input_key] = float(reported.iloc[-1])
        revenue = hist.revenue.dropna()
        op = hist.operating_income.dropna()
        quarterly = hist[hist.revenue.notna()].period.astype(str).str.contains(r"Q[1-4] FY", case=False).all() if hist.revenue.notna().any() else False
        latest_revenue = float(revenue.tail(4).sum()) if quarterly and len(revenue) >= 4 else (float(revenue.iloc[-1]) if not quarterly and not revenue.empty else math.nan)
        latest_op = float(op.tail(4).sum()) if len(op) >= 4 else math.nan
        adjusted_rows = hist.consolidated_adjusted_ebitda.dropna() if "consolidated_adjusted_ebitda" in hist else pd.Series(dtype=float)
        adjusted_ebitda_ttm = float(adjusted_rows.tail(4).sum()) if quarterly and len(adjusted_rows) >= 4 else math.nan
        ev, per_share = _dcf(fc, p)
        market_cap = p["market_cap"]
        net_debt = p["debt"] - p["cash"]
        market_ev = market_cap + net_debt if market_cap > 0 else math.nan
        net_income = hist.net_income.dropna()
        ttm_net_income = float(net_income.tail(4).sum()) if len(net_income) >= 4 else math.nan
        rows.append({"Company": company, "Market cap (input)": market_cap if market_cap > 0 else "Unavailable", "P/S (TTM)": _multiple(market_cap, latest_revenue) if market_cap > 0 else "Unavailable", "EV / revenue (TTM)": _multiple(market_ev, latest_revenue), "EV / adjusted EBITDA (TTM)": _multiple(market_ev, adjusted_ebitda_ttm), "P/E (TTM)": _multiple(market_cap, ttm_net_income) if market_cap > 0 else "Unavailable", "DCF enterprise value": ev if math.isfinite(ev) else "Unavailable", "DCF equity value / share": per_share if math.isfinite(per_share) else "Unavailable", "Inputs": "Market cap estimated from quote and paid-up shares; debt assumption editable"})
    return pd.DataFrame(rows)

def _multiple(numerator: float, denominator: float) -> float | str:
    if not math.isfinite(numerator) or not math.isfinite(denominator):
        return "Unavailable"
    if denominator <= 0:
        return "Not meaningful"
    return numerator / denominator

def dcf_sensitivity(forecast: pd.DataFrame, company: str, assumptions: dict, history: pd.DataFrame | None = None) -> pd.DataFrame:
    fc = forecast[forecast.company == company]
    p = assumptions[company].copy()
    if history is not None:
        hist = history[history.company == company]
        for input_key, metric_key in [("shares", "shares_outstanding"), ("debt", "total_debt"), ("cash", "cash_and_equivalents")]:
            reported = hist[metric_key].dropna() if metric_key in hist else pd.Series(dtype=float)
            if p[input_key] <= 0 and not reported.empty:
                p[input_key] = float(reported.iloc[-1])
    rows = []
    for wacc in [0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13]:
        row = {"WACC": f"{wacc:.0%}"}
        for growth in [0.00, 0.01, 0.02, 0.03, 0.04]:
            _, value = _dcf(fc, p, wacc, growth)
            row[f"{growth:.0%}"] = value if math.isfinite(value) else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)
