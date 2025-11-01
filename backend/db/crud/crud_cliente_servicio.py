# Modelos
from backend.db.models import ClienteServicio, Servicio

# SQLAlchemy
from sqlalchemy import select

def obtener_clientes_servicios(db):
    filas = db.execute(select(ClienteServicio)).scalars().all()
    return filas

def obtener_servicios_clientes(db, id_cliente: str):
    q = (
        select(
            ClienteServicio.id.label("id_cliente_servicio"),
            Servicio.nombre.label("nombre"),
        )
        .select_from(ClienteServicio)
        .join(Servicio, Servicio.id == ClienteServicio.id_servicio)
        .where(
            ClienteServicio.id_cliente == id_cliente,
            )
        .order_by(Servicio.nombre.asc())
    )
    return db.execute(q).mappings().all()

def crear_cliente_servicio(db, id_cliente: str, id_servicio: int) -> ClienteServicio:
    nuevo = ClienteServicio(
        id_cliente=id_cliente,
        id_servicio=id_servicio,
    )
    db.add(nuevo)
    db.flush()
    return nuevo

def eliminar_servicio_cliente(db, id_cliente: str, id_servicio: int):
    fila = db.execute(
        select(ClienteServicio).where(
            ClienteServicio.id_cliente == id_cliente,
            ClienteServicio.id_servicio == id_servicio,
        )
    ).scalar_one_or_none()
    if not fila:
        raise ValueError("Servicio del cliente no encontrado")
    db.delete(fila)
    db.flush()
    return True