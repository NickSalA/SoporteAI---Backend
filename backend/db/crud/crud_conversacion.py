from backend.db.models import Conversacion
from sqlalchemy import select

def traer_conversacion(db, ticket: int):
    query = select(Conversacion).where(Conversacion.id_ticket == ticket)
    conversacion = db.execute(query).scalar_one_or_none()
    return conversacion.contenido if conversacion else None

def guardar_conversacion(db, ticket: int, contenido: list[dict]):
    query = select(Conversacion).where(Conversacion.id_ticket == ticket)
    conversacion = db.execute(query).scalar_one_or_none()
    if conversacion:
        conversacion.contenido = contenido
    else:
        nueva_conversacion = Conversacion(id_ticket=ticket, contenido=contenido)
        db.add(nueva_conversacion)
    db.flush()