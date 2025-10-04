from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from backend.flow.AgentAsTools import AgentsAsTools
from backend.util.util_conectar_orm import obtenerSesion
chat_router = APIRouter()

class ChatIn(BaseModel):
    mensaje: str

@chat_router.post("/user/chat")
def chat(req: Request, body: ChatIn):
    user = obtenerSesion(req)
    if not user or not user.get("persona_id"):
        raise HTTPException(401, "unauthorized")

    saver = getattr(req.app.state, "checkpointer", None)
    if saver is None:
        raise HTTPException(500, "server_config: checkpointer ausente")

    orq = AgentsAsTools(user=user, saver=saver)
    # Aseguramos que el thread_id quede persistido en la sesión
    if user.get("thread_id") != orq.user.get("thread_id"):
        user["thread_id"] = orq.user.get("thread_id")
        req.session["user"] = user
    try:
        respuesta = orq.enviarMensaje(body.mensaje)
    except Exception as e:
        raise HTTPException(500, f"Error al enviar mensaje: {e}")

    # Si la respuesta es un diccionario con estructura de ticket, devolverla completa
    if isinstance(respuesta, dict) and respuesta.get('type') == 'ticket':
        return respuesta
    
    # Si es una respuesta normal, usar el formato anterior
    return {"respuesta": respuesta}

@chat_router.post("/user/reset")
def reset(req: Request):
    user = req.session.get("user")
    if not user or not user.get("persona_id"):
        raise HTTPException(401, "unauthorized")
    
    saver = getattr(req.app.state, "checkpointer", None)
    if saver is None:
        raise HTTPException(500, "server_config: checkpointer ausente")
    
    orq = AgentsAsTools(user=user, saver=saver)
    try:
        user["thread_id"] = orq.agenteOrquestador.reiniciarMemoria()
        req.session["user"] = user
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, f"Error al reiniciar memoria: {e}")