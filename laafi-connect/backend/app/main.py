from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routes import ai_chat, auth, doctors, notifications, pharmacies, profile, vitals

settings = get_settings()

app = FastAPI(title="Laafi-Connect API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(profile.router, prefix=API_PREFIX)
app.include_router(vitals.router, prefix=API_PREFIX)
app.include_router(pharmacies.router, prefix=API_PREFIX)
app.include_router(doctors.router, prefix=API_PREFIX)
app.include_router(ai_chat.router, prefix=API_PREFIX)
app.include_router(notifications.router, prefix=API_PREFIX)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"service": "Laafi-Connect API", "docs": "/docs"}
