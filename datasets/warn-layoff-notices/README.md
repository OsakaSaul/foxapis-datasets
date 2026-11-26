# US WARN Layoff and Closure Notices (Weekly)

One layoff or closure notice published by a US state under the WARN Act or the state's own version of it.

## Files

| File | Rows (built 2026-11-26) |
|---|---|
| `warn-layoff-notices-12-months.csv` / `.parquet` | 2,055 |
| `warn-layoff-notices-last-7-days.csv` / `.parquet` | 2 |

Rows are chosen by `notice_date`. Newest record in this build: 2026-11-20. Rebuilt weekly.

## Source and terms

Notices published by individual US states; `notice_url` is the state page each row came from. Each state sets its own terms of use and its own publishing schedule; we have not reviewed every state's terms. Not every state publishes notices, so this is not a count of all US layoffs.

## Columns

| Column | Type | Meaning |
|---|---|---|
| `state` | text | State that published the notice |
| `company` | text | Employer name as published |
| `city` | text | City of the affected site |
| `county` | text | County of the affected site, when published |
| `notice_date` | date | Date of the notice |
| `effective_date` | date | Date the layoff or closure takes effect, when published |
| `employees_affected` | integer | Employees affected |
| `notice_type` | text | Layoff, closure or other, as published |
| `permanence` | text | Permanent or temporary, when published |
| `industry` | text | Industry, when published |
| `notice_url` | url | The state's page that publishes the notice |

## Three example analyses

```python
import pandas as pd
df = pd.read_parquet("warn-layoff-notices-12-months.parquet")
```

**Employees affected per month**

```python
print(df.groupby(df.notice_date.str[:7]).employees_affected.agg(['count', 'sum']))
```

**States with the most notices**

```python
print(df.state.value_counts().head(15))
```

**Largest notices**

```python
print(df.nlargest(15, 'employees_affected')[['notice_date', 'state', 'company', 'employees_affected', 'notice_url']])
```

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, https://github.com/OsakaSaul/foxapis-datasets".
The licence does not change the terms of the underlying government sources described above, and it grants no rights
over them. Records are as published by the source and may contain errors. Not investment or legal advice.
