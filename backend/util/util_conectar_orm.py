# db.py
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.util.util_key import obtenerAPI
from backend.db.crud.crud_cliente import obtener_cliente_nombre
from backend.db.crud.crud_cliente_servicio import obtener_servicios_clientes
from fastapi import Request

DATABASE_URL = obtenerAPI("CONF-DATABASE-ANALYTICS-URL")

engine = create_engine(DATABASE_URL, future=True, echo=False)  # echo=True si quieres logs SQL
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

@contextmanager
def conectarORM():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def obtenerSesion(req: Request):
    user = req.session.get("user")
    if user:
        cliente_id = user.get("cliente_id")
        with conectarORM() as db:
            user["cliente_nombre"] = obtener_cliente_nombre(db, cliente_id)
            filas = obtener_servicios_clientes(db, cliente_id)
            user["servicios"] = [
                {"id": str(r["id_cliente_servicio"]), "nombre": r["nombre"]}
            for r in filas
            ]
        req.session["user"] = user
    return req.session.get("user")
    
        