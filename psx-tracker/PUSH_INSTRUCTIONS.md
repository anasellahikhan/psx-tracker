# One-time setup: put the tracker on GitHub (about 10 minutes)

After this one-time push, everything runs automatically in GitHub's cloud — your PC can stay off.

## Option A - GitHub Desktop (easiest, no commands)

1. Install **GitHub Desktop** from https://desktop.github.com and sign in with your GitHub account.
2. In GitHub Desktop: **File → Clone repository**, pick `anasellahikhan/psx-tracker`, and clone it (note the folder location it chooses).
3. Open the cloned folder in File Explorer and copy **everything inside** `Desktop\Agents\PSX 6 stocks\psx-tracker` into it — including the `.github` folder (if you can't see it, enable **View → Show → Hidden items** in File Explorer).
4. Back in GitHub Desktop you'll see the new files listed. Type a message like `Initial tracker` in the Summary box → click **Commit to main** → click **Push origin**.

## Option B - Command line (if you have Git installed)

Open Command Prompt and run:

```
cd "C:\Users\Anas\Desktop\Agents\PSX 6 stocks\psx-tracker"
git init
git add .
git commit -m "Initial tracker"
git branch -M main
git remote add origin https://github.com/anasellahikhan/psx-tracker.git
git push -u origin main
```

(A browser window will pop up asking you to log in to GitHub the first time.)

## After pushing - 3 clicks to switch it on

1. Go to https://github.com/anasellahikhan/psx-tracker/actions — if you see a button to enable workflows, click it.
2. Click **PSX Price Tracker** in the left sidebar → **Run workflow** → **Run workflow** (green button). This is a manual test run; after ~1 minute it should show a green check. (If today is a market holiday it will correctly record nothing — that's the holiday protection working.)
3. Optional, for the live dashboard: go to **Settings → Pages**, under "Branch" choose `main` and `/ (root)`, click **Save**. After a few minutes your dashboard is live at https://anasellahikhan.github.io/psx-tracker/

That's it. From now on it records prices every hour, 9 AM-4 PM PKT, Monday-Friday, skips public holidays, and saves a weekly file every Friday at 4 PM.

## Optional cleanup

Your old hourly task on this PC (the one updating `psx_live.csv` in this folder) is no longer needed once GitHub is running — tell Claude "delete my psx hourly scheduled task" whenever you're ready.
