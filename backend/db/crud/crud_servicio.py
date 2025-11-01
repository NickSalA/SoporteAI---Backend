from backend.db.models import Servicio
from sqlalchemy import select
from typing import Optional

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

def eliminar_servicio(db, id_servicio: str):
    servicio = db.execute(
        select(Servicio).where(Servicio.id == id_servicio)
    ).scalar_one_or_none()
    if not servicio:
        raise ValueError("Servicio no encontrado")
    db.delete(servicio)
    db.flush()
    return True

def actualizar_servicio(db, id_servicio: str, nombre: Optional[str] = None) -> Servicio:
    servicio = db.execute(
        select(Servicio).where(Servicio.id == id_servicio)
    ).scalar_one_or_none()
    if not servicio:
        raise ValueError("Servicio no encontrado")
    servicio.nombre = nombre
    db.flush()
    return servicio