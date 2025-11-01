from backend.db.models import Prompt
from sqlalchemy import select

def obtener_prompt(db, id = 1) -> dict | None:
    try:
        query = select(Prompt).where(Prompt.id == id)
        prompt = db.execute(query).scalar_one_or_none()
        return prompt.contenido if prompt else None
    except Exception as e:
        raise ValueError(f"Error al obtener Prompt por ID: {str(e)}")

def actualizar_prompt(db, prompt: dict = {}, id: int = 1) -> bool:
    try:
        prompt_actual = db.execute(select(Prompt).where(Prompt.id == id)).scalar_one_or_none()
        if not prompt_actual:
            raise ValueError("Prompt no encontrado")

        prompt_actual.contenido = prompt or {}
        db.add(prompt_actual)
        db.flush()
        return True
    except Exception as e:
        raise ValueError(f"Error al actualizar Prompt: {str(e)}")