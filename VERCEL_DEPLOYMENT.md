# Deploying to Vercel (Hobby / free plan)

This app now has two run modes with the **same source code**:

| Mode | Database | How to run |
| --- | --- | --- |
| Local (unchanged) | `research.db` (SQLite) | `python server.py` → http://127.0.0.1:8000 |
| Vercel serverless | Neon Postgres via `DATABASE_URL` | Push to GitHub and import the repo in Vercel |

Vercel Functions have a **read-only filesystem**, so the local `research.db`
cannot be used there. When `DATABASE_URL` is present, `app/data.py` uses
Postgres instead; the seed catalog, accounts, imports, and history are created
automatically in Postgres on the first request.

## 1. Push the project

This folder is not currently a git repository. Initialise one and push it to
GitHub/GitLab/Bitbucket:

```powershell
git init
git add .
git commit -m "Add Vercel serverless deployment"
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

## 2. Import into Vercel

1. Go to https://vercel.com/new and import the repository.
2. Select the **Hobby** (free) plan.
3. Framework preset: **Other**. Build command and output directory can be left
   empty — `vercel.json` already maps:
   - `/` → `static/index.html`
   - `/app.js`, `/style.css` → the files in `static/`
   - `/api/*` → the Python function `api/index.py`
4. The Python runtime installs `requirements.txt` automatically.

## 3. Add a free database

Vercel no longer provides its own Postgres. Use the free Neon integration:

1. In the Vercel project, open **Storage → Create Database → Neon Postgres**
   (Marketplace integration, Free plan).
2. Connect it to the project. Vercel injects a connection string; this app reads
   `DATABASE_URL` first, then `POSTGRES_URL`, then `NEON_DATABASE_URL`.
3. If your integration uses a different variable name, add `DATABASE_URL`
   manually under **Settings → Environment Variables** and paste the Neon
   pooled connection string. Apply it to **Production** (and Preview if you
   want preview deployments to work).

No database file needs to be uploaded — `research.db` stays local only.

## 4. Environment variables

Under **Settings → Environment Variables**:

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | Neon Postgres connection string (usually injected by the integration) |
| `GOOGLE_CLIENT_ID` | No | Enables the Gmail button |
| `GOOGLE_CLIENT_SECRET` | No | Enables the Gmail button |
| `GOOGLE_REDIRECT_URI` | Recommended with Gmail | `https://<your-project>.vercel.app/api/auth/google/callback` |

If the Google variables are absent, the Gmail button is hidden and local
username/email + password login still works.

For Gmail, add the production callback URL to the **Authorized redirect URIs**
in Google Cloud Console. See `GOOGLE_SIGNIN_SETUP.md`.

## 5. First-run admin

Open `https://<your-project>.vercel.app`, choose **Create admin account**, and
fill in username, email, and password. The first account is the administrator;
later accounts are regular users. This is stored in Postgres, so it survives
function restarts and redeploys.

## 6. Important limits on Hobby

- Non-commercial, personal use only.
- Serverless functions have no persistent local disk. CSV imports and history
  are stored in Postgres, not on disk.
- `api/index.py` sets a 60-second function duration; Shamela (30s) and Dorar
  (20s) calls may take most of that on a slow network.
- Neon Free scales to zero after inactivity, so the first request after a pause
  can be slower.
- Shamela and Dorar are queried live; neither corpus is bundled or copied.
- Do not expect the deployed demo to handle heavy traffic. Hobby pauses a
  feature for 30 days if its included usage is exceeded.

## 7. Verify a deployment

```text
GET  https://<your-project>.vercel.app/api/health        → {"status":"ok"}
GET  https://<your-project>.vercel.app/                  → the app UI
POST https://<your-project>.vercel.app/api/dorar/search  → 4 Dorar results
```

The `Origin` check accepts same-origin `https` requests on the deployed host
and same-origin `http` requests on localhost. Session cookies gain the `Secure`
flag automatically outside localhost.

## 8. Local development after deploying

Nothing changes. Without `DATABASE_URL`, `python server.py` keeps using
`research.db`. To test the production data path locally:

```powershell
$env:DATABASE_URL = "postgresql://user:pass@host/db?sslmode=require"
python server.py
```
