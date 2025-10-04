# Rutas FASTAPI para autenticación de analistas
from fastapi import APIRouter, Request, HTTPException

# Google OAuth
from google.oauth2 import id_token
from google.auth.transport import requests as grequests

# ORM
from backend.util.util_conectar_orm import conectarORM

# CRUD
from backend.db.persona.create_analista import insertar_analista

# Helpers
from backend.util.util_key import obtenerAPI
from pydantic import BaseModel

auth_analista_router = APIRouter()
class LoginIn(BaseModel):
    id_token: str

def _assert_gmail(email: str):
    if not email or "@" not in email:
        raise HTTPException(401, "email_missing_in_token")
    if email.split("@")[-1].lower() != "gmail.com":
        raise HTTPException(403, f"solo se permite acceso con cuentas @gmail.com (email: {email})")

@auth_analista_router.post("/google/analista")
def google_analista(req: Request, body: LoginIn):
    idt = body.id_token
    if not idt:
        raise HTTPException(400, "missing id_token")

    client_id = obtenerAPI("CONF-CLIENT-GOOGLE-ID")
    if not client_id:
        raise HTTPException(500, "server_misconfig: GOOGLE_CLIENT_ID missing")

    try:
        info = id_token.verify_oauth2_token(idt, grequests.Request(), client_id)
        if info.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
            raise HTTPException(401, "invalid_google_token: bad_iss")
        if info.get("aud") != client_id:
            raise HTTPException(401, "invalid_google_token: aud_mismatch")
    except Exception as e:
        raise HTTPException(401, f"invalid_google_token: {e}")

    if not info.get("email_verified", True):
        raise HTTPException(403, "email_not_verified")

    email = info.get("email")
    _assert_gmail(email)

    sub   = info["sub"]
    name  = info.get("name") or (email.split("@")[0] if email else None)
    hd    = info.get("hd")
    
    # suele venir None para gmail.com
    with conectarORM() as db:
        out = insertar_analista(db, sub=sub, email=email, name=name, hd=hd)

    req.session["user"] = {
        "email": email,
        "name": name,
        "persona_id": out["persona_id"],
        "analista_id": out["analista_id"],
        "rol": "analista",
        "nivel": out.get("nivel"),
    }
    return {"ok": True, **out}
