# ComLens methodology

## Analysis date and sources

This case uses Swiggy and Eternal Q2 FY27 public results for the quarter ended September 30, 2026. Both companies describe these results as unaudited and reviewed. Source URLs appear on each reported row. The market quote snapshot is dated November 9, 2026; the dashboard prefers a newer Yahoo Finance NSE observation when available and shows its timestamp.

## Comparability notes

- Revenue from operations follows each company's consolidated Ind AS statements. Eternal reports that quick commerce shifting to inventory ownership increased reported revenue. Eternal disclosed 76% adjusted revenue growth and 58% like-for-like adjusted revenue growth for Q2 FY27. Revenue growth across this model transition should not be read as entirely organic growth.
- Swiggy's B2C GOV includes completed orders across food delivery, quick commerce, and out-of-home consumption, excluding Platform Innovations. Eternal's B2C NOV covers food delivery, quick commerce, and going-out. GOV and NOV have different discount treatment and are shown as reported.
- Swiggy Food Delivery adjusted EBITDA margin is divided by GOV. Eternal's Zomato food delivery adjusted EBITDA margin is divided by NOV. The percentages are not directly comparable.
- Adjusted EBITDA is a company-defined, non-GAAP measure. Swiggy and Eternal use different reconciliation rules. Segment figures remain in their own company definitions.
- Half-year cash flow rows cover April through September. They are not quarterly values. Cash and cash equivalents exclude other bank balances, investments, and lease liabilities.

## Historical calculations

- Sequential revenue growth = current reported quarter revenue / previous available quarter revenue − 1. The calculation is blank when the prior value is missing or nonpositive.
- Gross, operating, and net margin = corresponding reported profit / reported revenue. The ratio is blank when the numerator or revenue is missing, or revenue is zero.
- Free cash flow = operating cash flow − capital expenditure when both are supplied in the same period and basis. A partial period is not treated as zero.
- TTM revenue for quarterly data is the sum of the latest four reported quarters. It is used for revenue multiples and as the forecast base. If fewer than four quarters are present, TTM revenue is unavailable. For annual period data, the latest annual value is used.

## Forecast

The forecast starts from trailing twelve-month revenue. Each forecast year applies an editable annual revenue growth assumption. Operating income, D&A, capital expenditure, and working capital investment are modeled as percentages of revenue. Cash taxes equal the positive operating income times the entered tax rate. Unlevered free cash flow is operating income less cash taxes, plus D&A, less capital expenditure, less working capital investment.

Base uses the entered growth and margin assumptions. Upside and downside use editable growth factors and operating margin changes. They are scenario assumptions, not management guidance or probabilities.

## Discounted cash flow

- Present value of explicit forecast cash flows = sum of annual unlevered free cash flows discounted at WACC.
- Terminal value = final forecast year free cash flow × (1 + terminal growth) / (WACC − terminal growth).
- Enterprise value = present value of forecast cash flows + present value of terminal value.
- Equity value = enterprise value − debt + cash.
- Equity value per share = equity value / shares outstanding.

The model requires WACC greater than terminal growth and a positive share count. The sensitivity grid varies WACC from 7% to 13% and terminal growth from 0% to 4%. DCF is assumption-sensitive. Enter debt on a consistent basis and decide whether lease liabilities are included.

## Trading multiples and market capitalization

- P/S (TTM) = market capitalization / TTM revenue.
- EV / revenue (TTM) = (market capitalization + debt − cash) / TTM revenue.
- EV / adjusted EBITDA (TTM) = enterprise value / latest four quarters of company-reported consolidated adjusted EBITDA. This is a non-GAAP multiple and the two companies' adjustment definitions may differ. It is unavailable when four quarterly values are missing and not meaningful when TTM adjusted EBITDA is zero or negative.
- P/E (TTM) = market capitalization / TTM net income. It is unavailable when four quarters are not present, and not meaningful for a zero or negative denominator.
- Estimated market capitalization = latest share price × paid-up shares. Paid-up share count is not a fully diluted share count, so the estimate is not a precise live market capitalization.

The dashboard checks Yahoo Finance's NSE quote feed on rerun and caches results for five minutes. If the feed is unavailable or older than the supplied November 9, 2026 snapshot, it uses that dated snapshot. The quote may be delayed. The displayed timestamp and status identify which value is being used.

## Classification and limits

Reported data retains the source, period, unit, notes, and definition supplied in the case file. Historical ratios are calculated metrics. Forecast and valuation inputs are analyst assumptions. Company-defined adjusted results remain labeled as reported by the company. No output is a buy or sell recommendation.
