from typing import Any, Optional
from pydantic import BaseModel, EmailStr


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class LogoutIn(BaseModel):
    refresh_token: str


class AuthOut(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str


class ProfileIn(BaseModel):
    name: Optional[str] = None
    pathology: Optional[str] = None
    stade: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    dob: Optional[str] = None
    avatar: Optional[str] = None


class VitalsSyncIn(BaseModel):
    # list of vitals recorded locally (offline-first), pushed once back online
    vitals: list[dict[str, Any]]


class ChatIn(BaseModel):
    message: str
    history: list[dict[str, str]] = []
    pathology: Optional[str] = None
    last_vitals: Optional[dict[str, Any]] = None


class ChatOut(BaseModel):
    reply: str
    provider: str


class DeviceRegisterIn(BaseModel):
    token: str
    platform: str = "android"
