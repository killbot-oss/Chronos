# Laafi-Connect

Suivi santé + accès aux soins, pensé pour fonctionner **hors-ligne d'abord**
au Burkina Faso. Android en premier, packagé avec Capacitor.

```
laafi-connect/
├── backend/          FastAPI (Python) → deploy on Render
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── deps.py             # auth dependency (validates Supabase JWT)
│   │   ├── supabase_client.py  # Supabase Auth + PostgREST HTTP wrapper
│   │   ├── schemas.py
│   │   └── routes/
│   │       ├── auth.py         # register / login / refresh / logout
│   │       ├── profile.py
│   │       ├── vitals.py       # offline-first sync (local_id dedupe)
│   │       ├── pharmacies.py   # distance-sorted, on-duty filter
│   │       ├── doctors.py
│   │       ├── ai_chat.py      # Gemini → Groq fallback
│   │       └── notifications.py # FCM push scaffold
│   ├── supabase/
│   │   ├── schema.sql          # tables + RLS policies
│   │   └── seed.sql            # real pharmacy/doctor data
│   ├── requirements.txt / render.yaml / Procfile / .env.example
│   └── README.md
│
└── frontend/          Static HTML/JS → deploy on Vercel + wrap with Capacitor
    ├── www/
    │   ├── index.html          # the app (your original file, patched)
    │   ├── manifest.json
    │   └── js/
    │       ├── config.js       # <- set your Render URL here
    │       ├── db.js           # IndexedDB local store + sync queue
    │       ├── offline-kb.json # offline chatbot knowledge base (editable)
    │       ├── offline-search.js
    │       ├── notifications.js # local med reminders (Capacitor)
    │       └── app-overrides.js # wires it all together
    ├── capacitor.config.json
    ├── package.json
    ├── vercel.json
    └── README.md
```

## Deploy order (each step unblocks the next)

1. **Supabase** — create project, run `backend/supabase/schema.sql` then
   `seed.sql` in the SQL editor. Copy your Project URL + anon key + service
   role key.
2. **Render (backend)** — deploy the `backend/` folder (Blueprint via
   `render.yaml`, or a manual Web Service), set env vars from
   `backend/.env.example` (Supabase keys + your Gemini/Groq keys). Note the
   public URL Render gives you (e.g. `https://laafi-connect-api.onrender.com`).
3. **Frontend config** — put that Render URL into
   `frontend/www/js/config.js`.
4. **Vercel (frontend)** — deploy `frontend/` (root directory `frontend`,
   output `www`, no build step). Add the resulting Vercel URL to the
   backend's `ALLOWED_ORIGINS` env var and redeploy the backend.
5. **Capacitor (Android)** — `cd frontend && npm install && npx cap add
   android && npx cap sync android && npx cap open android`, build/run from
   Android Studio.

Full detail for each step is in `backend/README.md` and `frontend/README.md`.

## How the "offline-first" pieces fit together

- **Login once, then offline** — a real Supabase login/register is required
  the first time the app is opened after install. After that, the session
  is cached and the app opens straight into offline mode with no network
  needed (`frontend/www/js/app-overrides.js`).
- **Local data + background sync** — vitals recorded offline are written to
  IndexedDB (`js/db.js`) with a client-generated id, then flushed to
  `/api/v1/vitals/sync` as soon as the network + session are available. The
  backend upserts on that id, so a retried sync never duplicates a reading.
- **Offline AI chatbot fallback** — when there's no connection (or the user
  toggles "Hors-ligne"), the chatbot answers from a local keyword-scored
  search over `js/offline-kb.json` instead of calling the AI provider. This
  is intentionally just a starting knowledge base — add more entries to
  that JSON file any time to make it smarter; no code changes required.
- **Online AI chatbot** — when online, the backend tries **Gemini** first,
  falls back to **Groq** (Llama 3.3) if Gemini fails, using the API keys
  you already have.
- **Medication reminders** — scheduled locally on-device via Capacitor's
  Local Notifications plugin, so they keep firing with zero connectivity.
  Server-triggered push (Firebase Cloud Messaging) is scaffolded on the
  backend for later, non-reminder use cases (e.g. "pharmacy X now on
  duty near you") — needs a Firebase project before it'll actually send.

## What's stubbed vs. what's real

**Real and working:** auth, profile, offline-first vitals sync with
dedup, pharmacy distance sorting, doctor listing, AI chat with automatic
provider fallback, offline keyword chatbot, local medication reminders,
Row-Level-Security-protected Supabase schema with seed data ported from
your original mock arrays.

**Stubbed, ready to extend:** server-push notifications (needs a Firebase
project + service account key), app icon/splash artwork (needs your
branding files), "forgot password" flow (still client-side only in the
original HTML — move it to Supabase's real password-reset email flow when
ready).
