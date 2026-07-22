from fastapi import APIRouter, Depends, Query

from .. import supabase_client
from ..deps import get_current_user

router = APIRouter(prefix="/doctors", tags=["doctors"])


@router.get("")
async def list_doctors(specialty: str | None = Query(default=None), user: dict = Depends(get_current_user)):
    params = {"select": "*"}
    if specialty:
        params["specialty"] = f"eq.{specialty}"
    res = await supabase_client.rest("GET", "doctors", use_service_role=True, params=params)
    if res.status_code >= 400:
        return []
    doctors = res.json()

    # look up this patient's treating doctor (stored on their profile row)
    treating_id = None
    prof_res = await supabase_client.rest(
        "GET", "profiles",
        access_token=user["_access_token"],
        params={"id": f"eq.{user['id']}", "select": "treating_doctor_id"},
    )
    if prof_res.status_code < 400:
        rows = prof_res.json()
        if rows:
            treating_id = rows[0].get("treating_doctor_id")

    for d in doctors:
        d["is_treating"] = d.get("id") == treating_id
    return doctors
