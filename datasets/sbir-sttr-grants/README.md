# US SBIR and STTR Awards (Weekly)

One SBIR or STTR award record from US federal award data.

## Files

| File | Rows (built 2026-11-26) |
|---|---|
| `sbir-sttr-grants-12-months.csv` / `.parquet` | 1,283 |
| `sbir-sttr-grants-last-7-days.csv` / `.parquet` | 0 |

Rows are chosen by `award_date`. Newest record in this build: 2026-11-16. Rebuilt weekly.

## Source and terms

US federal award records on USAspending.gov. USAspending's terms (https://www.usaspending.gov/db_info) say that recipient names and addresses supplied by Dun & Bradstreet need credit to Dun & Bradstreet and may not be passed on in bulk. We cannot tell which records those are, so these files deliberately contain **no recipient names, addresses, identifiers, websites or award titles**. `source_url` opens the official record, which names the recipient. Recent awards reach USAspending with a delay, so the last-7-days file is often empty. This is not every SBIR/STTR award.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `award_date` | date | Date of the award |
| `end_date` | date | Contract end date, when published |
| `kind` | text | Award kind |
| `agency` | text | Awarding agency |
| `branch` | text | Branch or sub-agency |
| `program` | text | SBIR or STTR, when published |
| `phase` | text | Program phase, when published |
| `topic_code` | text | Solicitation topic code, when published |
| `award_year` | integer | Award year |
| `amount_usd` | number | Award amount in US dollars |
| `source_url` | url | The award record on USAspending.gov (it names the recipient) |

## Three example analyses

```python
import pandas as pd
df = pd.read_parquet("sbir-sttr-grants-12-months.parquet")
```

**Award dollars by agency**

```python
print(df.groupby('agency').amount_usd.agg(['count', 'sum']).sort_values('sum', ascending=False))
```

**Median award by phase**

```python
print(df.groupby('phase', dropna=False).amount_usd.median())
```

**Awards per month**

```python
print(df.groupby(df.award_date.str[:7]).amount_usd.agg(['count', 'sum']))
```

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, https://github.com/OsakaSaul/foxapis-datasets".
The licence does not change the terms of the underlying government sources described above, and it grants no rights
over them. Records are as published by the source and may contain errors. Not investment or legal advice.
