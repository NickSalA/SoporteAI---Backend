# Rutas FASTAPI para autenticación de administrador
from fastapi import APIRouter, Request, HTTPException

from backend.db.crud.crud_prompt import obtener_prompt
from backend.db.crud.crud_analista import obtener_analistas
from typing import Optional
from pydantic import BaseModel

from backend.util.util_conectar_orm import conectarORM

admin_get_router = APIRouter()

class PromptContent(BaseModel):
    # Bloques opcionales: solo incluyes lo que quieras overridear
    identidadObjetivos: Optional[str] = None
    reglasComunicacion: Optional[str] = None
    flujoTrabajo: Optional[str] = None
    formatoBusquedas: Optional[str] = None
    formatoTickets: Optional[str] = None
    plantillaRespuesta: Optional[str] = None

class Analista(BaseModel):
    id_analista: str
    nivel: int
class Cliente(BaseModel):
    id_cliente: str
    nombre: str
class Servicio(BaseModel):
    id_servicio: str
    nombre: str

@admin_get_router.post("/administrador/prompt")
def obtenerPrompt(req: Request):

    with conectarORM() as db:
        contenido = obtener_prompt(db) or {}
        try:
            # Validar y dividir el JSON en el modelo Pydantic
            prompt = PromptContent.model_validate(contenido)
        except Exception as e:
            raise HTTPException(500, f"Contenido Invalido: {e}")

    # Guardamos un dict JSON-serializable (no el modelo) y sin None
    req.session["overrides"] = prompt.model_dump(exclude_none=True)

    return {"ok": True, "overrides": req.session["overrides"]}

@admin_get_router.get("/administrador/analistas")
def obtenerAnalistas(req: Request):
    with conectarORM() as db:
        try:
            analistas = obtener_analistas(db)
            return {"analistas": analistas}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")
        
@admin_get_router.get("/administrador/analista/{analista_id}")
def obtenerAnalista(analista_id: str, req: Request):
    with conectarORM() as db:
        try:
            analista = obtener_analista(db, analista_id)
            return {"analista": analista}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.get("/administrador/clientes")
def obtenerClientes(req: Request):
    with conectarORM() as db:
        try:
            clientes = obtener_clientes(db)
            return {"clientes": clientes}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.get("/administrador/cliente/{cliente_id}")
def obtenerCliente(cliente_id: str, req: Request):
    with conectarORM() as db:
        try:
            cliente = obtener_cliente(db, cliente_id)
            return {"cliente": cliente}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.get("/administrador/servicios")
def obtenerServicios(req: Request):
    with conectarORM() as db:
        try:
            servicios = obtener_servicios(db)
            return {"servicios": servicios}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.get("/administrador/servicio/{servicio_id}")