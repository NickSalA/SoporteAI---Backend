from backend.db.crud.crud_prompt import obtener_prompt, actualizar_prompt
#from backend.db.crud.crud_analista import eliminar_analista, obtener_analistas, actualizar_analista
from backend.db.crud.crud_cliente import eliminar_cliente, obtener_clientes
from backend.db.crud.crud_servicio import eliminar_servicio, obtener_servicios, actualizar_servicio
from backend.util.util_conectar_orm import conectarORM

def test():
    with conectarORM() as db:
        eliminar_cliente(db,"d75a71d2-a5b3-6ae7-86e5-6a2a05fc3ff2")
        # Importante: acceder a relaciones perezosas (persona/externals) mientras la sesión está abierta
        return f'Cliente eliminado'

def test2():
    with conectarORM() as db:
        clientes = obtener_clientes(db)
        return [{"id": str(c.id), "nombre": c.nombre, "dominio": c.dominio} for c in clientes]

print(test2())

