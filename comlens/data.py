from __future__ import annotations

from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CASE_STUDY_PATH = ROOT / "data" / "swiggy_eternal_q2fy27.csv"
MARKET_SNAPSHOT_PATH = ROOT / "data" / "market_snapshot.csv"
REQUIRED = ["period", "company", "metric", "value", "unit", "source", "notes"]
OPTIONAL = ["metric_definition"]
METRIC_LABELS = {
    "revenue": "Revenue", "cost_of_revenue": "Cost of revenue", "gross_profit": "Gross profit",
    "operating_income": "Operating income", "net_income": "Net income", "operating_cash_flow": "Operating cash flow",
    "capital_expenditure": "Capital expenditure", "cash_and_equivalents": "Cash and equivalents",
    "total_debt": "Total debt", "shares_outstanding": "Shares outstanding", "market_cap": "Market capitalization",
    "depreciation_amortization": "Depreciation & amortization", "ebitda": "EBITDA",
    "consolidated_adjusted_ebitda": "Consolidated adjusted EBITDA",
}

def normalize_metric(value: str) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    aliases = {
        "market_capitalization": "market_cap", "market_capitalisation": "market_cap",
        "depreciation_and_amortization": "depreciation_amortization",
        "depreciation_and_amortisation": "depreciation_amortization",
        "cash_and_cash_equivalents": "cash_and_equivalents",
    }
    return aliases.get(key, key)

def validate_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    errors: list[str] = []
    missing = [col for col in REQUIRED if col not in frame.columns]
    if missing:
        return pd.DataFrame(), ["Missing required columns: " + ", ".join(missing)]
    data = frame.copy()
    for col in OPTIONAL:
        if col not in data.columns:
            data[col] = ""
    for col in ["period", "company", "metric", "unit", "source", "notes", "metric_definition"]:
        data[col] = data[col].fillna("").astype(str).str.strip()
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    blank = data[["period", "company", "metric", "unit", "source"]].eq("").any(axis=1)
    if blank.any():
        errors.append(f"{int(blank.sum())} row(s) lack a period, company, metric, unit, or source and were removed.")
        data = data[~blank]
    invalid = data["value"].isna()
    if invalid.any():
        errors.append(f"{int(invalid.sum())} row(s) have a missing or non-numeric value and were removed.")
        data = data[~invalid]
    data["metric_key"] = data["metric"].map(normalize_metric)
    duplicate = data.duplicated(["period", "company", "metric_key"], keep=False)
    if duplicate.any():
        errors.append(f"{int(duplicate.sum())} duplicate company/period/metric rows found. Keep one row per metric or reconcile duplicates before analysis.")
    return data.reset_index(drop=True), errors

def load_data(source) -> tuple[pd.DataFrame, list[str]]:
    if source is None:
        return pd.DataFrame(columns=REQUIRED + OPTIONAL + ["metric_key"]), []
    try:
        frame = pd.read_csv(source)
    except Exception as exc:
        return pd.DataFrame(), [f"Could not read the CSV: {exc}"]
    return validate_data(frame)
