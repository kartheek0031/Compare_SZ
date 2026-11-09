# ComLens

ComLens is a company comparison and valuation workspace. Its preloaded case compares Swiggy Limited with Eternal Limited, the listed parent formerly known as Zomato. The case uses public Q2 FY27 filings for the quarter ended September 30, 2026, plus a market quote snapshot dated November 9, 2026.

## Run locally

1. Install Python 3.10 or newer.
2. From this folder, create and activate a virtual environment if you want an isolated install.
3. Install dependencies with `python -m pip install -r requirements.txt`.
4. Start the dashboard with `streamlit run app.py`.

The app opens with the sourced Swiggy and Eternal case. Upload a CSV to analyze another pair. Download the case CSV or the blank input template from Data & methods.

## Data freshness

Financial results are the latest published results available when this case was prepared: Q2 FY27, unaudited, quarter ended September 30, 2026. Source URLs are attached to each row. Market quotes are checked against Yahoo Finance's NSE quote endpoint when the dashboard refreshes. The quote lookup is cached for five minutes and uses the supplied November 9, 2026 snapshot if the feed is unavailable or older. Quote feeds may be delayed. The page displays the timestamp and quote status.

The case file is a dated analysis snapshot, not a promise that filings or prices refresh automatically while the app is idle. Click the quote refresh control on the Overview tab to request a fresh quote. Refresh the filing CSV when newer results become available.

## What to look at

- The Overview readout compares revenue growth, earnings direction, quick commerce, food delivery, and first-half operating cash flow. It calls out accounting and metric definition differences.
- Financials shows reported quarterly history and calculated ratios. Uploaded company-specific metrics remain visible with their definitions and sources.
- Forecast uses a trailing twelve-month revenue base and editable annual operating assumptions. Base, upside, and downside cases are scenario analyses, not company guidance.
- Valuation shows market multiples, a driver-based DCF, and a WACC versus terminal growth sensitivity grid. Inputs are editable and labeled.
- Data & methods lists the source rows, CSV template, case data, data dictionary, and formulas.

## Add or refresh sourced data

Use one row per company, period, and metric based on `data/comlens_template.csv`. Include a source URL or filing reference, unit, reported metric definition, and any comparability notes. Use reported values as published. Do not map an adjusted company metric into a standard financial metric without stating its definition. The data dictionary lists recognized financial metrics and the columns the app uses.

## Limits

Swiggy's B2C GOV and Eternal's B2C NOV are different measures. Their food delivery margins use GOV and NOV, respectively. Eternal notes that quick commerce moving to inventory ownership raises reported revenue, so its reported revenue growth is not like-for-like with prior periods. The app preserves these measures and flags the distinctions rather than forcing them into a single definition.

The valuation model is a portfolio case study, not a recommendation. DCF results depend on editable assumptions and the reported debt, cash, and share basis. Market capitalization is estimated from the displayed quote and paid-up share count. Review source filings before using any output.
