# Newly IRS-Recognized US Nonprofits by State

One organization with an IRS ruling in the newest month, as listed on a FoxAPIs state page.

| File | Rows (built 2026-11-26) |
|---|---|
| `new-irs-recognized-nonprofits-current.csv` | 3,572 |

**Browse it:** https://foxapis.com/nonprofits/new/
Need one record on request, from code? [Nonprofit check API](https://foxapis.com/api/research/nonprofit_vet/).

## Source and terms

The IRS [Exempt Organizations Business Master File extract](https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf). **A ruling date is not a founding date**; it also covers restored exemptions and some re-determinations.

## What this file is not

State pages list a limited number of rows each, in name order, so large states are cut off; this is not every ruling. The category is the IRS file's own and can be wrong or broad. No person, street or ZIP code. A listing is not an endorsement or a check. Updated when the IRS file is (about monthly).

## Columns

| Column | Meaning |
|---|---|
| `ruling_month` | Month of the IRS ruling |
| `state` | State |
| `name_as_irs_writes_it` | Name as in the IRS file |
| `city` | City |
| `subsection` | Tax code subsection |
| `ntee_category` | NTEE major group |
| `ein` | Employer Identification Number |
| `listed_on` | The FoxAPIs page the row came from |

## Refresh

Rebuilt weekly from the public pages. It holds only what those pages show; each file is a snapshot, and earlier
rows drop out as the pages change.

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, https://github.com/OsakaSaul/foxapis-datasets".
The licence does not change the terms of the underlying sources described above, and it grants no rights over them.
Records are as published by the source and may contain errors. Not legal or investment advice.
