# ComLens data dictionary

The case CSV is long-form. Each row represents one company, period, and metric. The input template uses the same structure.

| Field | Required | Meaning | Example |
| --- | --- | --- | --- |
| `period` | Yes | Period end date and fiscal period. H1 rows are six-month periods. | `2026-09-30 Q2 FY27` |
| `company` | Yes | Company name used to group rows. | `Swiggy Limited` |
| `metric` | Yes | Reported financial metric or company-defined operating metric. | `Revenue` |
| `value` | Yes | Numeric amount. Do not include commas or currency symbols. | `7571` |
| `unit` | Yes | Currency, scale, or count unit. | `INR crore`, `percent of GOV`, `stores` |
| `source` | Yes | Filing, investor letter, or quote source URL. | Company filing URL |
| `notes` | Yes | Period status, accounting basis, caveat, or scope. | `Consolidated unaudited results` |
| `metric_definition` | No | Company-reported definition or an explanation of the value. | `Revenue from operations as reported under Ind AS` |

## Recognized financial metrics

| Metric | How ComLens uses it |
| --- | --- |
| Revenue | Historical revenue, growth, and TTM multiple denominator |
| Net income | Net margin and TTM P/E denominator when four quarters are available |
| Operating cash flow | Historical cash flow table; case values are six-month periods |
| Cash and equivalents | Cash input to the DCF and enterprise value estimate |
| Total debt | Debt input to enterprise value and DCF |
| Shares outstanding | Per-share valuation input |
| Market cap / Market capitalization | Trading multiple numerator |
| Gross profit, operating income, depreciation & amortization, capital expenditure | Historical margin or EBITDA proxy where supplied |
| Consolidated adjusted EBITDA | TTM trading multiple denominator, retaining company-reported definitions |

## Case-specific operating metrics

The uploaded dataset includes company-defined metrics as separate rows. Examples include Swiggy B2C GOV, Eternal B2C NOV, Blinkit and Instamart NOV, segment adjusted EBITDA, restaurant metrics, and dark store counts. These are kept as supplied and are not normalized to another company's definition.

## Data checks

- A source, period, company, metric, and unit are required. Missing or nonnumeric values are removed with a notice, not converted to zero.
- Duplicate company, period, and metric rows are flagged for reconciliation.
- Revenue growth uses the previous available quarter when the prior value is positive.
- A market quote is shown separately from filing rows. The quote snapshot has its own observation date and source.
- `Adjusted EBITDA`, `GOV`, and `NOV` are company-defined operating measures. They are not interchangeable with reported Ind AS revenue, EBITDA, or each other.
