#!/usr/bin/env python3
"""Download this week's export, write CSV + Parquet files, and write one data card per dataset.

No key is needed: the export is published as public files. Run: python scripts/build.py
Writes  dist/<dataset>/    the files to publish (CSV, Parquet, README.md card, dataset-metadata.json)
        datasets/<dataset>/ the card and a 20-row sample, committed to the repository
"""
import json
import pathlib
import shutil
import urllib.request

import pandas as pd

BASE = "https://wnzxffwiiubqvcvnnjbz.supabase.co/storage/v1/object/public/public-datasets/latest/"
REPO = "https://github.com/OsakaSaul/foxapis-datasets"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

META = {
    "form-d-private-raises": {
        "title": "US Private Raises: SEC Form D Filings (Weekly)",
        "kaggle_slug": "us-form-d-private-raises",
        "subtitle": "Form D notices of private offerings, with a link to each filing",
        "api": "https://foxapis.com/free/free-sec-form-d-api/",
        "tags": ["finance", "business", "investing"],
        "one_row": "One Form D or Form D/A notice of a private offering.",
        "source": "Form D filings made by the issuers with the US Securities and Exchange Commission. Every row links to its filing on sec.gov. Amounts are as the issuer filed them and are not checked by anyone. A Form D/A repeats the offering with updated totals, so filter `is_amendment` to count offerings once.",
        "examples": [
            ("Money raised per month, first notices only, funds left out",
             "d = df[~df.is_amendment & ~df.is_pooled_fund]\nprint(d.groupby(d.filed_date.str[:7]).amount_sold_usd.agg(['count', 'sum']))"),
            ("Industries with the most first-time notices",
             "print(df[~df.is_amendment].industry_group.value_counts().head(15))"),
            ("Median amount sold by state",
             "d = df[~df.is_amendment & (df.amount_sold_usd > 0)]\ns = d.groupby('state').amount_sold_usd.agg(['count', 'median'])\nprint(s[s['count'] >= 50].sort_values('median', ascending=False).head(15))"),
        ],
    },
    "warn-layoff-notices": {
        "title": "US WARN Layoff and Closure Notices (Weekly)",
        "kaggle_slug": "us-warn-layoff-notices",
        "subtitle": "State WARN notices with employer, site, dates and a source link",
        "api": "https://foxapis.com/free/free-warn-layoff-notices-api/",
        "tags": ["employment", "business"],
        "one_row": "One layoff or closure notice published by a US state under the WARN Act or the state's own version of it.",
        "source": "Notices published by individual US states; `notice_url` is the state page each row came from. Each state sets its own terms of use and its own publishing schedule; we have not reviewed every state's terms. Not every state publishes notices, so this is not a count of all US layoffs.",
        "examples": [
            ("Employees affected per month",
             "print(df.groupby(df.notice_date.str[:7]).employees_affected.agg(['count', 'sum']))"),
            ("States with the most notices",
             "print(df.state.value_counts().head(15))"),
            ("Largest notices",
             "print(df.nlargest(15, 'employees_affected')[['notice_date', 'state', 'company', 'employees_affected', 'notice_url']])"),
        ],
    },
    "sec-8k-executive-changes": {
        "title": "US Executive and Director Changes from SEC 8-K (Weekly)",
        "kaggle_slug": "us-sec-8k-executive-changes",
        "subtitle": "Officers and directors joining or leaving, with the filing's own sentence",
        "api": "https://foxapis.com/free/free-sec-executive-changes-api/",
        "tags": ["finance", "business"],
        "one_row": "One officer or director joining or leaving, as a company reported it in an 8-K (Item 5.02).",
        "source": "8-K filings made with the US Securities and Exchange Commission. The `quote` column is the filing's own sentence; the other event columns are read from it by rule and can be wrong or empty, so read the quote before relying on them. People are named only because the company named them in its filing. No contact details are included.",
        "examples": [
            ("Appointments and departures per month",
             "print(df.pivot_table(index=df.filed_date.str[:7], columns='event_type', values='accession', aggfunc='count'))"),
            ("Companies with the most reported changes",
             "print(df.company.value_counts().head(15))"),
            ("Chief financial officer departures, newest first",
             "m = (df.event_type == 'departed') & df.role.fillna('').str.contains('chief financial|CFO', case=False)\nprint(df[m].sort_values('filed_date', ascending=False)[['filed_date', 'company', 'person', 'filing_url']].head(20))"),
        ],
    },
    "sbir-sttr-grants": {
        "title": "US SBIR and STTR Awards (Weekly)",
        "kaggle_slug": "us-sbir-sttr-awards",
        "subtitle": "Award amounts, agencies, phases and dates, with a link to each record",
        "api": "https://foxapis.com/free/free-sbir-grants-api/",
        "tags": ["government", "business"],
        "one_row": "One SBIR or STTR award record from US federal award data.",
        "source": "US federal award records on USAspending.gov. USAspending's terms (https://www.usaspending.gov/db_info) say that recipient names and addresses supplied by Dun & Bradstreet need credit to Dun & Bradstreet and may not be passed on in bulk. We cannot tell which records those are, so these files deliberately contain **no recipient names, addresses, identifiers, websites or award titles**. `source_url` opens the official record, which names the recipient. Recent awards reach USAspending with a delay, so the last-7-days file is often empty. This is not every SBIR/STTR award.",
        "examples": [
            ("Award dollars by agency",
             "print(df.groupby('agency').amount_usd.agg(['count', 'sum']).sort_values('sum', ascending=False))"),
            ("Median award by phase",
             "print(df.groupby('phase', dropna=False).amount_usd.median())"),
            ("Awards per month",
             "print(df.groupby(df.award_date.str[:7]).amount_usd.agg(['count', 'sum']))"),
        ],
    },
}


def fetch(name: str) -> bytes:
    request = urllib.request.Request(BASE + name, headers={"User-Agent": "foxapis-datasets"})
    with urllib.request.urlopen(request, timeout=180) as response:
        return response.read()


def card(name, info, meta, built_on):
    m = META[name]
    columns = "\n".join(f"| `{c['name']}` | {c['type']} | {c['description']} |" for c in meta["columns"])
    examples = "\n\n".join(
        f"**{title}**\n\n```python\n{code}\n```" for title, code in m["examples"])
    return f"""# {m['title']}

{m['one_row']}

## Files

| File | Rows (built {built_on}) |
|---|---|
| `{name}-12-months.csv` / `.parquet` | {meta['rows_12_months']:,} |
| `{name}-last-7-days.csv` / `.parquet` | {meta['rows_last_7_days']:,} |

Rows are chosen by `{meta['date_column']}`. Newest record in this build: {meta['newest']}. Rebuilt weekly.

## Source and terms

{m['source']}

## Columns

| Column | Type | Meaning |
|---|---|---|
{columns}

## Three example analyses

```python
import pandas as pd
df = pd.read_parquet("{name}-12-months.parquet")
```

{examples}

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, {REPO}".
The licence does not change the terms of the underlying government sources described above, and it grants no rights
over them. Records are as published by the source and may contain errors. Not investment or legal advice.
"""


def main():
    manifest = json.loads(fetch("manifest.json"))
    built_on = manifest["built_at"][:10]
    if DIST.exists():
        shutil.rmtree(DIST)
    for name, meta in manifest["datasets"].items():
        out = DIST / name
        out.mkdir(parents=True)
        keep = ROOT / "datasets" / name
        keep.mkdir(parents=True, exist_ok=True)
        types = {c["name"]: c["type"] for c in meta["columns"]}
        text = {n: "string" for n, t in types.items() if t in ("text", "url", "date")}
        for part, expected in (("12-months", meta["rows_12_months"]), ("last-7-days", meta["rows_last_7_days"])):
            stem = f"{name}-{part}"
            (out / f"{stem}.csv").write_bytes(fetch(f"{stem}.csv"))
            df = pd.read_csv(out / f"{stem}.csv", dtype=text)
            if len(df) != expected or list(df.columns) != list(types):
                raise SystemExit(f"{stem}: got {len(df)} rows, expected {expected}, or the columns differ; nothing is published")
            for column, kind in types.items():
                if kind == "integer":
                    df[column] = pd.to_numeric(df[column], errors="coerce").round().astype("Int64")
                elif kind == "number":
                    df[column] = pd.to_numeric(df[column], errors="coerce").astype("Float64")
                elif kind == "boolean":
                    df[column] = df[column].astype("boolean")
            df.to_parquet(out / f"{stem}.parquet", index=False)
            if part == "12-months":
                df.tail(20).to_csv(keep / "sample-20-rows.csv", index=False, lineterminator="\n")
        text_card = card(name, META[name], meta, built_on)
        (keep / "README.md").write_text(text_card, encoding="utf-8", newline="\n")
        # Hugging Face reads the YAML block at the top of the card
        front = ("---\nlicense: cc-by-4.0\nlanguage:\n- en\n"
                 f"pretty_name: \"{META[name]['title']}\"\ntags:\n" + "".join(f"- {t}\n" for t in META[name]["tags"]) +
                 "configs:\n- config_name: last_12_months\n  default: true\n"
                 f"  data_files: {name}-12-months.parquet\n- config_name: last_7_days\n  data_files: {name}-last-7-days.parquet\n---\n\n")
        (out / "README.md").write_text(front + text_card, encoding="utf-8", newline="\n")
        (out / "card-for-kaggle.txt").write_text(text_card, encoding="utf-8", newline="\n")
        print(f"{name}: {meta['rows_12_months']} rows, {meta['rows_last_7_days']} in the last 7 days")
    (ROOT / "datasets" / "manifest.json").write_text(
        json.dumps({"built_at": manifest["built_at"], "rows": {n: [d["rows_12_months"], d["rows_last_7_days"], d["newest"]] for n, d in manifest["datasets"].items()}}, indent=1) + "\n",
        encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
