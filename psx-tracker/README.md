# PSX Sharia Bluechips Tracker

Automatic hourly price tracker for 33 sharia-compliant PSX bluechips plus the KSE-100 and KMI-30 indices. It runs entirely on GitHub's servers (GitHub Actions), so it keeps working even when your PC is off.

## Live data

| What | Link |
|---|---|
| Live CSV (always up to date) | https://raw.githubusercontent.com/anasellahikhan/psx-tracker/main/data/psx_live.csv |
| Live dashboard (after enabling GitHub Pages) | https://anasellahikhan.github.io/psx-tracker/ |
| Weekly snapshots (created every Friday 4 PM PKT) | `data/psx_week_ending_YYYY-MM-DD.csv` |

## Use in Google Colab

```python
import pandas as pd

url = "https://raw.githubusercontent.com/anasellahikhan/psx-tracker/main/data/psx_live.csv"
df = pd.read_csv(url, parse_dates=["Date"])
df.tail()

# Example: plot KSE-100
df.plot(x="Date", y="KSE100", figsize=(10, 4), title="KSE-100");
```

## Schedule

Runs Monday-Friday at 9:35 AM PKT (just after market open) and then hourly at 10:05, 11:05 ... 16:05 PKT. GitHub cron can be delayed by a few minutes at busy times — the recorded `Time` column always shows the actual fetch time in Pakistan time.

Public holidays are handled automatically: the PSX portal reports the date its data belongs to; if that date is not today, the market did not trade and no row is recorded.

Every Friday at the 4 PM run, a weekly snapshot file `psx_week_ending_YYYY-MM-DD.csv` is saved with that week's rows (Monday-Friday), in addition to the cumulative `psx_live.csv`.

## Tracked symbols

MARI, OGDC, PPL, POL, PSO, SNGP, SSGC, FFC, EFERT, FATIMA, ENGROH, COLG, LCI, HUBC, KAPCO, ATRL, PRL, NRL, LUCK, DGKC, MLCF, FCCL, CHCC, SYS, NETSOL, SAZEW, INDU, HCAR, AIRLINK, SEARL, AGP, NESTLE, ILP — plus KSE100 and KMI30.

Notes: Engro Corporation now trades as **ENGROH** (Engro Holdings), so that symbol is used. If a symbol is not found on the portal (for example KAPCO, which has faced delisting), its cell is left blank rather than guessed.

## Files

- `fetch_prices.py` — fetches and parses prices, appends to the CSV
- `.github/workflows/tracker.yml` — the schedule that runs it in the cloud
- `data/psx_live.csv` — the growing price history
- `index.html` — live chart dashboard for GitHub Pages

## Maintenance

GitHub pauses scheduled workflows after 60 days of no repository activity, but the tracker's own commits count as activity, so it keeps itself alive. If a run ever fails (red X in the Actions tab), it is usually a temporary PSX website issue; the next hourly run recovers automatically.
