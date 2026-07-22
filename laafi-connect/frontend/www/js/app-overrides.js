/* ══════════════════════════════════════════════════════════════
   Laafi-Connect — app overrides
   Loaded AFTER the main inline <script> in index.html so it can
   safely override the functions defined there (same pattern the
   original file already uses for its own online/offline overrides).
═══════════════════════════════════════════════════════════════ */

/* ── 1. LOGIN REQUIRED ONCE ─────────────────────────────────────
   The "Continuer hors-ligne" shortcut on the auth screen is only
   shown once the user has successfully logged in at least once on
   this device. First run always requires a real login/registration;
   every run after that can use offline mode freely because a
   session is already cached (API.loggedIn). */
(function gateOfflineSkip() {
  const btn = Array.from(document.querySelectorAll('.btn-secondary'))
    .find((b) => b.getAttribute('onclick') === 'skipAuth()');
  if (!btn) return;
  const onboarded = localStorage.getItem('cc_onboarded') === '1';
  btn.style.display = onboarded ? '' : 'none';
})();

const _origSubmitAuth = submitAuth;
submitAuth = async function () {
  await _origSubmitAuth();
  if (API.loggedIn) {
    localStorage.setItem('cc_onboarded', '1');
    LaafiDB.flushQueue((rows) => API.syncVitals(rows));
    if (window.LaafiNotifications) LaafiNotifications.init().then(() => LaafiNotifications.rescheduleAll(meds));
  }
};

/* ── 2. OFFLINE-FIRST VITALS: queue locally, sync when possible ── */
const _origSaveVital = saveVital;
saveVital = function () {
  const type = document.getElementById('vitalType').value;
  let values = {};
  if (type === 'ta') {
    const sys = parseFloat(document.getElementById('vSys').value);
    const dia = parseFloat(document.getElementById('vDia').value);
    if (sys && dia) values = { ta_sys: sys, ta_dia: dia };
  } else {
    const val = parseFloat(document.getElementById('vSingle').value);
    if (!isNaN(val)) values = { [type]: val };
  }
  // Run the original (keeps all existing local-state / UI rendering behavior)
  _origSaveVital();
  // Additionally queue for backend sync, best-effort
  if (Object.keys(values).length) {
    LaafiDB.queueVital({ type, values }).then(() => {
      if (API.online && API.loggedIn) {
        LaafiDB.flushQueue((rows) => API.syncVitals(rows));
      }
    });
  }
};

/* ── 3. OFFLINE CHAT: keyword-search engine instead of naive includes() ── */
repondreOffline = async function (question) {
  const entry = await OfflineSearch.search(question);
  if (entry) {
    const d = appendRaw(markdownLite(entry.response), 'msg-bot');
    const tag = document.createElement('div');
    tag.className = 'source-tag src-offline';
    tag.innerHTML = '<i class="ti ti-database" style="font-size:10px"></i> Base locale';
    d.appendChild(tag);
  } else {
    appendRaw(
      "Je n'ai pas trouvé de réponse dans ma base locale.<br><br>Activez le mode <strong>En ligne</strong> pour une réponse personnalisée via l'IA.",
      'msg-bot'
    );
  }
};

/* ── 4. MEDICATION REMINDERS: keep local notifications in sync ── */
const _origToggleMed = toggleMed;
toggleMed = function (i) {
  _origToggleMed(i);
  if (window.LaafiNotifications) LaafiNotifications.rescheduleAll(meds);
};

const _origOpenAddMed = openAddMed;
openAddMed = function () {
  _origOpenAddMed();
  if (window.LaafiNotifications) LaafiNotifications.rescheduleAll(meds);
};

/* ── 5. Flush any queued vitals whenever we detect connectivity ── */
window.addEventListener('online', () => {
  if (API.loggedIn) LaafiDB.flushQueue((rows) => API.syncVitals(rows));
});

/* ── 6. Init notifications once the main app is entered ────────── */
const _origEnterMainApp = enterMainApp;
enterMainApp = function () {
  _origEnterMainApp();
  if (window.LaafiNotifications) {
    LaafiNotifications.init().then((granted) => {
      if (granted) LaafiNotifications.rescheduleAll(meds);
    });
  }
  if (API.loggedIn) LaafiDB.flushQueue((rows) => API.syncVitals(rows));
};
