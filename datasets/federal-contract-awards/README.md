# US Federal Contract Awards Listed This Week

One new federal contract award listed on a FoxAPIs contract page (the largest recent ones by state, agency and industry).

| File | Rows (built 2026-11-26) |
|---|---|
| `federal-contract-awards-current.csv` | 697 |

**Browse it:** https://foxapis.com/contracts/
Need one record on request, from code? [Contract award API](https://foxapis.com/api/contract-award/).

## Source and terms

US federal award records on [USAspending.gov](https://www.usaspending.gov/). Each row links to the official record. **Recipient names are not in this file**: USAspending's [terms](https://www.usaspending.gov/db_info) say business names and addresses supplied by Dun & Bradstreet need credit to Dun & Bradstreet and limit passing them on in bulk, and we cannot tell which rows those are. Open the official record to see the recipient.

## What this file is not

Each page lists only its largest recent awards, so this is not every award. Amounts are the dollars obligated on the record when the page was built, and records are revised later. Blank cells are fields the listing page does not show.

## Columns

| Column | Meaning |
|---|---|
| `date` | Award date as listed |
| `amount_obligated_usd` | Dollars obligated |
| `awarding_agency` | Awarding agency (blank if the page did not show it) |
| `naics_code` | Six-digit industry code |
| `state_page` | State of performance, when the award is on a state page |
| `place_of_performance` | Where the work is done, as listed |
| `set_aside` | Set-aside type (industry pages only) |
| `official_record_url` | The record on USAspending.gov |
| `listed_on` | The FoxAPIs page the row came from |

## Refresh

Rebuilt weekly from the public pages. It holds only what those pages show; each file is a snapshot, and earlier
rows drop out as the pages change.

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, https://github.com/OsakaSaul/foxapis-datasets".
The licence does not change the terms of the underlying sources described above, and it grants no rights over them.
Records are as published by the source and may contain errors. Not legal or investment advice.
