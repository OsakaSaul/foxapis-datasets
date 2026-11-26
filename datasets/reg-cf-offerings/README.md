# US Regulation Crowdfunding Offerings Listed This Week

One Regulation Crowdfunding offering listed on a FoxAPIs state page.

| File | Rows (built 2026-11-26) |
|---|---|
| `reg-cf-offerings-current.csv` | 77 |

**Browse it:** https://foxapis.com/crowdfunding/
Need one record on request, from code? [Crowdfunding record API](https://foxapis.com/api/crowdfunding-record/).

## Source and terms

Form C filings made with the US Securities and Exchange Commission. Each row links to the filing on sec.gov. Figures are as the issuer filed them and are not checked.

## What this file is not

Only states that have a page are included, so this is not the whole country. A later filing can change or withdraw an offering: read the issuer's filings. Not an offer, a recommendation or investment advice.

## Columns

| Column | Meaning |
|---|---|
| `filed_date` | Date filed |
| `state` | State page |
| `issuer` | Issuer name |
| `intermediary` | Funding portal or broker |
| `target_usd` | Target amount |
| `maximum_usd` | Maximum amount |
| `deadline` | Offering deadline |
| `page_note` | The page's note on this issuer, if any |
| `sec_filing_url` | The Form C on sec.gov |
| `listed_on` | The FoxAPIs page the row came from |

## Refresh

Rebuilt weekly from the public pages. It holds only what those pages show; each file is a snapshot, and earlier
rows drop out as the pages change.

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, https://github.com/OsakaSaul/foxapis-datasets".
The licence does not change the terms of the underlying sources described above, and it grants no rights over them.
Records are as published by the source and may contain errors. Not legal or investment advice.
