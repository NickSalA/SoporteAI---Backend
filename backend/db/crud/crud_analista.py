# Modelos
from backend.db.models import Analista, Ticket

# SQLAlchemy
from sqlalchemy import func, String, cast
from sqlalchemy import select

import enum

def obtener_analistas(db) :
    analistas = db.execute(select(Analista)).scalars().all()
    return analistas 

TICKET_NIVEL_ANALISTA = {
    "bajo": 1,
    "medio": 2,
    "alto": 3,
    "crítico": 4,
    "critico": 4,
}

def nivel_numero(nivel) -> int:
    s = ""
    if isinstance(nivel, enum.Enum):
        s = nivel.value
    else:
        s = str(nivel)
        # si viene "TicketNivelEnum.bajo", toma la parte final
        if "." in s:
            s = s.split(".")[-1]
    s = s.lower()
    try: 
        return TICKET_NIVEL_ANALISTA[s]
    except KeyError:
        raise ValueError(f"Nivel desconocido: {nivel}")

def obtener_analista_nivel(db, nivel_ticket):
    nivel_int = nivel_numero(nivel_ticket)

    # Si NO tienes el Enum Python de Ticket.estado, castea la columna a texto para evitar el error del ENUM PG:
    subq = (
        select(
            Ticket.id_analista.label("id_analista"),
            func.count(Ticket.id_ticket).label("abiertos"),
        )
        .where(cast(Ticket.estado, String) != "cerrado")   # <-- evita el InvalidTextRepresentation
        .group_by(Ticket.id_analista)
        .subquery()
    )

    # Nota: si tu modelo expone la PK como Analista.id_analista en vez de Analista.id, cambia la comparación
    q = (
        select(Analista)
        .outerjoin(subq, Analista.id == subq.c.id_analista)   # usa Analista.id_analista si así se llama tu atributo
        .where(Analista.nivel == nivel_int)                   # INT, no enum
        .order_by(func.coalesce(subq.c.abiertos, 0).asc(), func.random())
        .limit(1)
    )
    analista = db.execute(q).scalars().first()

    # Fallback: si no hay analistas de ese nivel, elige el menos cargado de cualquier nivel
    if not analista:
        q2 = (
            select(Analista)
            .outerjoin(subq, Analista.id == subq.c.id_analista)
            .order_by(func.coalesce(subq.c.abiertos, 0).asc(), func.random())
            .limit(1)
        )
        analista = db.execute(q2).scalars().first()

    return analista


def obtener_analista(db):
    subq = (
        select(
            Ticket.id_analista.label("id_analista"),
            func.count(Ticket.id_ticket).label("abiertos"),
        )
        .where(cast(Ticket.estado, String) != "cerrado")   # <-- evita el InvalidTextRepresentation
        .group_by(Ticket.id_analista)
        .subquery()
    )
    q = (
        select(Analista)
        .outerjoin(subq, Analista.id == subq.c.id_analista)   # usa Analista.id_analista si así se llama tu atributo
        .where(Analista.nivel == 1)                          # filtra SIEMPRE por analistas de nivel 1
        .order_by(func.coalesce(subq.c.abiertos, 0).asc(), func.random())
        .limit(1)
    )
    analista = db.execute(q).scalars().first()
    return analista