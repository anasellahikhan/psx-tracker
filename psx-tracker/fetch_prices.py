#!/usr/bin/env python3
"""PSX Sharia Bluechips price tracker.

Fetches current prices for 33 sharia-compliant stocks plus the KSE-100 and
KMI-30 indices from the PSX data portal (dps.psx.com.pk) and appends one row
to data/psx_live.csv.

Designed to run unattended in GitHub Actions (.github/workflows/tracker.yml):
- Hourly, 9 AM - 4 PM Pakistan time, Monday-Friday.
- Public holidays are skipped automatically: the portal shows an "As of" date
  for its data; if that date is not today (PKT), the market did not trade
  today and no row is appended.
- On Friday's 4 PM PKT run it also writes data/psx_week_ending_YYYY-MM-DD.csv
  containing that week's rows (Monday to Friday).
"""

import csv
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

PKT = ZoneInfo("Asia/Karachi")
BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
LIVE_CSV = DATA_DIR / "psx_live.csv"

MARKET_WATCH_URL = "https://dps.psx.com.pk/market-watch"
INDICES_URL = "https://dps.psx.com.pk/indices"

# 33 sharia-compliant bluechips (order follows the Bluechips Sharia sheet).
# Note: Engro Corporation now trades as ENGROH (Engro Holdings) on PSX.
SYMBOLS = [
    "MARI", "OGDC", "PPL", "POL", "PSO", "SNGP", "SSGC",
    "FFC", "EFERT", "FATIMA", "ENGROH", "COLG", "LCI",
    "HUBC", "KAPCO", "ATRL", "PRL", "NRL",
    "LUCK", "DGKC", "MLCF", "FCCL", "CHCC",
    "SYS", "NETSOL", "SAZEW", "INDU", "HCAR", "AIRLINK",
    "SEARL", "AGP", "NESTLE", "ILP",
]

INDICES = ["KSE100", "KMI30"]
HEADER = ["Date", "Time"] + SYMBOLS + INDICES

HTTP_HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0 Safari/537.36"),
    "Accept-Language": "en-US,en;q=0.9",
}

NUM_RE = re.compile(r"-?\d+(\.\d+)?")


def fetch(url: str) -> str:
    resp = requests.get(url, headers=HTTP_HEADERS, timeout=60)
    resp.raise_for_status()
    return resp.text


def clean_number(text: str) -> str | None:
    """Return the numeric string without thousands separators, or None."""
    val = text.strip().replace(",", "")
    return val if NUM_RE.fullmatch(val) else None


def parse_market_watch(html: str) -> dict[str, str]:
    """Extract {symbol: CURRENT price} from the market-watch table.

    Row columns: SYMBOL | SECTOR | LISTED IN | LDCP | OPEN | HIGH | LOW |
                 CURRENT | CHANGE | CHANGE (%) | VOLUME
    """
    soup = BeautifulSoup(html, "lxml")
    prices: dict[str, str] = {}
    for a in soup.select('a[href*="/company/"]'):
        m = re.search(r"/company/([A-Z0-9]+)", a.get("href", ""))
        if not m or m.group(1) not in SYMBOLS:
            continue
        sym = m.group(1)
        tr = a.find_parent("tr")
        if tr is None:
            continue
        tds = tr.find_all("td")
        if len(tds) >= 8:
            val = clean_number(tds[7].get_text())
            if val is not None:
                prices[sym] = val
    return prices


def parse_indices(html: str):
    """Return ({index: Current value}, as_of_date | None).

    Indices table columns: Index | High | Low | Current | Change | % Change
    """
    soup = BeautifulSoup(html, "lxml")
    values: dict[str, str] = {}
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td")
        if len(tds) >= 4:
            name = tds[0].get_text(strip=True)
            if name in INDICES and name not in values:
                val = clean_number(tds[3].get_text())
                if val is not None:
                    values[name] = val

    as_of = None
    m = re.search(r"As of\s+([A-Za-z]{3}\s+\d{1,2},\s+\d{4})",
                  soup.get_text(" "))
    if m:
        try:
            as_of = datetime.strptime(m.group(1), "%b %d, %Y").date()
        except ValueError:
            pass
    return values, as_of


def read_rows() -> list[list[str]]:
    if not LIVE_CSV.exists():
        return []
    with LIVE_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    return rows[1:] if rows else []


def append_row(row: list[str]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    new_file = not LIVE_CSV.exists()
    with LIVE_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(HEADER)
        writer.writerow(row)


def maybe_write_weekly(now: datetime) -> None:
    """On Friday at/after 4 PM PKT, snapshot this week's rows (Mon-Fri)."""
    if now.weekday() != 4 or now.hour < 16:
        return
    friday = now.date()
    monday = friday - timedelta(days=4)
    week_rows = [r for r in read_rows()
                 if r and str(monday) <= r[0] <= str(friday)]
    out = DATA_DIR / f"psx_week_ending_{friday}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        writer.writerows(week_rows)
    print(f"Weekly snapshot written: {out.name} ({len(week_rows)} rows)")


def main() -> int:
    now = datetime.now(PKT)
    print(f"Run at {now:%Y-%m-%d %H:%M} PKT")

    prices = parse_market_watch(fetch(MARKET_WATCH_URL))
    idx_values, as_of = parse_indices(fetch(INDICES_URL))

    if as_of is not None and as_of != now.date():
        print(f"Portal data is as of {as_of}, not today - market closed "
              "(public holiday) or not yet open. No row appended.")
        maybe_write_weekly(now)
        return 0

    row = [f"{now:%Y-%m-%d}", f"{now:%H:%M}"]
    row += [prices.get(s, "") for s in SYMBOLS]
    row += [idx_values.get(i, "") for i in INDICES]

    got = sum(1 for v in row[2:] if v)
    missing = [s for s in SYMBOLS + INDICES
               if not (prices.get(s) or idx_values.get(s))]
    if got == 0:
        print("ERROR: no prices parsed - page layout may have changed.")
        return 1

    append_row(row)
    print(f"Appended row with {got}/{len(SYMBOLS) + 2} values."
          + (f" Missing: {', '.join(missing)}" if missing else ""))

    maybe_write_weekly(now)
    return 0


if __name__ == "__main__":
    sys.exit(main())
