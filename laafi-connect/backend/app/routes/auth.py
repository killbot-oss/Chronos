from fastapi import APIRouter, HTTPException

from .. import supabase_client
from ..schemas import AuthOut, LoginIn, LogoutIn, RefreshIn, RegisterIn

router = APIRouter(prefix="/auth", tags=["auth"])


def _to_auth_out(session: dict) -> AuthOut:
    return AuthOut(
        access_token=session["access_token"],
        refresh_token=session["refresh_token"],
        user_id=session["user"]["id"],
    )


@router.post("/register", response_model=AuthOut)
async def register(body: RegisterIn):
    try:
        session = await supabase_client.sign_up(body.email, body.password, body.full_name)
    except supabase_client.SupabaseAuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    if not session.get("access_token"):
        # Supabase requires email confirmation before issuing a session.
        # Use a non-2xx status so the frontend doesn't mistake this for a
        # successful login and try to save a session that doesn't exist.
        raise HTTPException(
            status_code=202,
            detail="Compte créé. Vérifiez votre email pour confirmer votre inscription avant de vous connecter.",
        )
    try:
        await supabase_client.ensure_profile(session["access_token"], session["user"]["id"], body.full_name)
    except Exception:
        pass
    return _to_auth_out(session)


@router.post("/login", response_model=AuthOut)
async def login(body: LoginIn):
    try:
        session = await supabase_client.sign_in(body.email, body.password)
    except supabase_client.SupabaseAuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    try:
        await supabase_client.ensure_profile(session["access_token"], session["user"]["id"], None)
    except Exception:
        pass
    return _to_auth_out(session)


@router.post("/refresh")
async def refresh(body: RefreshIn):
    try:
        session = await supabase_client.refresh_session(body.refresh_token)
    except supabase_client.SupabaseAuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return {"access_token": session["access_token"], "refresh_token": session["refresh_token"]}


@router.post("/logout")
async def logout(body: LogoutIn):
    # Best effort - Supabase revokes the refresh token family
    try:
        session = await supabase_client.refresh_session(body.refresh_token)
        await supabase_client.sign_out(session["access_token"])
    except Exception:
        pass
    return {"ok": True}
