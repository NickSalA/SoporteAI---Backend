# Modelos
from backend.db.models import ClienteServicio, Servicio, Ticket

# SQLAlchemy
from sqlalchemy import select, delete
import uuid

def obtener_clientes_servicios(db):
    filas = db.execute(select(ClienteServicio)).scalars().all()
    return filas

def obtener_servicios_clientes(db, id_cliente: str):
    q = (
        select(
            ClienteServicio.id.label("id_cliente_servicio"),
            Servicio.id.label("id_servicio"),
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

def actualizar_servicios_clientes(db, id_cliente: str, servicios_clientes: list[str]):
    """
    Actualiza los servicios de un cliente de forma inteligente:
    - Solo elimina relaciones que NO están referenciadas por tickets
    - Agrega nuevos servicios
    - Mantiene las relaciones existentes que están en uso
    """
    try:
        # 1. Obtener relaciones actuales del cliente
        relaciones_actuales = db.execute(
            select(ClienteServicio).where(ClienteServicio.id_cliente == id_cliente)
        ).scalars().all()
        
        # 2. Convertir a sets para comparación
        servicios_actuales = {str(rel.id_servicio) for rel in relaciones_actuales}
        servicios_nuevos = set(servicios_clientes)
        
        # 3. Identificar servicios a eliminar y agregar
        servicios_a_eliminar = servicios_actuales - servicios_nuevos
        servicios_a_agregar = servicios_nuevos - servicios_actuales
        
        # 4. Eliminar solo las relaciones que NO están referenciadas por tickets
        for rel in relaciones_actuales:
            if str(rel.id_servicio) in servicios_a_eliminar:
                # Verificar si hay tickets que referencian esta relación
                tickets_referenciando = db.execute(
                    select(Ticket).where(Ticket.id_cliente_servicio == rel.id)
                ).first()
                
                if not tickets_referenciando:
                    # No hay tickets, se puede eliminar
                    db.delete(rel)
                else:
                    # Hay tickets referenciando, mantener la relación
                    print(f"Manteniendo relación cliente-servicio {rel.id} porque está referenciada por tickets")
        
        # 5. Agregar nuevos servicios
        for id_servicio in servicios_a_agregar:
            nueva_relacion = ClienteServicio(
                id_cliente=id_cliente,
                id_servicio=id_servicio,
            )
            db.add(nueva_relacion)
        
        db.flush()
        return True
        
    except Exception as e:
        db.rollback()
        raise e