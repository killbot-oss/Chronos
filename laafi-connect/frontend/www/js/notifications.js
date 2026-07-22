/* ══════════════════════════════════════════════════════════════
   Laafi-Connect — notifications
   Medication reminders are scheduled LOCALLY on the device via the
   Capacitor Local Notifications plugin, so they keep firing even
   with zero network. This requires:
     npm install @capacitor/local-notifications
     npx cap sync android
   Falls back to a no-op on plain web (e.g. testing in a desktop
   browser) so the rest of the app keeps working.

   Server-sent push (FCM) for things like "new pharmacy on duty near
   you" is scaffolded separately in the backend
   (/api/v1/notifications/register-device) — wire it up once you add
   a Firebase project; not required for medication reminders.
═══════════════════════════════════════════════════════════════ */
const LaafiNotifications = (() => {
  function getPlugin() {
    return window.Capacitor && window.Capacitor.Plugins && window.Capacitor.Plugins.LocalNotifications;
  }

  async function ensurePermission() {
    const plugin = getPlugin();
    if (!plugin) return false;
    const perm = await plugin.checkPermissions();
    if (perm.display !== 'granted') {
      const req = await plugin.requestPermissions();
      return req.display === 'granted';
    }
    return true;
  }

  // Deterministic small int id from a medication's name+time so re-scheduling
  // the same reminder overwrites it instead of duplicating.
  function idFor(name, time) {
    const str = `${name}_${time}`;
    let h = 0;
    for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) & 0x7fffffff;
    return h % 100000;
  }

  return {
    async init() {
      const ok = await ensurePermission();
      return ok;
    },

    /* Schedules a daily repeating reminder for one medication time slot,
       e.g. scheduleMedReminder('Metformine', '08:00', '500mg'). */
    async scheduleMedReminder(name, time, dose) {
      const plugin = getPlugin();
      if (!plugin) return false;
      const [h, m] = time.split(':').map((n) => parseInt(n, 10) || 0);
      await plugin.schedule({
        notifications: [{
          id: idFor(name, time),
          title: 'Rappel médicament — Laafi-Connect',
          body: `${name}${dose ? ' · ' + dose : ''} — c'est l'heure de votre prise.`,
          schedule: { on: { hour: h, minute: m }, repeats: true, allowWhileIdle: true },
          smallIcon: 'ic_stat_laafi',
        }],
      });
      return true;
    },

    async cancelMedReminder(name, time) {
      const plugin = getPlugin();
      if (!plugin) return false;
      await plugin.cancel({ notifications: [{ id: idFor(name, time) }] });
      return true;
    },

    /* Re-syncs every reminder from the current `meds` array (call after any
       add/edit/delete so scheduled notifications never drift from the list). */
    async rescheduleAll(meds) {
      const plugin = getPlugin();
      if (!plugin) return;
      const pending = await plugin.getPending();
      if (pending.notifications.length) {
        await plugin.cancel({ notifications: pending.notifications.map((n) => ({ id: n.id })) });
      }
      for (const med of meds) {
        for (const t of med.times || []) {
          await this.scheduleMedReminder(med.name, t, med.dose);
        }
      }
    },
  };
})();
