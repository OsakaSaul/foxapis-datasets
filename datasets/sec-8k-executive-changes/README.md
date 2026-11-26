# US Executive and Director Changes from SEC 8-K (Weekly)

One officer or director joining or leaving, as a company reported it in an 8-K (Item 5.02).

## Files

| File | Rows (built 2026-11-26) |
|---|---|
| `sec-8k-executive-changes-12-months.csv` / `.parquet` | 9,908 |
| `sec-8k-executive-changes-last-7-days.csv` / `.parquet` | 216 |

Rows are chosen by `filed_date`. Newest record in this build: 2026-11-25. Rebuilt weekly.

## Source and terms

8-K filings made with the US Securities and Exchange Commission. The `quote` column is the filing's own sentence; the other event columns are read from it by rule and can be wrong or empty, so read the quote before relying on them. People are named only because the company named them in its filing. No contact details are included.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `accession` | text | The 8-K's accession number |
| `event_seq` | integer | Order of the event within the filing |
| `company` | text | Company name as filed |
| `cik` | text | Company's SEC central index key |
| `tickers` | text | Tickers listed for the company |
| `filed_date` | date | Date the 8-K was filed |
| `event_type` | text | appointed, departed, change or other |
| `person` | text | Officer or director the company named (empty when the sentence could not be read for a name) |
| `role` | text | Role named in the sentence |
| `effective_date` | date | Effective date named in the sentence |
| `quote` | text | The filing's own sentence for this event |
| `filing_url` | url | The filing itself, on sec.gov |

## Three example analyses

```python
import pandas as pd
df = pd.read_parquet("sec-8k-executive-changes-12-months.parquet")
```

**Appointments and departures per month**

```python
print(df.pivot_table(index=df.filed_date.str[:7], columns='event_type', values='accession', aggfunc='count'))
```

**Companies with the most reported changes**

```python
print(df.company.value_counts().head(15))
```

**Chief financial officer departures, newest first**

```python
m = (df.event_type == 'departed') & df.role.fillna('').str.contains('chief financial|CFO', case=False)
print(df[m].sort_values('filed_date', ascending=False)[['filed_date', 'company', 'person', 'filing_url']].head(20))
```

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, https://github.com/OsakaSaul/foxapis-datasets".
The licence does not change the terms of the underlying government sources described above, and it grants no rights
over them. Records are as published by the source and may contain errors. Not investment or legal advice.
