from backend.db.crud.crud_prompt import obtener_prompt, actualizar_prompt
#from backend.db.crud.crud_analista import eliminar_analista, obtener_analistas, actualizar_analista
from backend.db.crud.crud_cliente import eliminar_cliente, obtener_clientes, crear_cliente
from backend.db.crud.crud_servicio import obtener_servicios, crear_servicio, actualizar_servicio, eliminar_servicio
from backend.util.util_conectar_orm import conectarORM

def test():
    with conectarORM() as db:
        cliente = crear_cliente(db, "Intikapi", "intikapi.com")
        # Importante: acceder a relaciones perezosas (persona/externals) mientras la sesión está abierta
        return f'Cliente creado correctamente: {cliente.id}, {cliente.nombre}, "{cliente.dominio}"'

print(test())