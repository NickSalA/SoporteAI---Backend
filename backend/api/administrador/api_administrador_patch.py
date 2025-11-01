from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from pydantic import BaseModel

from backend.db.crud.crud_prompt import actualizar_prompt
from backend.util.util_conectar_orm import conectarORM

admin_patch_router = APIRouter()

class PromptContent(BaseModel):
    identidadObjetivos: Optional[str] = None
    reglasComunicacion: Optional[str] = None
    flujoTrabajo: Optional[str] = None
    formatoBusquedas: Optional[str] = None
    formatoTickets: Optional[str] = None
    plantillaRespuesta: Optional[str] = None

@admin_patch_router.patch("/administrador/prompt")
def actualizarPrompt(req: Request, contenido: PromptContent):

    with conectarORM() as db:
        try:
            actualizar_prompt(db, contenido.model_dump(exclude_none=True), 1)
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    req.session["overrides"] = contenido.model_dump(exclude_none=True)
    return {"ok": True, "overrides": contenido.model_dump(exclude_none=True)}