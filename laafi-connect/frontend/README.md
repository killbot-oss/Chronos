# Laafi-Connect — Frontend

Same `www/index.html` app, deployed two ways:
1. As a website on **Vercel** (works in any browser, installable as a PWA).
2. Wrapped with **Capacitor** into a native **Android** app (what you'll
   ship first, per the plan).

Both share the exact same `www/` folder — no duplicate code to maintain.

## 1. Point the app at your backend

Edit `www/js/config.js`:

```js
window.LAAFI_CONFIG = {
  API_BASE_URL: 'https://laafi-connect-api.onrender.com/api/v1',
  API_HEALTH_URL: 'https://laafi-connect-api.onrender.com/health',
  USE_LOCAL_BACKEND: false,
};
```

Set `USE_LOCAL_BACKEND: true` while developing against a local
`uvicorn app.main:app --reload` — it overrides both URLs to `127.0.0.1:8000`.

## 2. Deploy the website on Vercel

```bash
cd frontend
npx vercel        # first deploy, follow the prompts
npx vercel --prod # subsequent production deploys
```

Or connect the repo in the Vercel dashboard, set **Root Directory** to
`frontend`, and it picks up `vercel.json` (static, `outputDirectory: www`)
automatically. No build step needed — it's plain HTML/CSS/JS.

Once live, go back into `backend/.env` (or Render's Environment settings)
and add this Vercel URL to `ALLOWED_ORIGINS` so the backend accepts
requests from it.

## 3. Package the Android app with Capacitor

```bash
cd frontend
npm install
npx cap add android      # generates the android/ native project
npx cap sync android      # copies www/ into the native project + installs plugins
npx cap open android      # opens Android Studio
```

From Android Studio: **Build → Generate Signed Bundle/APK** to produce a
release build, or just **Run** on a device/emulator during development.

### Local notifications (medication reminders)

Already wired in `www/js/notifications.js` via
`@capacitor/local-notifications` (listed in `package.json`). After
`npx cap sync android`, Capacitor generates the Android manifest
permissions automatically. No extra setup needed for these to work fully
offline.

### App icon / splash screen

Not included here — drop your branding into `android/app/src/main/res/`
after `cap add android`, or use `npx @capacitor/assets generate` with a
source icon/splash image once you have final artwork.

### Login-once-then-offline behavior

`www/js/app-overrides.js` hides the "Continuer hors-ligne" shortcut on the
auth screen until the user has logged in at least once successfully on that
device (flag stored in `localStorage`). After that first login, the app can
be opened and used offline indefinitely — the cached Supabase session token
is reused, and any vitals recorded offline queue in IndexedDB and sync
automatically once the network is back.

## 4. Push notifications (optional, not required for reminders)

Medication reminders work offline without this. If you later want
server-triggered pushes (e.g. "new pharmacy on duty near you"):

1. Create a Firebase project, add an Android app with the same `appId`
   (`bf.laafi.connect`), download `google-services.json` into
   `android/app/`.
2. `npm install @capacitor/push-notifications` and wire registration in
   `notifications.js` (currently only local notifications are implemented).
3. Generate a Firebase service account key and set it as
   `FIREBASE_SERVICE_ACCOUNT_JSON` on the backend (see backend README).
