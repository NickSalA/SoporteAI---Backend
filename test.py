from backend.db.crud.crud_prompt import obtener_prompt, actualizar_prompt
from backend.db.crud.crud_analista import obtener_analistas, actualizar_analista
from backend.util.util_conectar_orm import conectarORM


def test():
    with conectarORM() as db:
        analistas = obtener_analistas(db)
        for a in analistas:
            print(f"Analista ID: {a.id}, Nombre: {a.nombre}, Email: {a.email}, Nivel: {a.nivel}")

print(test())
