from fastapi import Header, HTTPException

from . import supabase_client


async def get_current_user(authorization: str = Header(default="")) -> dict:
    """Extracts 'Bearer <token>' from the Authorization header, validates it
    against Supabase Auth, and returns the user record (contains 'id', 'email')."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Non authentifié")
    token = authorization.removeprefix("Bearer ").strip()
    user = await supabase_client.get_user(token)
    user["_access_token"] = token
    return user
