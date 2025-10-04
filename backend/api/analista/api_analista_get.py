# Rutas API para analistas
from fastapi import APIRouter, Request, HTTPException

# CRUD
from backend.db.crud.crud_ticket import obtener_tickets, obtener_ticket_especifico
from backend.db.crud.crud_conversacion import traer_conversacion
from backend.db.crud.crud_escalado import obtener_escalado_por_ticket
# ORM
from backend.util.util_conectar_orm import conectarORM

# Modelos
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid

analista_get_router = APIRouter()

class TicketRead(BaseModel):
    id_ticket: int
    asunto: str
    estado: str
    nivel: str
    email: str
    tipo: str # Nombre colaborador # Nombre servicio
    id_colaborador: uuid.UUID | None = None
    id_analista: uuid.UUID | None = None
    id_cliente_servicio: uuid.UUID | None = None
    diagnostico: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    closed_at: datetime | None = None
    cliente_nombre: str | None = None
    colaborador_nombre: str | None = None
    servicio_nombre: str | None = None
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

class EscaladoRead(BaseModel):
    id_escalado: int
    id_ticket: int
    id_analista_solicitante: str
    id_analista_derivado: str
    motivo: str
    created_at: datetime | None = None
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

@analista_get_router.get("/analista/tickets")
def obtenerTickets(req: Request):
    analista = req.session.get("user")
    if not analista or analista.get("rol") != "analista":
        raise HTTPException(401, "unauthorized")
    try:
        with conectarORM() as db:
            tickets = obtener_tickets(db, analista)
            data = [TicketRead.model_validate(t).model_dump() for t in tickets]
            return {"tickets": data}
    except Exception as e:
        raise HTTPException(500, f"Error interno: {e}")

@analista_get_router.get("/analista/chat")
def chatAnalista(ticket: int):
    try:
        with conectarORM() as db:
            contenido = traer_conversacion(db, ticket)
            return {"chat": contenido}
    except Exception as e:
        raise HTTPException(500, f"Error interno: {e}")

@analista_get_router.get("/analista/ticket")
def obtenerTicket(req: Request, ticket: int):
    analista = req.session.get("user")
    if not analista or analista.get("rol") != "analista":
        raise HTTPException(401, "unauthorized")
    try:
        with conectarORM() as db:
            ticket_obj = obtener_ticket_especifico(db, ticket, analista)
            if not ticket_obj:
                raise HTTPException(404, f"Ticket {ticket} no encontrado o no autorizado")
            
            ticket_data = TicketRead.model_validate(ticket_obj).model_dump()
        return {"ticket": ticket_data}
    except Exception as e:
        raise HTTPException(500, f"Error interno: {e}")

@analista_get_router.get("/analista/escalado")
def obtenerEscalado(ticket: int):
    try:
        with conectarORM() as db:
            escalado = obtener_escalado_por_ticket(db, ticket)
            if not escalado:
                raise HTTPException(404, f"No se encontró un escalado para el ticket {ticket}")
            escalado_data = EscaladoRead.model_validate(escalado).model_dump()
            return {"escalado": escalado_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error interno: {e}")