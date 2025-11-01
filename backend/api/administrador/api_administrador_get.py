# Rutas FASTAPI para autenticación de administrador
from fastapi import APIRouter, Request, HTTPException

from backend.db.crud.crud_prompt import obtener_prompt
from backend.db.crud.crud_analista import obtener_analistas
from backend.db.crud.crud_cliente import obtener_clientes
from backend.db.crud.crud_servicio import obtener_servicios
from backend.db.crud.crud_cliente_servicio import obtener_servicios_clientes
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
    nombre: str
    email: str
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

@admin_get_router.post("/administrador/analistas")
def obtenerAnalistas(req: Request):
    with conectarORM() as db:
        try:
            analistas = obtener_analistas(db)
            data = [Analista.model_validate(a).model_dump() for a in analistas]
            return {"analistas": data}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.post("/administrador/clientes")
def obtenerClientes(req: Request):
    with conectarORM() as db:
        try:
            clientes = obtener_clientes(db)
            data = [Cliente.model_validate(c).model_dump() for c in clientes]
            return {"clientes": data}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.post("/administrador/servicios")
def obtenerServicios(req: Request):
    with conectarORM() as db:
        try:
            servicios = obtener_servicios(db)
            data = [Servicio.model_validate(s).model_dump() for s in servicios]
            return {"servicios": data}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.post("/administrador/servicios_clientes")
def obtenerServiciosClientes(req: Request, id_cliente: str):
    with conectarORM() as db:
        try:
            servicios_clientes = obtener_servicios_clientes(db, id_cliente)
            return {"servicios_clientes": servicios_clientes}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")