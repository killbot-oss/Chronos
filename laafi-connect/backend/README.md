# Laafi-Connect — Backend (FastAPI, deploy on Render)

Thin API layer between the app and Supabase. Auth and user data live in
Supabase (Postgres + Auth); this backend adds business logic:
distance-sorted pharmacies, AI chat proxy (Gemini → Groq fallback), and a
push-notification device registry.

## 1. Set up Supabase

1. Create a project at https://supabase.com.
2. Open **SQL Editor** and run `supabase/schema.sql`, then `supabase/seed.sql`.
3. Go to **Settings → API** and copy: `Project URL`, `anon public` key,
   `service_role` key (keep this one secret, backend-only).
4. (Recommended) In **Authentication → Providers → Email**, you can disable
   "Confirm email" for faster testing, or leave it on for production.

## 2. Local run

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in the values
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000/docs for the interactive API docs.

## 3. Deploy on Render

**Option A — Blueprint (fastest):**

1. Push this repo to GitHub (or GitLab/Bitbucket).
2. On https://dashboard.render.com → **New → Blueprint**, point it at your
   repo. Render reads `backend/render.yaml` automatically and creates the
   web service (root dir `backend`, build `pip install -r requirements.txt`,
   start `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
3. Render will prompt you to fill in the env vars marked `sync: false`
   (Supabase keys, Gemini/Groq keys, `ALLOWED_ORIGINS`) — same values as
   `.env.example`.
4. Deploy. Note your public URL (e.g. `https://laafi-connect-api.onrender.com`)
   — you'll put this in the frontend's `js/config.js`.

**Option B — Manual web service:**

1. On https://dashboard.render.com → **New → Web Service** → connect your repo.
2. Set **Root Directory** to `backend`.
3. **Runtime**: Python 3. **Build Command**: `pip install -r requirements.txt`.
4. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. **Health Check Path**: `/health`.
6. Add all vars from `.env.example` under **Environment**.
7. Create Web Service — Render builds and gives you the public URL.

Note: Render's free tier spins down after inactivity, so the first request
after idling can take ~30-50s to respond. Fine for testing; upgrade the
plan before real users depend on it.

## AI chat

Tries **Gemini** first (`GEMINI_API_KEY`), falls back to **Groq**
(`GROQ_API_KEY`, Llama 3.3) if Gemini is unavailable. If neither key is set
or both fail, the endpoint returns 503 and the app falls back to its local
offline keyword-search engine automatically.

## Push notifications

Medication reminders are scheduled **on-device** (Capacitor Local
Notifications) so they work fully offline — no server needed for those.

`/api/v1/notifications/register-device` and `/send-test` are scaffolded for
real server-sent push (e.g. "new pharmacy on duty near you") via Firebase
Cloud Messaging, but need a Firebase project + `FIREBASE_SERVICE_ACCOUNT_JSON`
before they'll actually send anything — wire this up when you're ready to
add server-triggered notifications.

## Data model

See `supabase/schema.sql`. Vitals sync is offline-first: the client keeps a
local `local_id` per reading (generated while offline) and `POST
/api/v1/vitals/sync` upserts on `(user_id, local_id)` so re-sending the same
batch after a dropped connection never creates duplicates.
