/* ══════════════════════════════════════════════════════════════
   Laafi-Connect — offline keyword-search engine
   Loads offline-kb.json (a plain array of {id, keywords, response})
   and scores it against the user's question so the chatbot stays
   useful with zero network. To enrich the knowledge base later,
   just add more entries to offline-kb.json — no code changes needed.
═══════════════════════════════════════════════════════════════ */
const OfflineSearch = (() => {
  let _kb = [];
  let _ready = null;

  function normalize(s) {
    return String(s)
      .toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '') // strip accents
      .replace(/[^a-z0-9\s]/g, ' ')
      .trim();
  }

  async function load() {
    if (_ready) return _ready;
    _ready = fetch('js/offline-kb.json')
      .then((r) => r.json())
      .then((data) => { _kb = data; return _kb; })
      .catch(() => { _kb = []; return _kb; });
    return _ready;
  }

  function score(questionTokens, entry) {
    let s = 0;
    for (const kw of entry.keywords) {
      const kwNorm = normalize(kw);
      if (questionTokens.includes(kwNorm)) { s += 2; continue; }
      // partial match: keyword phrase appears as substring of the question
      if (questionTokens.join(' ').includes(kwNorm)) s += 1.5;
      // token starts-with match (handles simple French plural/conjugation drift)
      if (questionTokens.some((t) => t.length > 3 && kwNorm.length > 3 && t.startsWith(kwNorm.slice(0, 4)))) s += 0.5;
    }
    return s;
  }

  return {
    async search(question) {
      await load();
      const qNorm = normalize(question);
      const qTokens = qNorm.split(/\s+/).filter(Boolean);
      let best = null;
      let bestScore = 0;
      for (const entry of _kb) {
        const s = score(qTokens, entry);
        if (s > bestScore) { bestScore = s; best = entry; }
      }
      return bestScore >= 1.5 ? best : null;
    },

    async reload() {
      _ready = null;
      return load();
    },
  };
})();
