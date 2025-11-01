from fastapi import APIRouter, Request, HTTPException
from typing import Optional
from pydantic import BaseModel

from backend.db.crud.crud_prompt import actualizar_prompt
from backend.db.crud.crud_servicio import crear_servicio, eliminar_servicio, actualizar_servicio
from backend.db.crud.crud_cliente import crear_cliente, eliminar_cliente, actualizar_cliente
from backend.db.crud.crud_analista import eliminar_analista, actualizar_analista
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

@admin_patch_router.patch("/administrador/servicio/crear")
def crearServicio(nombre: str):
    with conectarORM() as db:
        try:
            servicio = crear_servicio(db, nombre)
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    return {"ok": True, "servicio": {"id_servicio": str(servicio.id), "nombre": servicio.nombre}}

@admin_patch_router.patch("/administrador/servicio/actualizar")
def actualizarServicio(id_servicio: str, nombre: str):
    with conectarORM() as db:
        try:
            actualizado = actualizar_servicio(db, id_servicio, nombre)
            if not actualizado:
                raise HTTPException(404, f"Servicio {id_servicio} no encontrado")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    return {"ok": True, "mensaje": f"Servicio {id_servicio} actualizado correctamente"}

@admin_patch_router.patch("/administrador/servicio/eliminar")
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

@admin_patch_router.patch("/administrador/cliente/crear")
def crearCliente(nombre: str, dominio: str):
    with conectarORM() as db:
        try:
            cliente = crear_cliente(db, nombre, dominio)
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    return {"ok": True, "cliente": {"id_cliente": str(cliente.id), "nombre": cliente.nombre}}

@admin_patch_router.patch("/administrador/cliente/actualizar")
def actualizarCliente(id_cliente: str, nombre: str):
    with conectarORM() as db:
        try:
            actualizado = actualizar_cliente(db, id_cliente, nombre)
            if not actualizado:
                raise HTTPException(404, f"Cliente {id_cliente} no encontrado")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    return {"ok": True, "mensaje": f"Cliente {id_cliente} actualizado correctamente"}

@admin_patch_router.patch("/administrador/cliente/eliminar")
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

@admin_patch_router.patch("/administrador/analista/eliminar")
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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")

    return {"ok": True, "mensaje": f"Analista {id_analista} actualizado correctamente"}