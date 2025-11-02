# Rutas FASTAPI para autenticación de administrador
from fastapi import APIRouter, Request, HTTPException

from backend.db.crud.crud_prompt import obtener_prompt
from backend.db.crud.crud_analista import obtener_analistas
from backend.db.crud.crud_cliente import obtener_clientes
from backend.db.crud.crud_servicio import obtener_servicios
from backend.db.crud.crud_cliente_servicio import obtener_servicios_clientes
from typing import Optional
from pydantic import BaseModel, ConfigDict

from backend.util.util_conectar_orm import conectarORM
import uuid

admin_get_router = APIRouter()

class PromptContent(BaseModel):
    # Bloques opcionales: solo incluyes lo que quieras overridear
    identidadObjetivos: Optional[str] = None
    reglasComunicacion: Optional[str] = None
    flujoTrabajo: Optional[str] = None
    formatoBusquedas: Optional[str] = None
    formatoTickets: Optional[str] = None
    plantillaRespuesta: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
class AnalistaModel(BaseModel):
    id_analista: uuid.UUID | None = None
    nombre: str
    email: str
    nivel: int
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
class Cliente(BaseModel):
    id_cliente: uuid.UUID | None = None
    nombre: str
    model_config = ConfigDict(from_attributes=True, use_enum_values=True    )
class Servicio(BaseModel):
    id_servicio: uuid.UUID | None = None
    nombre: str
    model_config = ConfigDict(from_attributes=True)

@admin_get_router.get("/administrador/prompt")
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
def obtenerAnalistas():
    with conectarORM() as db:
        try:
            analistas = obtener_analistas(db)
            data = [AnalistaModel.model_validate(a).model_dump() for a in analistas]
            print(data)
            return {"analistas": data}

        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.get("/administrador/clientes")
def obtenerClientes():
    with conectarORM() as db:
        try:
            clientes = obtener_clientes(db)
            data = [
                {
                    "id_cliente": str(c.id),
                    "nombre": c.nombre or "",
                }
                for c in clientes
            ]
            return {"clientes": data}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.get("/administrador/servicios")
def obtenerServicios():
    with conectarORM() as db:
        try:
            servicios = obtener_servicios(db)
            data = [
                {
                    "id_servicio": str(s.id),
                    "nombre": s.nombre or "",
                }
                for s in servicios
            ]
            return {"servicios": data}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_get_router.get("/administrador/servicios_clientes")
def obtenerServiciosClientes(id_cliente: str):
    with conectarORM() as db:
        try:
            servicios_clientes = obtener_servicios_clientes(db, id_cliente)
            return {"servicios_clientes": servicios_clientes}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")