# US Private Raises: SEC Form D Filings (Weekly)

One Form D or Form D/A notice of a private offering.

## Files

| File | Rows (built 2026-11-26) |
|---|---|
| `form-d-private-raises-12-months.csv` / `.parquet` | 63,199 |
| `form-d-private-raises-last-7-days.csv` / `.parquet` | 1,128 |

Rows are chosen by `filed_date`. Newest record in this build: 2026-11-25. Rebuilt weekly.

## Source and terms

Form D filings made by the issuers with the US Securities and Exchange Commission. Every row links to its filing on sec.gov. Amounts are as the issuer filed them and are not checked by anyone. A Form D/A repeats the offering with updated totals, so filter `is_amendment` to count offerings once.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `accession` | text | The filing's accession number (unique per filing) |
| `company` | text | Issuer name as filed |
| `cik` | text | Issuer's SEC central index key |
| `filed_date` | date | Date the Form D was filed |
| `is_amendment` | boolean | true for a Form D/A (an update to an earlier notice) |
| `first_sale_date` | date | Date of first sale, as filed |
| `amount_sold_usd` | number | Total amount sold so far, in US dollars |
| `offering_amount_usd` | number | Total offering amount; empty when filed as indefinite |
| `offering_indefinite` | boolean | true when the offering amount was filed as indefinite |
| `industry_group` | text | Industry group as filed |
| `is_pooled_fund` | boolean | true when the issuer is a pooled investment fund |
| `entity_type` | text | Legal form as filed |
| `state` | text | State or country of the principal place of business |
| `investors_count` | integer | Investors who have already invested |
| `has_non_accredited_investors` | boolean | true when the filing reports non-accredited investors |
| `filing_url` | url | The filing itself, on sec.gov |

## Three example analyses

```python
import pandas as pd
df = pd.read_parquet("form-d-private-raises-12-months.parquet")
```

**Money raised per month, first notices only, funds left out**

```python
d = df[~df.is_amendment & ~df.is_pooled_fund]
print(d.groupby(d.filed_date.str[:7]).amount_sold_usd.agg(['count', 'sum']))
```

**Industries with the most first-time notices**

```python
print(df[~df.is_amendment].industry_group.value_counts().head(15))
```

**Median amount sold by state**

```python
d = df[~df.is_amendment & (df.amount_sold_usd > 0)]
s = d.groupby('state').amount_sold_usd.agg(['count', 'median'])
print(s[s['count'] >= 50].sort_values('median', ascending=False).head(15))
```

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, https://github.com/OsakaSaul/foxapis-datasets".
The licence does not change the terms of the underlying government sources described above, and it grants no rights
over them. Records are as published by the source and may contain errors. Not investment or legal advice.
