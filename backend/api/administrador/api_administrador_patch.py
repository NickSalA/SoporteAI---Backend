from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from pydantic import BaseModel, ConfigDict
from fastapi import Query

from backend.db.crud.crud_prompt import actualizar_prompt
from backend.db.crud.crud_servicio import crear_servicio, eliminar_servicio, actualizar_servicio, obtener_servicio_nombre
from backend.db.crud.crud_cliente import crear_cliente, eliminar_cliente, actualizar_cliente
from backend.db.crud.crud_analista import eliminar_analista, actualizar_analista
from backend.db.crud.crud_cliente_servicio import actualizar_servicios_clientes
from backend.util.util_conectar_orm import conectarORM
from backend.util.util_overrides import set_overrides
import uuid

admin_patch_router = APIRouter()

class PromptContent(BaseModel):
    identidadObjetivos: Optional[str] = None
    reglasComunicacion: Optional[str] = None
    flujoTrabajo: Optional[str] = None
    formatoBusquedas: Optional[str] = None
    formatoTickets: Optional[str] = None
    plantillaRespuesta: Optional[str] = None

class AnalistaModel(BaseModel):
    id: uuid.UUID | None = None
    nombre: str
    email: str
    nivel: int
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
class Cliente(BaseModel):
    id: uuid.UUID | None = None
    nombre: str
    dominio: str
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
class Servicio(BaseModel):
    id: uuid.UUID | None = None
    nombre: str
    model_config = ConfigDict(from_attributes=True)

@admin_patch_router.patch("/administrador/prompt")
def actualizarPrompt(req: Request, contenido: PromptContent):

    with conectarORM() as db:
        try:
            actualizar_prompt(db, contenido.model_dump(exclude_none=True), 1)
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    cleaned = contenido.model_dump(exclude_none=True)
    req.session["overrides"] = cleaned
    # Actualizamos cache en memoria
    set_overrides(req.app, cleaned)
    return {"ok": True, "overrides": cleaned}

@admin_patch_router.post("/administrador/servicio/crear")
def crearServicio(payload: Servicio):
    with conectarORM() as db:
        try:
            if obtener_servicio_nombre(db, payload.nombre):
                raise HTTPException(400, f"El servicio con nombre '{payload.nombre}' ya existe.")
            servicio = crear_servicio(db, payload.nombre)
            
            # Convertir a diccionario serializable
            data = {
                "id_servicio": str(servicio.id),
                "nombre": servicio.nombre or "",
            }
            return {"ok": True, "servicio": data}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")


@admin_patch_router.patch("/administrador/servicio/actualizar")
def actualizarServicio(id_servicio: str, nombre: str):
    with conectarORM() as db:
        try:
            actualizado = actualizar_servicio(db, id_servicio, nombre)
            if not actualizado:
                raise HTTPException(404, f"Servicio {id_servicio} no encontrado")
            
            # Convertir a diccionario serializable
            data = {
                "id_servicio": str(actualizado.id),
                "nombre": actualizado.nombre or "",
            }
            return {"ok": True, "servicio": data}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")


@admin_patch_router.delete("/administrador/servicio/eliminar")
def eliminarServicio(id_servicio: str):
    with conectarORM() as db:
        try:
            eliminado = eliminar_servicio(db, id_servicio)
            if not eliminado:
                raise HTTPException(404, f"Servicio {id_servicio} no encontrado")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    return {"ok": True, "mensaje": f"Servicio {id_servicio} eliminado correctamente"}

@admin_patch_router.post("/administrador/cliente/crear")
def crearCliente(nombre: str, dominio: str):
    with conectarORM() as db:
        try:
            cliente = crear_cliente(db, nombre, dominio)
            
            # Convertir a diccionario serializable
            data = {
                "id_cliente": str(cliente.id),
                "nombre": cliente.nombre or "",
                "dominio": cliente.dominio or "",
            }
            return {"ok": True, "cliente": data}
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_patch_router.patch("/administrador/cliente/actualizar")
def actualizarCliente(id_cliente: str, nombre: str, dominio: str):
    with conectarORM() as db:
        try:
            actualizado = actualizar_cliente(db, id_cliente, nombre, dominio)
            if not actualizado:
                raise HTTPException(404, f"Cliente {id_cliente} no encontrado")
            
            # Convertir a diccionario serializable
            data = {
                "id_cliente": str(actualizado.id),
                "nombre": actualizado.nombre or "",
                "dominio": actualizado.dominio or "",
            }
            return {"ok": True, "cliente": data}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_patch_router.delete("/administrador/cliente/eliminar")
def eliminarCliente(id_cliente: str):
    with conectarORM() as db:
        try:
            eliminado = eliminar_cliente(db, id_cliente)
            if not eliminado:
                raise HTTPException(404, f"Cliente {id_cliente} no encontrado")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    return {"ok": True, "mensaje": f"Cliente {id_cliente} eliminado correctamente"}

@admin_patch_router.delete("/administrador/analista/eliminar")
def eliminarAnalista(id_analista: str):
    with conectarORM() as db:
        try:
            eliminado = eliminar_analista(db, id_analista)
            if not eliminado:
                raise HTTPException(404, f"Analista {id_analista} no encontrado")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    return {"ok": True, "mensaje": f"Analista {id_analista} eliminado correctamente"}

@admin_patch_router.patch("/administrador/analista/actualizar")
def actualizarAnalista(id_analista: str, nivel: int):
    with conectarORM() as db:
        try:
            actualizado = actualizar_analista(db, id_analista, nivel)
            if not actualizado:
                raise HTTPException(404, f"Analista {id_analista} no encontrado")
            return actualizado
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

@admin_patch_router.patch("/administrador/servicios_clientes/actualizar")
def actualizarServiciosClientes(id_cliente: str, servicios_clientes: list[str] = Query(...)):
    with conectarORM() as db:
        try:
            actualizado = actualizar_servicios_clientes(db, id_cliente, servicios_clientes)
            if not actualizado:
                raise HTTPException(404, f"Cliente {id_cliente} no encontrado")
            return {"ok": True, "mensaje": f"Servicios del cliente {id_cliente} actualizados correctamente"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")
