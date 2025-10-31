from backend.db.models import Servicio
from sqlalchemy import select

def crear_servicio(db, nombre: str) -> Servicio:
    servicio = Servicio(nombre=nombre)
    db.add(servicio)
    db.flush()
    return servicio

def obtener_servicios(db):
    servicios = db.execute(select(Servicio)).scalars().all()
    return servicios

def obtener_servicio_nombre(db, nombre: str) -> Servicio | None:
    servicio = db.execute(
        select(Servicio).where(Servicio.nombre == nombre)
    ).scalars().first()
    return servicio