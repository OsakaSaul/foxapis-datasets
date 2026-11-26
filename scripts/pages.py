#!/usr/bin/env python3
"""Build five weekly CSV snapshots from our own public pages. Run: python scripts/pages.py (after scripts/build.py)

No key and no library beyond Python's own: each file holds only rows and fields that a public page already shows.
A page lists a limited number of rows, so these are snapshots of what the pages list, not complete extracts; every
card says so. A family whose page layout has changed, or whose row count falls too low, is not published and the run
fails; the other families are still written.
Writes  dist/<dataset>/<dataset>-current.csv    and datasets/<dataset>/ (card and a 20-row sample)
"""
import csv
import datetime
import html
import io
import json
import pathlib
import re
import sys
import time
import urllib.request

REPO = "https://github.com/OsakaSaul/foxapis-datasets"
ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
FA, FP = "https://foxapis.com", "https://foxplug.com"


def get(url: str) -> str:
    for attempt in (1, 2, 3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "foxapis-datasets"})
            with urllib.request.urlopen(request, timeout=90) as response:
                time.sleep(0.2)
                return response.read().decode("utf-8")
        except Exception:
            if attempt == 3:
                raise
            time.sleep(5 * attempt)


def sitemap(url: str) -> list:
    found = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", get(url)):
        if loc.endswith(".xml"):
            found.extend(sitemap(loc))
        else:
            found.append(loc)
    return found


def text(cell: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", cell)).split())


def tables(page: str, css_class: str):
    """Yield (headings, rows) for each table of this class; a row is a list of raw cell HTML."""
    for table in re.findall(rf'<table class="{css_class}">.*?</table>', page, re.S):
        heads = [text(h) for h in re.findall(r"<th\b[^>]*>(.*?)</th>", table, re.S)]
        body = table.split("<tbody>", 1)[1]
        yield heads, [re.findall(r"<td\b[^>]*>(.*?)</td>", row, re.S) for row in re.findall(r"<tr\b[^>]*>(.*?)</tr>", body, re.S)]


def link(cell: str, host: str) -> str:
    found = re.search(rf'href="(https://{re.escape(host)}/[^"]+)"', cell)
    return html.unescape(found.group(1)) if found else ""


def need(heads, expected, url):
    if heads != expected:
        raise ValueError(f"{url}: columns are now {heads}")


def title_of(page: str) -> str:
    return text(re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S).group(1))


# ── federal contract awards ─────────────────────────────────────────────────
# No recipient name: USAspending limits passing on Dun & Bradstreet business names in bulk.
def contracts(urls):
    awards = {}
    for url in [u for u in urls if re.match(rf"{FA}/contracts/.", u)]:
        page = get(url)
        for css in ("cz-table", "nc-table"):
            for heads, rows in tables(page, css):
                for cells in rows:
                    by = dict(zip(heads, cells))
                    record = link(by.get("Official record", ""), "www.usaspending.gov")
                    if not record or "Amount obligated" not in by or "Date" not in by:
                        raise ValueError(f"{url}: a row has no official record, amount or date")
                    a = awards.setdefault(record, dict.fromkeys(["date", "amount_obligated_usd", "awarding_agency", "naics_code", "state_page", "place_of_performance", "set_aside", "official_record_url", "listed_on"], ""))
                    a["official_record_url"] = record
                    a["listed_on"] = a["listed_on"] or url
                    a["date"] = text(by["Date"])
                    a["amount_obligated_usd"] = int(re.sub(r"[^\d-]", "", text(by["Amount obligated"])))
                    a["awarding_agency"] = a["awarding_agency"] or text(by.get("Awarding agency") or by.get("Agency") or "")
                    code = re.match(r"\d{6}", text(by.get("Industry code (NAICS)", "")))
                    if code:
                        a["naics_code"] = code.group(0)
                    elif "/contracts/naics/" in url:
                        a["naics_code"] = re.search(r"/naics/(\d{6})-", url).group(1)
                    state = re.match(rf"{FA}/contracts/(?!agency/|naics/)([a-z-]+)/$", url)
                    if state:
                        a["state_page"] = state.group(1).replace("-", " ").title().replace(" Of ", " of ")
                    a["place_of_performance"] = a["place_of_performance"] or text(by.get("Place of performance", ""))
                    a["set_aside"] = a["set_aside"] or text(by.get("Set-aside", ""))
    return sorted(awards.values(), key=lambda a: (a["date"], a["official_record_url"]), reverse=True)


# ── trademark filings by class ──────────────────────────────────────────────
def trademarks(urls):
    out = []
    for url in [u for u in urls if re.match(rf"{FA}/trademarks/class-\d+-", u)]:
        number = int(re.search(r"/class-(\d+)-", url).group(1))
        for heads, rows in tables(get(url), "tm-table"):
            need(heads, ["Mark", "Owner, as filed", "Owner city", "Filed", "Serial"], url)
            for c in rows:
                serial = re.search(r"\?q=(\d+)", c[4]).group(1)
                out.append({"filing_date": text(c[3]), "class_number": number, "mark": text(c[0]), "owner_as_filed": text(c[1]), "owner_city": text(c[2]),
                            "serial_number": serial, "uspto_status_url": link(c[4], "tsdr.uspto.gov"), "listed_on": url})
    return sorted(out, key=lambda r: (r["filing_date"], r["serial_number"], r["class_number"]), reverse=True)


# ── new IRS recognitions by state ───────────────────────────────────────────
def nonprofits(urls):
    out = []
    for url in [u for u in urls if re.match(rf"{FA}/nonprofits/new/(?!category/)[a-z-]+/$", u)]:
        page = get(url)
        state = url.rstrip("/").rsplit("/", 1)[1].replace("-", " ").title().replace(" Of ", " of ")
        for heads, rows in tables(page, "np-table"):
            need(heads, ["Name, as the IRS writes it", "City", "Subsection", "NTEE category", "Ruling date", "EIN"], url)
            for c in rows:
                out.append({"ruling_month": text(c[4]), "state": state, "name_as_irs_writes_it": text(c[0]), "city": text(c[1]), "subsection": text(c[2]),
                            "ntee_category": text(c[3]), "ein": re.search(r"\?q=(\d{9})", c[5]).group(1), "listed_on": url})
    return sorted(out, key=lambda r: (r["state"], r["name_as_irs_writes_it"], r["ein"]))


# ── Regulation Crowdfunding offerings ───────────────────────────────────────
def crowdfunding(urls):
    out = []
    for url in [u for u in urls if re.match(rf"{FA}/crowdfunding/[a-z-]+/$", u)]:
        state = url.rstrip("/").rsplit("/", 1)[1].replace("-", " ").title()
        for heads, rows in tables(get(url), "cf-table"):
            need(heads, ["Issuer", "Intermediary", "Target", "Maximum", "Deadline", "Filed", "SEC filing"], url)
            for c in rows:
                issuer = text(c[0].split("<br")[0])
                note = text(re.sub(r"^.*?<br\s*/?>", "", c[0], flags=re.S)) if "<br" in c[0] else ""
                out.append({"filed_date": text(c[5]), "state": state, "issuer": issuer, "intermediary": text(c[1]), "target_usd": re.sub(r"[^\d]", "", text(c[2])),
                            "maximum_usd": re.sub(r"[^\d]", "", text(c[3])), "deadline": text(c[4]), "page_note": note,
                            "sec_filing_url": link(c[6], "www.sec.gov"), "listed_on": url})
    return sorted(out, key=lambda r: (r["filed_date"], r["sec_filing_url"]), reverse=True)


# ── vendor status incidents ─────────────────────────────────────────────────
MONTHS = "January February March April May June July August September October November December".split()


def day(words: str) -> str:
    return datetime.datetime.strptime(words, "%B %d, %Y").date().isoformat()


def details(inner: str):
    """'minor; resolved after 5 minutes; A and B' -> impact, resolved-after, components."""
    parts = [p.strip() for p in inner.split(";")]
    impact = parts.pop(0)
    took = ""
    if parts and parts[0].startswith("resolved after "):
        took = parts.pop(0)[len("resolved after "):]
    elif parts and parts[0] in ("marked resolved at once", "not marked resolved when we read it"):
        took = parts.pop(0)
    return impact, took, "; ".join(parts)


def status(_urls):
    found = {}
    pages = [u for u in sitemap(f"{FP}/sitemap.xml") if re.match(rf"{FP}/status/[a-z0-9-]+$", u)]
    date = rf"(?:{'|'.join(MONTHS)}) \d{{1,2}}, \d{{4}}"
    unread = 0
    for url in pages:
        page = get(url)
        tool = re.match(r"(.*?) status and incident history", title_of(page)).group(1)
        for block in re.findall(r'<ul class="st-list">(.*?)</ul>', page, re.S):
            for item in re.findall(r"<li>(.*?)</li>", block, re.S):
                report = re.search(r'<a href="([^"]+)"[^>]*>Report</a>', item)
                if not report:
                    continue  # lists of component names carry no report link
                words = text(item[:report.start()])
                if re.search(r": named in \d+ incidents?, most recently ", words):
                    continue  # the page's summary by component, not an incident of its own
                recent = re.match(rf"({date}): (.*) \(([^()]*(?:\([^()]*\)[^()]*)*)\)\.?$", words)
                longest = re.match(rf'"(.*)" began ({date}) and was marked resolved (.*?) later \((.*)\)\.?$', words)
                if longest:
                    title, started, took, (impact, _, parts) = longest.group(1), longest.group(2), longest.group(3), details(longest.group(4))
                elif recent:
                    started, title = recent.group(1), recent.group(2)
                    impact, took, parts = details(recent.group(3))
                else:
                    unread += 1
                    continue
                key = (tool, html.unescape(report.group(1)))
                row = {"started_date": day(started), "tool": tool, "incident_title": title, "impact_label_from_vendor": impact, "resolved_after": took,
                       "components": parts, "vendor_report_url": key[1], "listed_on": url}
                if key not in found or len(row["components"]) > len(found[key]["components"]):
                    found[key] = row
    if unread > max(5, len(found) // 100):
        raise ValueError(f"status: {unread} list items could not be read")
    if unread:
        print(f"vendor-status-incidents: {unread} list items not read and left out")
    return sorted(found.values(), key=lambda r: (r["started_date"], r["tool"], r["vendor_report_url"]), reverse=True)


# name: (builder, least rows accepted, card)
FAMILIES = {
    "federal-contract-awards": (contracts, 200, {
        "title": "US Federal Contract Awards Listed This Week",
        "one_row": "One new federal contract award listed on a FoxAPIs contract page (the largest recent ones by state, agency and industry).",
        "source": "US federal award records on [USAspending.gov](https://www.usaspending.gov/). Each row links to the official record. **Recipient names are not in this file**: USAspending's [terms](https://www.usaspending.gov/db_info) say business names and addresses supplied by Dun & Bradstreet need credit to Dun & Bradstreet and limit passing them on in bulk, and we cannot tell which rows those are. Open the official record to see the recipient.",
        "limits": "Each page lists only its largest recent awards, so this is not every award. Amounts are the dollars obligated on the record when the page was built, and records are revised later. Blank cells are fields the listing page does not show.",
        "columns": {"date": "Award date as listed", "amount_obligated_usd": "Dollars obligated", "awarding_agency": "Awarding agency (blank if the page did not show it)", "naics_code": "Six-digit industry code", "state_page": "State of performance, when the award is on a state page", "place_of_performance": "Where the work is done, as listed", "set_aside": "Set-aside type (industry pages only)", "official_record_url": "The record on USAspending.gov", "listed_on": "The FoxAPIs page the row came from"},
        "family": f"{FA}/contracts/", "api": ("Contract award API", f"{FA}/api/contract-award/")}),
    "trademark-filings-by-class": (trademarks, 1000, {
        "title": "US Trademark Applications by Class, Newest Listed",
        "one_row": "One recent US trademark application listed on a FoxAPIs class page. A mark filed in several classes can appear once per class.",
        "source": "US Patent and Trademark Office application data. Each row links to the USPTO's own status page. **An application is not a registration.**",
        "limits": "Each class page lists only its newest applications, from corporations and limited liability companies. Of the owner's address only the city is shown, as filed; no person, street or state. Removal requests are honored.",
        "columns": {"filing_date": "Date filed", "class_number": "International class", "mark": "The mark, as filed", "owner_as_filed": "Owner name, as filed", "owner_city": "Owner city, as filed", "serial_number": "USPTO serial number", "uspto_status_url": "USPTO status page", "listed_on": "The FoxAPIs page the row came from"},
        "family": f"{FA}/trademarks/", "api": ("Brand record API", f"{FA}/api/brand-record/")}),
    "new-irs-recognized-nonprofits": (nonprofits, 1000, {
        "title": "Newly IRS-Recognized US Nonprofits by State",
        "one_row": "One organization with an IRS ruling in the newest month, as listed on a FoxAPIs state page.",
        "source": "The IRS [Exempt Organizations Business Master File extract](https://www.irs.gov/charities-non-profits/exempt-organizations-business-master-file-extract-eo-bmf). **A ruling date is not a founding date**; it also covers restored exemptions and some re-determinations.",
        "limits": "State pages list a limited number of rows each, in name order, so large states are cut off; this is not every ruling. The category is the IRS file's own and can be wrong or broad. No person, street or ZIP code. A listing is not an endorsement or a check. Updated when the IRS file is (about monthly).",
        "columns": {"ruling_month": "Month of the IRS ruling", "state": "State", "name_as_irs_writes_it": "Name as in the IRS file", "city": "City", "subsection": "Tax code subsection", "ntee_category": "NTEE major group", "ein": "Employer Identification Number", "listed_on": "The FoxAPIs page the row came from"},
        "family": f"{FA}/nonprofits/new/", "api": ("Nonprofit check API", f"{FA}/api/research/nonprofit_vet/")}),
    "reg-cf-offerings": (crowdfunding, 20, {
        "title": "US Regulation Crowdfunding Offerings Listed This Week",
        "one_row": "One Regulation Crowdfunding offering listed on a FoxAPIs state page.",
        "source": "Form C filings made with the US Securities and Exchange Commission. Each row links to the filing on sec.gov. Figures are as the issuer filed them and are not checked.",
        "limits": "Only states that have a page are included, so this is not the whole country. A later filing can change or withdraw an offering: read the issuer's filings. Not an offer, a recommendation or investment advice.",
        "columns": {"filed_date": "Date filed", "state": "State page", "issuer": "Issuer name", "intermediary": "Funding portal or broker", "target_usd": "Target amount", "maximum_usd": "Maximum amount", "deadline": "Offering deadline", "page_note": "The page's note on this issuer, if any", "sec_filing_url": "The Form C on sec.gov", "listed_on": "The FoxAPIs page the row came from"},
        "family": f"{FA}/crowdfunding/", "api": ("Crowdfunding record API", f"{FA}/api/crowdfunding-record/")}),
    "vendor-status-incidents": (status, 500, {
        "title": "Software Vendor Status Page Incidents",
        "one_row": "One incident a software vendor posted on its own official status page, as listed on a FoxPlug status page.",
        "source": "Each vendor's official status feed. `vendor_report_url` is the vendor's own report. Titles, impact labels and component names are the vendor's wording.",
        "limits": "Each tool page lists only its latest and longest incidents, so this is not a full history and counts here must not be used to rank vendors. An incident is whatever the vendor posted: it is not always an outage. Vendors post differently. Neither FoxAPIs nor FoxPlug is affiliated with them.",
        "columns": {"started_date": "Date the incident began", "tool": "Product", "incident_title": "Vendor's title", "impact_label_from_vendor": "Vendor's impact label", "resolved_after": "Time to the vendor marking it resolved", "components": "Components the vendor named", "vendor_report_url": "Vendor's report", "listed_on": "The FoxPlug page the row came from"},
        "family": f"{FP}/status/", "api": None}),
}


def as_csv(rows, columns) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def card(name, m, rows, built_on):
    columns = "\n".join(f"| `{c}` | {d} |" for c, d in m["columns"].items())
    api = (f"Need one record on request, from code? [{m['api'][0]}]({m['api'][1]})." if m["api"] else "There is no API for this data.")
    return f"""# {m['title']}

{m['one_row']}

| File | Rows (built {built_on}) |
|---|---|
| `{name}-current.csv` | {rows:,} |

**Browse it:** {m['family']}
{api}

## Source and terms

{m['source']}

## What this file is not

{m['limits']}

## Columns

| Column | Meaning |
|---|---|
{columns}

## Refresh

Rebuilt weekly from the public pages. It holds only what those pages show; each file is a snapshot, and earlier
rows drop out as the pages change.

## Licence

Our compilation (selection, cleaning and column layout) is released under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Attribute "FoxAPIs datasets, {REPO}".
The licence does not change the terms of the underlying sources described above, and it grants no rights over them.
Records are as published by the source and may contain errors. Not legal or investment advice.
"""


def main(only):
    urls = sitemap(f"{FA}/sitemap.xml")
    built_on = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    manifest_path = ROOT / "datasets" / "manifest-pages.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    failed = []
    for name, (build, least, m) in FAMILIES.items():
        if only and name not in only:
            continue
        try:
            rows = build(urls)
            if len(rows) < least:
                raise ValueError(f"only {len(rows)} rows, expected at least {least}")
            columns = list(m["columns"])
            if set(rows[0]) != set(columns):
                raise ValueError("row fields and card columns differ")
            if any(re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", str(v), re.I) for r in rows for v in r.values()):
                raise ValueError("something that looks like an email address is in the rows")
        except Exception as error:
            failed.append(f"{name}: {error}")
            continue
        out, keep = DIST / name, ROOT / "datasets" / name
        out.mkdir(parents=True, exist_ok=True)
        keep.mkdir(parents=True, exist_ok=True)
        (out / f"{name}-current.csv").write_text(as_csv(rows, columns), encoding="utf-8", newline="\n")
        (keep / "sample-20-rows.csv").write_text(as_csv(rows[:20], columns), encoding="utf-8", newline="\n")
        (keep / "README.md").write_text(card(name, m, len(rows), built_on), encoding="utf-8", newline="\n")
        manifest[name] = {"built_on": built_on, "rows": len(rows)}
        print(f"{name}: {len(rows)} rows")
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8", newline="\n")
    if failed:
        sys.exit("Not published: " + " | ".join(failed))


if __name__ == "__main__":
    main(sys.argv[1:])
