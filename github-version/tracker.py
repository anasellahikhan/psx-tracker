#!/usr/bin/env python3
"""
PSX price tracker — GitHub Actions version.

Each run takes ONE snapshot of 7 stocks + 2 indices from the PSX data portal
and appends a row to psx_live.csv in the repository root. On the Friday 4 PM
(PKT) run it also writes psx_week_ending_YYYY-MM-DD.csv with that week's rows.

Scheduling is handled by .github/workflows/psx.yml (hourly 9-16 PKT, Mon-Fri).

Symbols: OGDC, MARI, ENGROH (Engro Holdings), PSO, SYS, HUBC, FFC
Indices: KSE100, KMI30
"""

import csv
import os
import re
import sys
import time
from datetime import datetime, timedelta
from io import StringIO
from zoneinfo import ZoneInfo

import requests

try:
    import pandas as pd
except ImportError:
    pd = None

PKT = ZoneInfo("Asia/Karachi")
LIVE_CSV = "psx_live.csv"  # repo root (workflow runs from the checkout dir)

STOCKS = ["OGDC", "MARI", "ENGROH", "PSO", "SYS", "HUBC", "FFC"]
INDICES = ["KSE100", "KMI30"]
HEADER = ["Date", "Time"] + STOCKS + INDICES

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def _num(text):
    """'186,255.55' -> 186255.55, else None."""
    try:
        return float(str(text).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def fetch_stock_prices():
    """Return {symbol: current_price} from the PSX market-watch table."""
    html = requests.get("https://dps.psx.com.pk/market-watch",
                        headers=HEADERS, timeout=30).text
    prices = {}

    if pd is not None:
        try:
            for table in pd.read_html(StringIO(html)):
                cols = [str(c).strip().upper() for c in table.columns]
                if "SYMBOL" in cols and "CURRENT" in cols:
                    table.columns = cols
                    for _, row in table.iterrows():
                        sym = str(row["SYMBOL"]).split()[0].strip()
                        if sym in STOCKS:
                            prices[sym] = _num(row["CURRENT"])
                    break
        except Exception:
            pass

    # Regex fallback: CURRENT is the 5th number (LDCP, OPEN, HIGH, LOW, CURRENT).
    for sym in STOCKS:
        if prices.get(sym) is not None:
            continue
        m = re.search(r'company/%s["\'].{0,3000}?</tr>' % sym, html, re.S)
        if m:
            nums = re.findall(r'>\s*([\d,]+\.\d{2})\s*<', m.group(0))
            if len(nums) >= 5:
                prices[sym] = _num(nums[4])
    return prices


def fetch_index_values():
    """Return {index: current_value} from the PSX indices page."""
    html = requests.get("https://dps.psx.com.pk/indices",
                        headers=HEADERS, timeout=30).text
    values = {}

    if pd is not None:
        try:
            for table in pd.read_html(StringIO(html)):
                cols = [str(c).strip().upper() for c in table.columns]
                if "INDEX" in cols and "CURRENT" in cols:
                    table.columns = cols
                    for _, row in table.iterrows():
                        name = re.sub(r"[^A-Z0-9]", "", str(row["INDEX"]).upper())
                        for idx in INDICES:
                            if name.startswith(idx):
                                values[idx] = _num(row["CURRENT"])
                    break
        except Exception:
            pass

    for idx in INDICES:
        if values.get(idx) is None:
            m = re.search(r'%s\b.{0,400}?([\d,]{4,}\.\d{2})' % idx, html, re.S)
            if m:
                values[idx] = _num(m.group(1))
    return values


def take_snapshot():
    """Fetch everything (3 attempts) and append one row to psx_live.csv."""
    prices, indices = {}, {}
    for attempt in range(3):
        try:
            if len(prices) < len(STOCKS):
                prices.update({k: v for k, v in fetch_stock_prices().items()
                               if v is not None})
            if len(indices) < len(INDICES):
                indices.update({k: v for k, v in fetch_index_values().items()
                                if v is not None})
            if len(prices) == len(STOCKS) and len(indices) == len(INDICES):
                break
        except Exception as e:
            print(f"attempt {attempt + 1} failed: {e}", flush=True)
        time.sleep(20)

    now = datetime.now(PKT)
    row = [now.strftime("%Y-%m-%d"), now.strftime("%H:%M")]
    row += [prices.get(s, "") for s in STOCKS]
    row += [indices.get(i, "") for i in INDICES]

    new_file = not os.path.exists(LIVE_CSV)
    with open(LIVE_CSV, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(HEADER)
        w.writerow(row)
    print(f"appended: {row}", flush=True)


def write_weekly_file():
    """Copy this week's rows (Mon..today) into psx_week_ending_YYYY-MM-DD.csv."""
    today = datetime.now(PKT).date()
    monday = today - timedelta(days=today.weekday())
    out_path = f"psx_week_ending_{today.isoformat()}.csv"

    with open(LIVE_CSV, newline="") as f:
        rows = list(csv.reader(f))

    weekly = [rows[0]]
    for r in rows[1:]:
        try:
            d = datetime.strptime(r[0], "%Y-%m-%d").date()
            if monday <= d <= today:
                weekly.append(r)
        except (ValueError, IndexError):
            continue

    with open(out_path, "w", newline="") as f:
        csv.writer(f).writerows(weekly)
    print(f"weekly file written: {out_path} ({len(weekly) - 1} rows)", flush=True)


def main():
    now = datetime.now(PKT)
    take_snapshot()
    # Friday 4 PM PKT run (the 11:00 UTC job, allowing for start delays)
    if now.weekday() == 4 and now.hour >= 16:
        write_weekly_file()


if __name__ == "__main__":
    sys.exit(main())
