# FoxAPIs datasets

Four free US business datasets, rebuilt weekly. Each comes as CSV and Parquet: the last 12 months and the last 7 days.

**Download:** [latest release](https://github.com/OsakaSaul/foxapis-datasets/releases/tag/latest)

| Dataset | One row is | Card and sample | Need it live, filtered or per company? |
|---|---|---|---|
| Private raises (SEC Form D) | one Form D notice | [card](datasets/form-d-private-raises/) | [Form D API](https://foxapis.com/free/free-sec-form-d-api/) |
| WARN layoff notices | one state notice | [card](datasets/warn-layoff-notices/) | [WARN API](https://foxapis.com/free/free-warn-layoff-notices-api/) |
| Executive changes (SEC 8-K) | one officer or director joining or leaving | [card](datasets/sec-8k-executive-changes/) | [Executive changes API](https://foxapis.com/free/free-sec-executive-changes-api/) |
| SBIR and STTR awards | one award record, without recipient names | [card](datasets/sbir-sttr-grants/) | [SBIR grants API](https://foxapis.com/free/free-sbir-grants-api/) |

## What is left out

No phone numbers, email addresses or street addresses. The awards files carry no recipient name, address, identifier,
website or award title, because of the limit USAspending.gov places on Dun & Bradstreet data (see that card).
People who asked us to suppress their details are left out.

## Licence

Our compilation is [CC BY 4.0](LICENSE). The underlying government records keep their sources' own terms; each card
says where the data comes from. Records are as published and may contain errors. Not investment or legal advice.

## How it is built

`scripts/build.py` downloads the week's export (public files, no key), checks row counts and columns, and writes
Parquet and the data cards. `scripts/publish.py` pushes new versions to Kaggle and Hugging Face when the repository
has their tokens. The workflow in `.github/workflows/weekly.yml` runs both.
