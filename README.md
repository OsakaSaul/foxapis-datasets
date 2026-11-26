# FoxAPIs datasets

Free business datasets, rebuilt weekly. Four come as CSV and Parquet (the last 12 months and the last 7 days); five
more are CSV snapshots of what our public pages list.

**Download:** [latest release](https://github.com/OsakaSaul/foxapis-datasets/releases/tag/latest)

| Dataset | One row is | Card and sample | Need it live, filtered or per company? |
|---|---|---|---|
| Private raises (SEC Form D) | one Form D notice | [card](datasets/form-d-private-raises/) | [Form D API](https://foxapis.com/free/free-sec-form-d-api/) |
| WARN layoff notices | one state notice | [card](datasets/warn-layoff-notices/) | [WARN API](https://foxapis.com/free/free-warn-layoff-notices-api/) |
| Executive changes (SEC 8-K) | one officer or director joining or leaving | [card](datasets/sec-8k-executive-changes/) | [Executive changes API](https://foxapis.com/free/free-sec-executive-changes-api/) |
| SBIR and STTR awards | one award record, without recipient names | [card](datasets/sbir-sttr-grants/) | [SBIR grants API](https://foxapis.com/free/free-sbir-grants-api/) |

## Snapshots of public pages (CSV)

Each of these holds only rows and fields that a public page already shows. Pages list a limited number of rows, so
these are **not complete extracts**.

| Dataset | One row is | Card and sample | Browse | Need one record from code? |
|---|---|---|---|---|
| Federal contract awards | one listed award, without the recipient's name | [card](datasets/federal-contract-awards/) | [contracts](https://foxapis.com/contracts/) | [Contract award API](https://foxapis.com/api/contract-award/) |
| Trademark applications by class | one listed application (owner city only) | [card](datasets/trademark-filings-by-class/) | [trademarks](https://foxapis.com/trademarks/) | [Brand record API](https://foxapis.com/api/brand-record/) |
| Newly IRS-recognized nonprofits | one listed ruling, by state | [card](datasets/new-irs-recognized-nonprofits/) | [new nonprofits](https://foxapis.com/nonprofits/new/) | [Nonprofit check API](https://foxapis.com/api/research/nonprofit_vet/) |
| Reg CF offerings | one listed offering | [card](datasets/reg-cf-offerings/) | [crowdfunding](https://foxapis.com/crowdfunding/) | [Crowdfunding record API](https://foxapis.com/api/crowdfunding-record/) |
| Vendor status incidents | one incident from a vendor's own status page | [card](datasets/vendor-status-incidents/) | [status pages](https://foxplug.com/status/) | no API |

## What is left out

No phone numbers, email addresses or street addresses. The awards files carry no recipient name, address, identifier,
website or award title, because of the limit USAspending.gov places on Dun & Bradstreet data (see that card).
The contract awards file carries no recipient name for the same reason.
People who asked us to suppress their details are left out.

## Licence

Our compilation is [CC BY 4.0](LICENSE). The underlying government records keep their sources' own terms; each card
says where the data comes from. Records are as published and may contain errors. Not investment or legal advice.

## How it is built

`scripts/build.py` downloads the week's export (public files, no key), checks row counts and columns, and writes
Parquet and the data cards. `scripts/publish.py` pushes new versions to Kaggle and Hugging Face when the repository
has their tokens. `scripts/pages.py` reads the public pages and writes the five CSV snapshots (GitHub release only).
The workflow in `.github/workflows/weekly.yml` runs them on Mondays.
