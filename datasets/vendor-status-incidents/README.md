# Software Vendor Status Page Incidents

One incident a software vendor posted on its own official status page, as listed on a FoxPlug status page.

| File | Rows (built 2026-11-26) |
|---|---|
| `vendor-status-incidents-current.csv` | 1,766 |

**Browse it:** https://foxplug.com/status/
There is no API for this data.

## Source and terms

Each vendor's official status feed. `vendor_report_url` is the vendor's own report. Titles, impact labels and component names are the vendor's wording.

## What this file is not

Each tool page lists only its latest and longest incidents, so this is not a full history and counts here must not be used to rank vendors. An incident is whatever the vendor posted: it is not always an outage. Vendors post differently. Neither FoxAPIs nor FoxPlug is affiliated with them.

## Columns

| Column | Meaning |
|---|---|
| `started_date` | Date the incident began |
| `tool` | Product |
| `incident_title` | Vendor's title |
| `impact_label_from_vendor` | Vendor's impact label |
| `resolved_after` | Time to the vendor marking it resolved |
| `components` | Components the vendor named |
| `vendor_report_url` | Vendor's report |
| `listed_on` | The FoxPlug page the row came from |

## Refresh

Rebuilt weekly from the public pages. It holds only what those pages show; each file is a snapshot, and earlier
rows drop out as the pages change.

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, https://github.com/OsakaSaul/foxapis-datasets".
The licence does not change the terms of the underlying sources described above, and it grants no rights over them.
Records are as published by the source and may contain errors. Not legal or investment advice.
