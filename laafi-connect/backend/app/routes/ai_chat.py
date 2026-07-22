import httpx
from fastapi import APIRouter, Depends, HTTPException

from ..config import get_settings
from ..deps import get_current_user
from ..schemas import ChatIn, ChatOut

router = APIRouter(prefix="/ai", tags=["ai"])
settings = get_settings()

PATH_LABELS = {
    "diabete": "Diabète type 2",
    "hta": "Hypertension",
    "asthme": "Asthme",
    "cardio": "Insuff. cardiaque",
    "rein": "IRC (Rein)",
    "multi": "Poly-pathologie",
}

SYSTEM_TEMPLATE = (
    "Tu es un assistant santé bienveillant pour un patient atteint de {patho}, au Burkina Faso. "
    "Dernières constantes connues : {vitals}. "
    "Donne des informations claires, prudentes et rassurantes, en français simple. "
    "Rappelle systématiquement qu'un professionnel de santé doit être consulté pour tout "
    "diagnostic ou changement de traitement. Réponds en 3 à 5 phrases courtes maximum."
)


def _build_context(body: ChatIn) -> str:
    patho = PATH_LABELS.get(body.pathology or "", "pathologie non renseignée")
    vitals = ", ".join(f"{k}: {v}" for k, v in (body.last_vitals or {}).items()) or "aucune constante"
    return SYSTEM_TEMPLATE.format(patho=patho, vitals=vitals)


async def _call_gemini(system: str, message: str, history: list[dict]) -> str | None:
    if not settings.GEMINI_API_KEY:
        return None
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
    )
    contents = []
    for h in history[-8:]:
        role = "user" if h.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [{"text": h.get("content", "")}]})
    contents.append({"role": "user", "parts": [{"text": message}]})
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 400, "temperature": 0.4},
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            res = await client.post(url, json=payload)
        if res.status_code >= 400:
            return None
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None


async def _call_groq(system: str, message: str, history: list[dict]) -> str | None:
    if not settings.GROQ_API_KEY:
        return None
    url = "https://api.groq.com/openai/v1/chat/completions"
    messages = [{"role": "system", "content": system}]
    for h in history[-8:]:
        messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": message})
    payload = {"model": settings.GROQ_MODEL, "messages": messages, "max_tokens": 400, "temperature": 0.4}
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}", "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            res = await client.post(url, json=payload, headers=headers)
        if res.status_code >= 400:
            return None
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


@router.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn, user: dict = Depends(get_current_user)):
    system = _build_context(body)

    reply = await _call_gemini(system, body.message, body.history)
    if reply:
        return ChatOut(reply=reply, provider="gemini")

    reply = await _call_groq(system, body.message, body.history)
    if reply:
        return ChatOut(reply=reply, provider="groq")

    raise HTTPException(status_code=503, detail="Aucun fournisseur IA disponible pour le moment")
