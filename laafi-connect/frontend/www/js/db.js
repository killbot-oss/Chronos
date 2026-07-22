/* ══════════════════════════════════════════════════════════════
   Laafi-Connect — local database (IndexedDB)
   Small offline-first store: everything the user records while
   offline (vitals, med checks) is written here immediately and
   queued for sync. When the app detects a network connection AND
   a valid session, LaafiDB.flushQueue() pushes the queue to the
   backend, which upserts on the client-generated local_id so
   re-sending never creates duplicates.
═══════════════════════════════════════════════════════════════ */
const LaafiDB = (() => {
  const DB_NAME = 'laafi_connect_db';
  const DB_VERSION = 1;
  let _db = null;

  function open() {
    if (_db) return Promise.resolve(_db);
    return new Promise((resolve, reject) => {
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains('vitals_queue')) {
          db.createObjectStore('vitals_queue', { keyPath: 'local_id' });
        }
        if (!db.objectStoreNames.contains('kv')) {
          db.createObjectStore('kv', { keyPath: 'key' });
        }
      };
      req.onsuccess = (e) => { _db = e.target.result; resolve(_db); };
      req.onerror = () => reject(req.error);
    });
  }

  function tx(store, mode) {
    return open().then((db) => db.transaction(store, mode).objectStore(store));
  }

  function uuid() {
    return 'v_' + Date.now().toString(36) + '_' + Math.random().toString(36).slice(2, 9);
  }

  return {
    /* Queue a vital reading recorded while offline (or online — always
       queue, then flush; this keeps a single code path). */
    async queueVital(entry) {
      const store = await tx('vitals_queue', 'readwrite');
      const record = {
        local_id: uuid(),
        type: entry.type,
        value: entry.values || entry.value,
        recorded_at: entry.recorded_at || new Date().toISOString(),
        note: entry.note || '',
      };
      return new Promise((resolve, reject) => {
        const req = store.add(record);
        req.onsuccess = () => resolve(record);
        req.onerror = () => reject(req.error);
      });
    },

    async getQueuedVitals() {
      const store = await tx('vitals_queue', 'readonly');
      return new Promise((resolve, reject) => {
        const req = store.getAll();
        req.onsuccess = () => resolve(req.result || []);
        req.onerror = () => reject(req.error);
      });
    },

    async clearQueuedVitals(localIds) {
      const store = await tx('vitals_queue', 'readwrite');
      localIds.forEach((id) => store.delete(id));
    },

    /* Flush the queue to the backend. Call this after login and whenever
       connectivity is (re)detected. Safe to call repeatedly. */
    async flushQueue(apiSyncFn) {
      const queued = await this.getQueuedVitals();
      if (!queued.length) return { synced: 0 };
      try {
        const result = await apiSyncFn(queued);
        if (result) {
          await this.clearQueuedVitals(queued.map((q) => q.local_id));
          return { synced: queued.length };
        }
      } catch (_) { /* stays queued, will retry next time */ }
      return { synced: 0 };
    },

    async kvSet(key, value) {
      const store = await tx('kv', 'readwrite');
      store.put({ key, value });
    },

    async kvGet(key) {
      const store = await tx('kv', 'readonly');
      return new Promise((resolve) => {
        const req = store.get(key);
        req.onsuccess = () => resolve(req.result ? req.result.value : null);
        req.onerror = () => resolve(null);
      });
    },
  };
})();
