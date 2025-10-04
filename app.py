# FastAPI para SoporteAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Lifespan
from contextlib import asynccontextmanager

# Servidor ASGI
import uvicorn

# Routers
from backend.api.auth.api_auth_colaborador import auth_colab_router
from backend.api.auth.api_auth_analista import auth_analista_router
from backend.api.analista.api_analista_get import analista_get_router
from backend.api.analista.api_analista_patch import analista_patch_router
from backend.api.usuario.api_root import chat_router

# Utilitario de conexión al checkpointer
from backend.util.util_base_de_datos import obtenerConexionBaseDeDatos 

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn, saver = obtenerConexionBaseDeDatos() 
    app.state.conn = conn
    app.state.checkpointer = saver
    print("Checkpointer listo:", type(saver).__name__ if saver else None)
    try:
        yield
    finally:
        try:
            if getattr(app.state, "conn", None) is not None:
                app.state.conn.__exit__(None, None, None)  # #type: ignore
        except Exception:
            pass

app = FastAPI(title="IAnalytics API", lifespan=lifespan)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:9002",
]

# CORS (ajusta origins a tu front real)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cookie de sesión
app.add_middleware(
    SessionMiddleware,
    secret_key="cambia-esto-en-prod",
    same_site="lax",  
    https_only=False,   # pon True en producción HTTPS
    # session_cookie="support_session",
)

# Routers
app.include_router(auth_colab_router,     prefix="/auth",       tags=["auth"])
app.include_router(auth_analista_router,  prefix="/auth",       tags=["auth"])
app.include_router(chat_router,                                 tags=["chat"])
app.include_router(analista_get_router,                         tags=["analista"])
app.include_router(analista_patch_router,                       tags=["analista"])

@app.get("/")
def home():
    return {"ok": True, "msg": "API de IA activa. Usa POST /user/chat"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True, log_level="debug")