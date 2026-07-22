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
        # Supabase requires email confirmation before issuing a session
        raise HTTPException(
            status_code=200,
            detail="Compte créé. Vérifiez votre email pour confirmer votre inscription avant de vous connecter.",
        )
    # create an empty profile row for this user (best effort)
    try:
        await supabase_client.rest(
            "POST", "profiles",
            access_token=session["access_token"],
            json={"id": session["user"]["id"], "full_name": body.full_name},
            prefer="return=minimal",
        )
    except Exception:
        pass
    return _to_auth_out(session)


@router.post("/login", response_model=AuthOut)
async def login(body: LoginIn):
    try:
        session = await supabase_client.sign_in(body.email, body.password)
    except supabase_client.SupabaseAuthError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
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
