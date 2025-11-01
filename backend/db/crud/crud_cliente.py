from backend.db.models import Cliente, ClienteDominio
from sqlalchemy import select
from typing import Optional

def obtener_clientes(db):
    clientes = db.execute(select(Cliente)).scalars().all()
    return clientes

def obtener_cliente_nombre(db, id_cliente: str):
    stmt = select(Cliente).where(Cliente.id == id_cliente)
    result = db.execute(stmt).scalars().first()
    return result.nombre if result else None

def crear_cliente(db, nombre: str, dominio: str) -> Cliente:
    # 1) ¿Existe ya el dominio? (PK en cliente_dominio)
    existente_dom = db.execute(
        select(ClienteDominio).where(ClienteDominio.dominio == dominio)
    ).scalar_one_or_none()
    if existente_dom:
        # Idempotente: devolvemos el cliente ya vinculado a ese dominio
        return existente_dom.cliente

    # 2) ¿Existe ya un cliente con ese nombre?
    existente_cliente = db.execute(
        select(Cliente).where(Cliente.nombre == nombre)
    ).scalar_one_or_none()

    if existente_cliente:
        # Asociar el nuevo dominio a este cliente
        nuevo_dominio = ClienteDominio(dominio=dominio, cliente=existente_cliente)
        db.add(nuevo_dominio)
        db.flush()
        return existente_cliente

    # 3) Crear cliente y dominio nuevos
    nuevo_cliente = Cliente(nombre=nombre)
    nuevo_dominio = ClienteDominio(dominio=dominio, cliente=nuevo_cliente)
    db.add(nuevo_cliente)
    db.add(nuevo_dominio)
    db.flush()
    return nuevo_cliente

def actualizar_cliente(db, id_cliente: str, nombre: Optional[str] = "", dominio: Optional[str] = "") -> Cliente:
    cliente = db.execute(select(Cliente).where(Cliente.id == id_cliente)).scalar_one_or_none()
    if not cliente:
        raise ValueError("Cliente no encontrado")
    
    if nombre:
        cliente.nombre = nombre

    if dominio:
        dominio_obj = db.execute(
            select(ClienteDominio).where(ClienteDominio.id_cliente == id_cliente)
        ).scalar_one_or_none()
        if dominio_obj:
            dominio_obj.dominio = dominio
        else:
            nuevo_dominio = ClienteDominio(dominio=dominio, id_cliente=id_cliente)
            db.add(nuevo_dominio)
    db.flush()
    return cliente

def eliminar_cliente(db, id_cliente: str):
    try:
        cliente = db.execute(select(Cliente).where(Cliente.id == id_cliente)).scalar_one_or_none()
        if not cliente:
            return False
        db.delete(cliente)
        db.flush()
        return True
    except Exception as e:
        raise ValueError(f"Error al eliminar cliente: {str(e)}")
