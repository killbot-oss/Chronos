/* ══════════════════════════════════════════════════════════════
   Laafi-Connect — runtime config
   Edit API_BASE_URL after you deploy the backend to Render, e.g:
     const API_BASE_URL = 'https://laafi-connect-api.onrender.com/api/v1';
   Keep the localhost value for local development against
   `uvicorn app.main:app --reload`.
═══════════════════════════════════════════════════════════════ */
window.LAAFI_CONFIG = {
  API_BASE_URL: 'https://chronos-nc82.onrender.com/api/v1',
  API_HEALTH_URL: 'https://chronos-nc82.onrender.com/health',
  // Set to true while developing locally with `uvicorn` on your machine.
  USE_LOCAL_BACKEND: false,
};

if (window.LAAFI_CONFIG.USE_LOCAL_BACKEND) {
  window.LAAFI_CONFIG.API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
  window.LAAFI_CONFIG.API_HEALTH_URL = 'http://127.0.0.1:8000/health';
}
