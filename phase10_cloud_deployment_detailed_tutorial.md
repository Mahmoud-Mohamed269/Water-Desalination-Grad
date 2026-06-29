# 🚀 Vercel Deployment — Detailed Walkthrough

---

## 🧰 What You Need Before Starting

- [ ] Your project folder: `d:\Projects\Arduino Projects\Water Desalination`
- [ ] The file `backend\serviceAccountKey.json` exists (downloaded from Firebase Console)
- [ ] A [GitHub](https://github.com) account (free)
- [ ] A [Vercel](https://vercel.com) account (free — sign in with GitHub)

---

## Step 1 — Encode the Firebase Service Account

Vercel cannot read files on your hard drive. Instead, you convert `serviceAccountKey.json` into a single long text string (base64) and paste it as an environment variable.

### Open PowerShell in the project folder

Right-click the folder `d:\Projects\Arduino Projects\Water Desalination` in File Explorer → **"Open in Terminal"**

### Run this exact command:

```powershell
[Convert]::ToBase64String(
    [IO.File]::ReadAllBytes("backend\serviceAccountKey.json")
) | Set-Clipboard
```

> **What happens:** The entire contents of `serviceAccountKey.json` get encoded and silently copied to your clipboard. Nothing will print — that's correct. The encoded string will be several hundred characters long.

### Verify it worked

```powershell
# Paste and check the first 50 characters
[Convert]::ToBase64String(
    [IO.File]::ReadAllBytes("backend\serviceAccountKey.json")
) | ForEach-Object { $_.Substring(0, 50) }
```

You should see something like: `ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsC...`

> [!IMPORTANT]
> **Save this string somewhere safe** (e.g., a temporary Notepad file) before proceeding. You'll paste it into Vercel in Step 5. If you close the terminal, run the command again to re-copy it.

---

## Step 2 — Push the Project to GitHub

### 2.1 Initialize Git (if not already done)

```powershell
cd "d:\Projects\Arduino Projects\Water Desalination"
git init
```

If git is already initialized, skip to 2.2.

### 2.2 Safety check — make sure secrets are excluded

```powershell
git status
```

**Look at the output carefully.** You should NOT see any of these files listed:
- `backend/serviceAccountKey.json`
- `backend/.env`
- `*.sqlite` or `*.db`

If you see them, your `.gitignore` isn't working — stop and check it before continuing.

### 2.3 Stage and commit everything

```powershell
git add .
git commit -m "Phase 10: Vercel deployment ready"
```

### 2.4 Create a GitHub repository

1. Go to **[github.com/new](https://github.com/new)**
2. Repository name: `water-desalination` (or any name)
3. Set to **Private** (recommended — protects your code)
4. Click **"Create repository"**
5. GitHub shows you a page with setup commands. Copy the remote URL — it looks like:
   ```
   https://github.com/YOUR_USERNAME/water-desalination.git
   ```

### 2.5 Connect and push

```powershell
git remote add origin https://github.com/YOUR_USERNAME/water-desalination.git
git branch -M main
git push -u origin main
```

You'll be prompted for your GitHub username and password (or a personal access token if you have 2FA enabled).

> ✅ **Success check:** Refresh your GitHub repo page — you should see all the project files listed, including `backend/`, `mobile/`, `README.md`, etc.

---

## Step 3 — Create a Vercel Account

1. Go to **[vercel.com](https://vercel.com)**
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"** — this lets Vercel access your repos directly
4. Authorize Vercel on GitHub when prompted
5. On the Vercel dashboard, you'll see **"No projects yet"**

---

## Step 4 — Import the Project into Vercel

### 4.1 Click "Add New… → Project"

In the top-right of the Vercel dashboard, click the **"Add New…"** button → select **"Project"**

### 4.2 Import from GitHub

- Vercel shows a list of your GitHub repos
- Find **`water-desalination`** and click **"Import"**

### 4.3 Configure the project — this is the critical step

You'll see a **"Configure Project"** screen. Fill it in exactly as follows:

| Setting | Value |
|---|---|
| **Project Name** | `water-desalination` (or any name) |
| **Framework Preset** | `Other` |
| **Root Directory** | Click **"Edit"** → type `backend` → click **"Continue"** |
| **Build Command** | Leave blank (auto-detected) |
| **Output Directory** | Leave blank |
| **Install Command** | Leave blank (Vercel auto-runs `pip install -r requirements.txt`) |

> [!IMPORTANT]
> Setting **Root Directory = `backend`** is crucial. It tells Vercel to deploy only the `backend/` subfolder where `vercel.json` and `main.py` are. If you skip this, Vercel will try to deploy the entire project root and fail.

### What it looks like after setting Root Directory:

```
Root Directory: backend ✓
  ├── main.py            ← Vercel's entry point
  ├── vercel.json        ← Deployment config
  ├── requirements.txt   ← Dependencies
  ├── app/               ← FastAPI app
  └── ml/                ← .pkl model files
```

---

## Step 5 — Set Environment Variables

**Do not click "Deploy" yet.** Scroll down to the **"Environment Variables"** section on the same Configure Project screen.

Add each variable one at a time by clicking **"Add"**:

---

### Variable 1: `FIREBASE_DATABASE_URL`

- **Name:** `FIREBASE_DATABASE_URL`
- **Value:** Your Firebase RTDB URL

**How to find it:**
1. Go to [console.firebase.google.com](https://console.firebase.google.com)
2. Select your project
3. Left menu → **"Realtime Database"**
4. At the top of the page, copy the URL — it looks like:
   ```
   https://water-desalination-8638c-default-rtdb.europe-west1.firebasedatabase.app
   ```

---

### Variable 2: `FIREBASE_SERVICE_ACCOUNT_BASE64`

- **Name:** `FIREBASE_SERVICE_ACCOUNT_BASE64`
- **Value:** Paste the base64 string you copied in Step 1

> [!IMPORTANT]
> This is a very long string. Paste the **entire** thing. It starts with `eyJ` and ends with a `=` or `==`. Make sure there are no spaces or line breaks.

---

### Variable 3: `GEMINI_API_KEY`

- **Name:** `GEMINI_API_KEY`
- **Value:** Your Gemini API key

**How to find it:**
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **"Get API Key"** in the top menu
3. Copy the key (starts with `AQ.` or `AI...`)

---

### Variable 4: `API_KEY`

- **Name:** `API_KEY`
- **Value:** `aquamonitor-secret-key-2024`

> This is your custom key that protects the `/ingest` endpoint. You can use any value — just keep it secret and remember it.

---

### After adding all 4 variables, check the boxes:

Make sure all 4 variables have these environments checked:
- ✅ Production
- ✅ Preview
- ✅ Development

---

## Step 6 — Deploy

Click the **"Deploy"** button.

### What happens during the build (watch the logs):

```
[10:00] Cloning github.com/YOUR_USERNAME/water-desalination...
[10:02] Detected Python project
[10:02] Running: pip install -r requirements.txt
[10:15] Installing: fastapi, uvicorn, firebase-admin, scikit-learn...
[10:45] Build completed
[10:46] Deploying...
[10:47] ✅ Deployment ready!
```

> The build takes **1–3 minutes** — the ML packages (`scikit-learn`, `firebase-admin`) are large.

### Success screen

You'll see a **confetti animation** and your deployment URL:
```
🎉 Congratulations!
https://water-desalination-abc123.vercel.app
```

**Copy this URL** — you'll need it in Step 8.

---

## Step 7 — Verify the Deployment

Open your browser and test each URL. Replace `your-project` with your actual Vercel URL.

### ✅ Test 1 — Root health check
```
https://your-project.vercel.app/
```
**Expected:**
```json
{"message": "Water Desalination API is running.", "docs": "/docs"}
```

### ✅ Test 2 — API documentation
```
https://your-project.vercel.app/docs
```
**Expected:** A Swagger UI page showing all your endpoints. Click on any `GET` endpoint → "Try it out" → "Execute" to test live.

### ✅ Test 3 — Live sensor data
```
https://your-project.vercel.app/api/v1/sensors/live
```
**Expected:**
```json
{"status": "ok", "data": {"ph_feed": 7.2, "tds_feed": 300, ...}}
```
or `{"status": "no_data"}` if the hardware hasn't pushed recently.

### ✅ Test 4 — ML prediction (run from browser)
```
https://your-project.vercel.app/api/v1/predict/run
```
**Expected:**
```json
{
  "status": "ok",
  "predictions": {
    "water_quality": {"label": "good", "confidence": 94.2},
    "membrane_status": {"label": "good", "confidence": 87.5}
  }
}
```

### ✅ Test 5 — Security check (use PowerShell)

Without the API key — should be rejected:
```powershell
Invoke-RestMethod -Uri "https://your-project.vercel.app/api/v1/sensors/ingest" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"ph_feed": 7.2}'
```
**Expected:** `403 Forbidden` — `"Invalid or missing API key"`

With the correct key — should succeed:
```powershell
$headers = @{ "X-API-Key" = "aquamonitor-secret-key-2024" }
Invoke-RestMethod -Uri "https://your-project.vercel.app/api/v1/sensors/ingest" `
  -Method POST `
  -ContentType "application/json" `
  -Headers $headers `
  -Body '{"ph_feed": 7.2, "tds_feed": 300}'
```
**Expected:** `{"status": "ok", "timestamp": "2026-..."}`

---

## Step 8 — Update the Mobile App

Now that the backend is live in the cloud, point the mobile app to it.

1. Run the mobile app:
   ```powershell
   cd "d:\Projects\Arduino Projects\Water Desalination\mobile\src"
   python main.py
   ```
2. Click the **Settings** tab (gear icon, bottom right)
3. In **"FastAPI Backend URL"**, clear the current value and type:
   ```
   https://your-project.vercel.app
   ```
4. Click **"Save Settings"**
5. The app will now sync data to the cloud backend — even when you're not on your home WiFi

---

## Step 9 — Update CORS (Final Step)

Now that you know your Vercel URL, add it to the CORS whitelist so the web dashboard can call the API from a browser.

Open `backend/main.py` and update:

```python
ALLOWED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
    "https://your-project.vercel.app",   # ← Add YOUR actual URL here
]
```

Then commit and push:
```powershell
cd "d:\Projects\Arduino Projects\Water Desalination"
git add backend/main.py
git commit -m "Add Vercel URL to CORS whitelist"
git push
```

> Vercel will automatically detect the push and redeploy within ~90 seconds. No manual action needed.

---

## 🎉 You're Done!

Your backend is now:
- ✅ Running 24/7 on Vercel (free tier)
- ✅ Accessible from anywhere in the world
- ✅ Protected with an API key on write endpoints
- ✅ Automatically redeploying on every `git push`

**Your live API URL:** `https://your-project.vercel.app`  
**Interactive docs:** `https://your-project.vercel.app/docs`

---

## 🔧 If Something Goes Wrong

| Problem | What to check |
|---|---|
| Build fails at `pip install` | Check `backend/requirements.txt` has `pydantic-settings>=2.2.0` |
| "No module named X" error | The module is missing from `requirements.txt` — add it and push again |
| Firebase 403 / credential error | The base64 string was truncated — re-encode and update the env var in Vercel dashboard |
| All endpoints return 500 | Check **Function Logs** in Vercel dashboard → your project → Deployments → click latest → Logs |
| ML model not found | Verify `backend/ml/*.pkl` files are committed to Git (not in `.gitignore`) |

### How to view live error logs on Vercel:
1. Go to [vercel.com](https://vercel.com) → your project
2. Click **"Deployments"** tab
3. Click the latest deployment
4. Click **"Functions"** → click any function name
5. Click **"Logs"** — shows real-time errors
