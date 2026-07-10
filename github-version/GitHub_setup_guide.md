# GitHub Setup — PSX Price Tracker (no account needed yet)

Total time: ~15 minutes. Everything is free. Once set up, GitHub's servers take a price snapshot every hour, 9 AM–4 PM PKT, Monday–Friday — your PC stays off.

## 1. Create a GitHub account
Go to https://github.com/signup and sign up with your email (anasilahikhan@gmail.com works fine). Pick any username — you'll use it in URLs later. Choose the **Free** plan.

## 2. Create a repository
- Click the **+** icon (top right) → **New repository**.
- Repository name: `psx-tracker`
- Visibility: **Public** is easiest (one-line loading in Colab). **Private** keeps the data to yourself — PSX's terms restrict republishing market data, so private is the safer choice; Colab access then needs a token (see step 6).
- Tick **Add a README file**, then click **Create repository**.

## 3. Upload the tracker script
- In your new repo, click **Add file → Upload files**.
- Drag in `tracker.py` (from this github-version folder).
- Click **Commit changes**.

## 4. Add the workflow file
This one must go in a special folder, so create it by hand:
- Click **Add file → Create new file**.
- In the filename box type exactly: `.github/workflows/psx.yml` (the slashes create the folders).
- Open `psx.yml` from this folder on your PC in Notepad, copy everything, paste it into the editor.
- Click **Commit changes**.

## 5. Test it
- Go to the **Actions** tab. If prompted, click **"I understand my workflows, enable them"**.
- Click **PSX price tracker** (left side) → **Run workflow** → green **Run workflow** button.
- Wait ~1 minute, refresh. A green check = success. `psx_live.csv` now exists in your repo with the first row.

From now on it runs automatically on schedule. Runs may start 5–15 minutes late (GitHub queues cron jobs) — the timestamp column always records the actual capture time.

## 6. Load the data in Google Colab

**Public repo** — one line (replace YOURUSERNAME):

```python
import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/YOURUSERNAME/psx-tracker/main/psx_live.csv")
```

**Private repo** — create a token first (GitHub → Settings → Developer settings → Personal access tokens → Fine-grained → give it read access to psx-tracker), then:

```python
import pandas as pd, requests, io
token = "YOUR_TOKEN"
url = "https://raw.githubusercontent.com/YOURUSERNAME/psx-tracker/main/psx_live.csv"
r = requests.get(url, headers={"Authorization": f"token {token}"})
df = pd.read_csv(io.StringIO(r.text))
```

## What you get
- `psx_live.csv` — one row per hour: Date, Time (PKT), OGDC, MARI, ENGROH, PSO, SYS, HUBC, FFC, KSE100, KMI30.
- `psx_week_ending_YYYY-MM-DD.csv` — created every Friday after the 4 PM snapshot, containing that week's rows.
- Full history: every snapshot is a git commit, so nothing is ever lost.

## Notes
- GitHub pauses schedules in repos with no activity for 60 days; the tracker's own commits keep it active, but if you ever see it stopped, the Actions tab has a one-click re-enable button.
- Symbols use PSX's current tickers — note Engro is **ENGROH** (Engro Holdings) since its 2025 restructuring, and Systems Ltd is **SYS**.
