from math import atan2, cos, radians, sin, sqrt

from fastapi import APIRouter, Query

from .. import supabase_client

router = APIRouter(prefix="/pharmacies", tags=["pharmacies"])


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


@router.get("")
async def list_pharmacies(
    on_duty: bool = Query(default=False),
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
):
    params = {"select": "*"}
    if on_duty:
        params["on_duty"] = "eq.true"
    res = await supabase_client.rest("GET", "pharmacies", use_service_role=True, params=params)
    if res.status_code >= 400:
        return []
    data = res.json()
    if lat is not None and lon is not None:
        for p in data:
            if p.get("lat") is not None and p.get("lon") is not None:
                p["distance_km"] = round(_haversine_km(lat, lon, p["lat"], p["lon"]), 2)
        data.sort(key=lambda p: p.get("distance_km", 9999))
    return data
