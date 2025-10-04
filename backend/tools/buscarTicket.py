# Query's para buscar tickets
from backend.db.crud.crud_ticket import obtener_ticket_asunto, obtener_ticket_especifico, obtener_tickets, obtener_tickets_abiertos

# Modelo Pydantic para los argumentos de las tools
from pydantic import BaseModel, Field

# Decorador tool
from langchain_core.tools import tool

# Formateo de tickets
from backend.util.util_formateo import formatearTicket, formatearTickets

# Conexión ORM
from backend.util.util_conectar_orm import conectarORM
class BuscarPorAsuntoInput(BaseModel):
    asunto: str = Field(..., description="Asunto o frase para buscar tickets.")

class BuscarPorIdInput(BaseModel):
    id_ticket: int = Field(..., description="ID del ticket a consultar.")

def make_buscar_tools(obtenerSesion):
    
    @tool (
        "BuscarTicketPorAsunto",
        description=(
            "Eres BuscarTicketPorAsunto. Sólo puedes buscar tickets por su asunto en el sistema de soporte."
            "Usa esta herramienta sólo si el usuario te lo pide explícitamente."
            "Debes esperar un diccionario con la clave 'asunto' que contiene una cadena de texto."
            "Devuelve los detalles de los tickets encontrados o un mensaje indicando que no se encontraron tickets."
        ),
        args_schema=BuscarPorAsuntoInput,
    )
    def buscar_ticket_por_asunto(asunto: str):
        user = obtenerSesion()
        with conectarORM() as db:
            tickets = obtener_ticket_asunto(db, asunto, user)
            tickets_list = [formatearTickets(t) for t in tickets] if tickets else []
            if tickets_list:
                return {
                    "type": "ticket_list",
                    "mode": "asunto",
                    "query": asunto,
                    "count": len(tickets_list),
                    "tickets": tickets_list,
                    "message": f"Se encontraron {len(tickets_list)} tickets relacionados al asunto '{asunto}'."
                }
            return {
                "type": "ticket_list",
                "mode": "asunto",
                "query": asunto,
                "count": 0,
                "tickets": [],
                "message": f"No se encontraron tickets relacionados al asunto '{asunto}'."
            }
    
    @tool (
        "BuscarTicketPorID",
        description=(
            "Eres BuscarTicketPorID. Sólo puedes buscar un ticket por su ID en el sistema de soporte."
            "Usa esta herramienta sólo si el usuario te lo pide explícitamente."
            "Debes esperar un diccionario con la clave 'id_ticket' que contiene un entero."
            "Devuelve los detalles del ticket encontrado o un mensaje indicando que no se encontró el ticket."
        ),
        args_schema=BuscarPorIdInput,
    )
    def buscar_ticket_por_id(id_ticket: int):
        user = obtenerSesion()
        with conectarORM() as db:
            ticket = obtener_ticket_especifico(db, id_ticket, user)
            if ticket:
                return {
                    "type": "ticket",
                    "ticket": formatearTicket(ticket),
                    "message": f"Se encontró el ticket con ID {id_ticket}."
                }
            return {
                "type": "ticket",
                "ticket": None,
                "message": f"No se encontró el ticket con ID {id_ticket}."
            }

    @tool  (
        "ListarTicketsAbiertos",
        description=(
            "Eres ListarTicketsAbiertos. Sólo puedes listar todos los tickets abiertos en el sistema de soporte."
            "Usa esta herramienta sólo si el usuario te lo pide explícitamente."
            "No necesitas argumentos para esta herramienta."
            "Devuelve los detalles de los tickets abiertos o un mensaje indicando que no hay tickets abiertos."
        ),
    )
    def listar_tickets_abiertos():
        user = obtenerSesion()
        with conectarORM() as db:
            tickets = obtener_tickets_abiertos(db, user)
            tickets_list = [formatearTickets(t) for t in tickets] if tickets else []
            return {
                "type": "ticket_list",
                "mode": "abiertos",
                "query": None,
                "count": len(tickets_list),
                "tickets": tickets_list,
                "message": (
                    f"Se encontraron {len(tickets_list)} tickets abiertos." if tickets_list else "No se encontraron tickets abiertos."
                ),
            }

    @tool (
        "ListarTodosLosTickets",
        description=(
            "Eres ListarTodosLosTickets. Sólo puedes listar todos los tickets en el sistema de soporte."
            "Usa esta herramienta sólo si el usuario te lo pide explícitamente."
            "No necesitas argumentos para esta herramienta."
            "Devuelve los detalles de todos los tickets o un mensaje indicando que no hay tickets en el sistema."
        ),
    )
    def listar_todos_los_tickets():
        user = obtenerSesion()
        try:
            with conectarORM() as db:
                tickets = obtener_tickets(db, user)
                tickets_list = [formatearTickets(t) for t in tickets] if tickets else []
                return {
                    "type": "ticket_list",
                    "mode": "todos",
                    "query": None,
                    "count": len(tickets_list),
                    "tickets": tickets_list,
                    "message": (
                        f"Se encontraron {len(tickets_list)} tickets en total." if tickets_list else "No se encontraron tickets en el sistema."
                    ),
                }
        except Exception as e:
            print("[ERROR] Excepción inesperada al listar todos los tickets:", e)
            return {
                "type": "ticket_list",
                "mode": "todos",
                "query": None,
                "count": 0,
                "tickets": [],
                "message": "No se pudieron obtener los tickets por un error interno.",
                "error": str(e)
            }
    
    return [buscar_ticket_por_asunto, buscar_ticket_por_id, listar_tickets_abiertos, listar_todos_los_tickets]