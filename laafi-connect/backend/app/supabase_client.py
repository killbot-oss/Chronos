"""
Thin wrapper around Supabase's HTTP APIs (Auth + PostgREST).
We talk to Supabase over plain httpx instead of the supabase-py SDK to keep
the backend lightweight and avoid SDK version churn.

Auth:   {SUPABASE_URL}/auth/v1/...
Data:   {SUPABASE_URL}/rest/v1/...   (PostgREST, respects Row Level Security)
"""
import httpx
from fastapi import HTTPException

from .config import get_settings

settings = get_settings()


def _auth_headers(extra: dict | None = None) -> dict:
    h = {"apikey": settings.SUPABASE_ANON_KEY, "Content-Type": "application/json"}
    if extra:
        h.update(extra)
    return h


def _service_headers() -> dict:
    # Service role key bypasses RLS - used for server-side trusted operations
    # (e.g. reading public pharmacies/doctors tables, admin writes).
    return {
        "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }


class SupabaseAuthError(Exception):
    def __init__(self, detail: str, status_code: int = 400):
        self.detail = detail
        self.status_code = status_code


async def sign_up(email: str, password: str, full_name: str | None) -> dict:
    url = f"{settings.SUPABASE_URL}/auth/v1/signup"
    payload = {"email": email, "password": password, "data": {"full_name": full_name}}
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.post(url, headers=_auth_headers(), json=payload)
    if res.status_code >= 400:
        raise SupabaseAuthError(res.json().get("msg") or res.json().get("error_description") or "Erreur inscription", res.status_code)
    return res.json()


async def sign_in(email: str, password: str) -> dict:
    url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password"
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.post(url, headers=_auth_headers(), json={"email": email, "password": password})
    if res.status_code >= 400:
        raise SupabaseAuthError(res.json().get("error_description") or "Identifiants invalides", 401)
    return res.json()


async def refresh_session(refresh_token: str) -> dict:
    url = f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=refresh_token"
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.post(url, headers=_auth_headers(), json={"refresh_token": refresh_token})
    if res.status_code >= 400:
        raise SupabaseAuthError("Session expirée", 401)
    return res.json()


async def sign_out(access_token: str) -> None:
    url = f"{settings.SUPABASE_URL}/auth/v1/logout"
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, headers=_auth_headers({"Authorization": f"Bearer {access_token}"}))


async def get_user(access_token: str) -> dict:
    """Validate an access token and return the Supabase auth user."""
    url = f"{settings.SUPABASE_URL}/auth/v1/user"
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(url, headers=_auth_headers({"Authorization": f"Bearer {access_token}"}))
    if res.status_code >= 400:
        raise HTTPException(status_code=401, detail="Session invalide")
    return res.json()


async def rest(
    method: str,
    table: str,
    *,
    access_token: str | None = None,
    params: dict | None = None,
    json: dict | list | None = None,
    use_service_role: bool = False,
    prefer: str | None = None,
) -> httpx.Response:
    """Generic PostgREST call. Pass the user's access_token to run as that
    user (subject to RLS), or use_service_role=True for trusted server reads
    (e.g. public reference data like pharmacies/doctors)."""
    url = f"{settings.SUPABASE_URL}/rest/v1/{table}"
    if use_service_role:
        headers = _service_headers()
    else:
        headers = _auth_headers({"Authorization": f"Bearer {access_token}"} if access_token else None)
    if prefer:
        headers["Prefer"] = prefer
    async with httpx.AsyncClient(timeout=15) as client:
        return await client.request(method, url, headers=headers, params=params, json=json)
