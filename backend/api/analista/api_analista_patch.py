# Rutas API para analistas
from fastapi import APIRouter, Request, HTTPException

# CRUD
from backend.db.crud.crud_ticket import actualizar_ticket_estado, escalar_ticket, actualizar_ticket_nivel

# ORM
from backend.util.util_conectar_orm import conectarORM

analista_patch_router = APIRouter()

@analista_patch_router.patch("/analista/nivel")
def cambiarNivelTicket(ticket: int, nivel: str):
    with conectarORM() as db:
        try:
            ticket_actualizado = actualizar_ticket_nivel(db, ticket, nivel=nivel)
        except ValueError as ve:
            raise HTTPException(400, str(ve))
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")
        if not ticket_actualizado:
            raise HTTPException(404, f"Ticket {ticket} no encontrado")
    return {"mensaje": f"Nivel del ticket {ticket} cambiado a: {nivel}"}

@analista_patch_router.patch("/analista/escalar")
def escalarTicket(req: Request, ticket: int, motivo: str):
    analista = req.session.get("user")
    if not analista or analista.get("rol") != "analista":
        raise HTTPException(401, "unauthorized")
    try:
        with conectarORM() as db:
            nivel_destino = escalar_ticket(db, ticket, motivo)
            return {"mensaje": f"Ticket {ticket} escalado correctamente a nivel {nivel_destino} por el motivo: {motivo}"}
    except Exception as e:
        raise HTTPException(500, f"Error interno: {e}")

@analista_patch_router.patch("/analista/estado")
def cambiarEstadoTicket(ticket: int, estado: str, diagnostico: str | None = ""):
    with conectarORM() as db:
        try:
            ticket_actualizado = actualizar_ticket_estado(db, ticket, estado, diagnostico)
        except ValueError as ve:
            raise HTTPException(400, str(ve))
        except Exception as e:
            raise HTTPException(500, f"Error interno: {e}")
        if not ticket_actualizado:
            raise HTTPException(404, f"Ticket {ticket} no encontrado")
    return {"mensaje": f"Estado del ticket {ticket} cambiado a: {estado}"}
