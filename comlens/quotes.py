from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st

from .data import MARKET_SNAPSHOT_PATH

@st.cache_data(ttl=300, show_spinner=False)
def get_market_quotes() -> pd.DataFrame:
    """Return last market quotes, preferring Yahoo data newer than the saved source snapshot."""
    snapshot = pd.read_csv(MARKET_SNAPSHOT_PATH)
    snapshot["observed_at"] = pd.to_datetime(snapshot["quote_observed"], errors="coerce", utc=True)
    snapshot["market_source"] = snapshot["quote_source"]
    snapshot["quote_status"] = "Dated source snapshot"
    for idx, row in snapshot.iterrows():
        try:
            response = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{row.ticker}",
                params={"range": "5d", "interval": "1d"},
                headers={"User-Agent": "Mozilla/5.0"}, timeout=4,
            )
            response.raise_for_status()
            result = response.json()["chart"]["result"][0]
            meta = result["meta"]
            quote_time = datetime.fromtimestamp(int(meta["regularMarketTime"]), tz=ZoneInfo("Asia/Kolkata"))
            snapshot_time = row.observed_at.to_pydatetime() if pd.notna(row.observed_at) else datetime.min.replace(tzinfo=timezone.utc)
            if quote_time.astimezone(timezone.utc) > snapshot_time:
                snapshot.at[idx, "last_price"] = float(meta["regularMarketPrice"])
                snapshot.at[idx, "observed_at"] = pd.Timestamp(quote_time)
                snapshot.at[idx, "market_source"] = "Yahoo Finance delayed quote"
                snapshot.at[idx, "quote_status"] = "Latest market feed"
        except Exception:
            continue
    snapshot["estimated_market_cap_crore"] = snapshot.last_price * snapshot.paid_up_shares_crore
    return snapshot
