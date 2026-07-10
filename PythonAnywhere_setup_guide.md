# PythonAnywhere Setup — PSX Price Tracker

Runs in the cloud, so your PC can stay off. One daily task starts at 8:50 AM PKT and snapshots prices every hour from 9 AM to 4 PM, Monday–Friday.

## 1. Create account
Sign up free at https://www.pythonanywhere.com (a "Beginner" account is fine to start).

## 2. Upload the script
- Go to the **Files** tab.
- Upload `psx_tracker.py` to your home directory (`/home/YOURUSERNAME/`).

## 3. Test internet access (important)
Free accounts can only reach whitelisted websites. Check whether PSX is reachable — open a **Bash console** and run:

```bash
python3 -c "import requests; print(requests.get('https://dps.psx.com.pk/market-watch', timeout=30).status_code)"
```

- **200** → you're good, continue to step 4.
- **403 / ProxyError** → PSX is not whitelisted. Either:
  - email support@pythonanywhere.com asking them to whitelist `dps.psx.com.pk` (it's a public data portal — they often agree), or
  - upgrade to the $5/month "Hacker" plan, which has unrestricted internet.

## 4. Do a test run
In the same Bash console:

```bash
python3 psx_tracker.py
```

On a weekday during market hours it will wait for the next full hour, then print `appended: [...]`. You can stop it with Ctrl+C after the first snapshot and check `psx_live.csv` in the Files tab. (On a weekend it just prints "weekend" and exits.)

## 5. Schedule it
- Go to the **Tasks** tab.
- Create a daily task at **03:50 UTC** (= 8:50 AM Pakistan time) with the command:

```bash
python3 /home/YOURUSERNAME/psx_tracker.py
```

Replace `YOURUSERNAME` with your actual username.

## 6. Getting the data
- `psx_live.csv` grows with every snapshot; `psx_week_ending_YYYY-MM-DD.csv` is created each Friday after 4 PM.
- Download files anytime from the **Files** tab, then upload to Google Colab. Or read them in a Colab cell after downloading:

```python
import pandas as pd
df = pd.read_csv("psx_live.csv", parse_dates=["Date"])
df.head()
```

## Known free-tier limits
- Only one scheduled task per day — that's why the script loops internally instead of being scheduled hourly.
- Free tasks are occasionally killed if they run very long. If you notice afternoon snapshots missing, the $5/month plan's "always-on tasks" solve it.
- Free accounts expire if unused for ~3 months — log in occasionally.

## Symbols tracked
OGDC, MARI, ENGROH (Engro Holdings — new symbol after Engro's 2025 restructuring), PSO, SYS (Systems Ltd), HUBC, FFC, plus KSE-100 and KMI-30 indices.
