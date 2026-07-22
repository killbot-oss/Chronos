import json

import httpx
from fastapi import APIRouter, Depends, HTTPException

from .. import supabase_client
from ..config import get_settings
from ..deps import get_current_user
from ..schemas import DeviceRegisterIn

router = APIRouter(prefix="/notifications", tags=["notifications"])
settings = get_settings()


@router.post("/register-device")
async def register_device(body: DeviceRegisterIn, user: dict = Depends(get_current_user)):
    """Stores an FCM device token for this user so the backend can later
    push server-side alerts (e.g. new on-duty pharmacy, doctor availability).
    Medication reminders themselves are scheduled locally on-device (see
    frontend/www/js/notifications.js) so they keep working fully offline."""
    res = await supabase_client.rest(
        "POST", "device_tokens",
        access_token=user["_access_token"],
        json={"user_id": user["id"], "token": body.token, "platform": body.platform},
        prefer="resolution=merge-duplicates,return=minimal",
    )
    if res.status_code >= 400:
        raise HTTPException(status_code=502, detail="Erreur enregistrement device")
    return {"ok": True}


async def _get_fcm_access_token() -> str | None:
    """Exchanges the Firebase service account JSON for a short-lived OAuth2
    token used to call the FCM HTTP v1 API. Requires the `google-auth`
    package and FIREBASE_SERVICE_ACCOUNT_JSON to be set (see README)."""
    if not settings.FIREBASE_SERVICE_ACCOUNT_JSON:
        return None
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request

        info = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/firebase.messaging"]
        )
        creds.refresh(Request())
        return creds.token
    except Exception:
        return None


@router.post("/send-test")
async def send_test(user: dict = Depends(get_current_user)):
    """Sends a test push to every device registered for this user. No-op
    (returns a clear message) until FIREBASE_SERVICE_ACCOUNT_JSON is configured."""
    token = await _get_fcm_access_token()
    if not token:
        raise HTTPException(
            status_code=501,
            detail="Notifications push non configurées : ajoutez FIREBASE_SERVICE_ACCOUNT_JSON.",
        )

    settings_ = get_settings()
    info = json.loads(settings_.FIREBASE_SERVICE_ACCOUNT_JSON)
    project_id = info.get("project_id")

    res = await supabase_client.rest(
        "GET", "device_tokens",
        access_token=user["_access_token"],
        params={"user_id": f"eq.{user['id']}", "select": "token"},
    )
    devices = res.json() if res.status_code < 400 else []

    sent = 0
    async with httpx.AsyncClient(timeout=15) as client:
        for d in devices:
            payload = {
                "message": {
                    "token": d["token"],
                    "notification": {"title": "Laafi-Connect", "body": "Notification de test."},
                }
            }
            r = await client.post(
                f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
            )
            if r.status_code < 300:
                sent += 1
    return {"sent": sent, "total": len(devices)}
