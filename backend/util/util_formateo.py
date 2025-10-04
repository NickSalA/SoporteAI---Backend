from langchain_core.messages import AIMessage, HumanMessage

def formatearMensaje(conversacion: list) -> list[dict]:
    formateado = []
    for msg in conversacion:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "agent"
        else:
            continue
        formateado.append({"role": role, "content": msg.content})
    return formateado

def formatearTicket(ticket) -> dict:
    detalles = {
        "ID": f"#{ticket.id_ticket}",
        "Asunto": ticket.asunto,
        "Estado": ticket.estado,
        "Nivel": ticket.nivel,
        "Tipo": ticket.tipo,
        "Empresa": ticket.cliente_nombre,
        "Servicio": ticket.servicio_nombre,
        "Analista": ticket.analista_nombre,
        "Fecha de creacion": ticket.created_at.strftime('%d/%m/%Y') if ticket.created_at else 'No especificada',
    }
    
    if ticket.estado == 'en atención':
        detalles["Fecha de actualización"] = ticket.updated_at.strftime('%d/%m/%Y') if ticket.updated_at else 'No especificada'

    if ticket.estado == 'finalizado' or ticket.estado == 'cancelado':
        detalles["Diagnostico"] = ticket.diagnostico
        detalles["Fecha de cierre"] = ticket.closed_at.strftime('%d/%m/%Y') if ticket.closed_at else 'No especificada'

    return detalles

def formatearTickets(ticket) -> dict:
    return {
        "id": ticket.id_ticket,
        "asunto": ticket.asunto,
        "estado": getattr(ticket, "estado", None),
        "nivel": getattr(ticket, "nivel", None),
        "tipo": getattr(ticket, "tipo", None),
    }