from fastapi import APIRouter, Depends, HTTPException

from .. import supabase_client
from ..deps import get_current_user
from ..schemas import ProfileIn

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("")
async def get_profile(user: dict = Depends(get_current_user)):
    res = await supabase_client.rest(
        "GET", "profiles",
        access_token=user["_access_token"],
        params={"id": f"eq.{user['id']}", "select": "*"},
    )
    if res.status_code >= 400:
        raise HTTPException(status_code=502, detail="Erreur lecture profil")
    rows = res.json()
    return rows[0] if rows else {}


@router.put("")
async def save_profile(body: ProfileIn, user: dict = Depends(get_current_user)):
    payload = {k: v for k, v in body.model_dump().items() if v is not None}
    payload["id"] = user["id"]
    res = await supabase_client.rest(
        "POST", "profiles",
        access_token=user["_access_token"],
        json=payload,
        prefer="resolution=merge-duplicates,return=representation",
    )
    if res.status_code >= 400:
        raise HTTPException(status_code=502, detail="Erreur sauvegarde profil")
    rows = res.json()
    return rows[0] if rows else payload
