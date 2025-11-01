from backend.db.models import Prompt
from sqlalchemy import select

def obtener_prompt_id(db, id: int) -> Prompt | None:
    try:
        query = select(Prompt).where(Prompt.id_prompt == id)
        prompt = db.execute(query).scalar_one_or_none()
        return prompt
    except Exception as e:
        raise ValueError(f"Error al obtener Prompt por ID: {str(e)}")

def obtener_prompt_nombre(db, nombre: str) -> Prompt | None:
    try:
        query = select(Prompt).where(Prompt.nombre == nombre)
        prompt = db.execute(query).scalar_one_or_none()
        return prompt
    except Exception as e:
        raise ValueError(f"Error al obtener Prompt por nombre: {str(e)}")