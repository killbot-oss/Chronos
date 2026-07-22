from fastapi import APIRouter, Depends, HTTPException

from .. import supabase_client
from ..deps import get_current_user
from ..schemas import VitalsSyncIn

router = APIRouter(prefix="/vitals", tags=["vitals"])


@router.post("/sync")
async def sync_vitals(body: VitalsSyncIn, user: dict = Depends(get_current_user)):
    """Accepts a batch of vitals recorded while offline (each with a client-
    generated local_id) and upserts them. Returns the synced rows so the
    client can mark its local queue as flushed."""
    rows = []
    for v in body.vitals:
        rows.append({
            "user_id": user["id"],
            "local_id": v.get("local_id"),
            "type": v.get("type"),
            "value": v.get("value"),
            "recorded_at": v.get("recorded_at"),
        })
    if not rows:
        return {"synced": 0, "rows": []}

    res = await supabase_client.rest(
        "POST", "vitals",
        access_token=user["_access_token"],
        json=rows,
        prefer="resolution=merge-duplicates,return=representation",
    )
    if res.status_code >= 400:
        raise HTTPException(status_code=502, detail="Erreur synchronisation")
    saved = res.json()
    return {"synced": len(saved), "rows": saved}


@router.get("")
async def list_vitals(user: dict = Depends(get_current_user)):
    res = await supabase_client.rest(
        "GET", "vitals",
        access_token=user["_access_token"],
        params={"user_id": f"eq.{user['id']}", "select": "*", "order": "recorded_at.desc", "limit": "200"},
    )
    if res.status_code >= 400:
        raise HTTPException(status_code=502, detail="Erreur lecture constantes")
    return res.json()
