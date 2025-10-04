from backend.db.models import Cliente
from sqlalchemy import select

def obtener_cliente_nombre(db, id_cliente: str):
    stmt = select(Cliente).where(Cliente.id == id_cliente)
    result = db.execute(stmt).scalars().first()
    return result.nombre if result else None