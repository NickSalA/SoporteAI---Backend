from backend.db.crud.crud_prompt import obtener_prompt, actualizar_prompt
#from backend.db.crud.crud_analista import eliminar_analista, obtener_analistas, actualizar_analista
#from backend.db.crud.crud_cliente import eliminar_cliente, obtener_clientes, crear_cliente
from backend.db.crud.crud_servicio import obtener_servicios, crear_servicio, actualizar_servicio, eliminar_servicio
from backend.util.util_conectar_orm import conectarORM

def test():
    with conectarORM() as db:
        servicio = eliminar_servicio(db,"a8a05ab6-6496-0f82-8094-65f3616c2062")
        # Importante: acceder a relaciones perezosas (persona/externals) mientras la sesión está abierta
        return f'Servicio eliminado'

print(test())