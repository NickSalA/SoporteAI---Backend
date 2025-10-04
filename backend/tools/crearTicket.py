from langchain_core.tools import tool
from backend.db.crud.crud_ticket import crear_ticket, obtener_ticket_especifico, TicketCreatePublic, TicketNivelEnum, TicketTipoEnum
from backend.db.crud.crud_conversacion import guardar_conversacion
from backend.util.util_conectar_orm import conectarORM
from backend.util.util_formateo import formatearMensaje, formatearTicket
from typing import List
def make_crear_ticket_Tool(obtenerSesion, obtenerSaver):
    @tool(
        "CrearTicket",
        description=(
            "Eres CrearTicket. Sólo puedes crear un nuevo ticket en el sistema de soporte."\
            "Usa esta herramienta sólo si el usuario te lo pide explícitamente."\
            "Debes esperar un diccionario con las claves: asunto, nivel, tipo, servicio."\
            "El nivel puede ser 'bajo', 'medio', 'alto' o 'crítico'."\
            "El tipo puede ser 'incidencia' o 'solicitud'."\
            "Devuelve un mensaje de confirmación con el ID del ticket creado o un mensaje de error."
        ),
        args_schema=TicketCreatePublic,
    )
    def crearTicket_Tool(asunto: str, nivel: str, tipo: str, servicio: str) -> dict:
        user = obtenerSesion()
        saver = obtenerSaver()
        if not user:
            return {"error": "Usuario no autenticado.", "type": "error"}
        try:
            payload = TicketCreatePublic(
                asunto=asunto,
                nivel=TicketNivelEnum(nivel),
                tipo=TicketTipoEnum(tipo),
                servicio=servicio
            )
        except Exception as e:
            raise Exception(f"Error en los datos proporcionados: {str(e)}")
        thread = user.get("thread_id")
        state = saver.get({"configurable": {"thread_id": thread}}) if saver else None
        mensajes = state["channel_values"]["messages"] if state else []
        conversacion: List[dict] = formatearMensaje(mensajes)                
        try:
            with conectarORM() as db:
                nuevo_ticket = crear_ticket(db, payload, user)
                
                try:
                    guardar_conversacion(db, nuevo_ticket.id_ticket, conversacion)
                except Exception as e:
                    raise Exception(f"Error al guardar la conversación: {str(e)}")
                
                if nuevo_ticket:
                    # Recargar el ticket con relaciones para obtener nombres y datos derivados (incluye analista_nombre)
                    recargado = obtener_ticket_especifico(db, nuevo_ticket.id_ticket, user)
                    ticket_fmt = formatearTicket(recargado) if recargado else None
                    print(ticket_fmt)
                    return {
                        "type": "ticket_created",
                        "ticket": ticket_fmt,
                        "message": f"Ticket creado con éxito. ID del ticket: {nuevo_ticket.id_ticket}."
                    }
                else:
                    raise Exception("No se pudo crear el ticket. Por favor, inténtelo de nuevo más tarde.")
        except Exception as e:
            raise Exception(f'Error al crear el ticket: {str(e)}')

    return crearTicket_Tool