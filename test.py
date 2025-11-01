from backend.db.crud.crud_prompt import obtener_prompt, actualizar_prompt
#from backend.db.crud.crud_analista import eliminar_analista, obtener_analistas, actualizar_analista
from backend.db.crud.crud_cliente import eliminar_cliente, obtener_clientes, actualizar_cliente
from backend.db.crud.crud_servicio import eliminar_servicio, obtener_servicios, actualizar_servicio
from backend.util.util_conectar_orm import conectarORM

def test():
    with conectarORM() as db:
        clientes = obtener_clientes(db)
        # Importante: acceder a relaciones perezosas (persona/externals) mientras la sesión está abierta
        return f'Clientes obtenidos: {[{"id_cliente": c.id, "nombre": c.nombre} for c in clientes]}'
print(test())