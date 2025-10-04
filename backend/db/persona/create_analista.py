from backend.db.models import External, Analista
from sqlalchemy import select

def insertar_analista(db, sub: str, email: str | None, name: str | None, hd: str | None):
    ext = db.execute(
        select(External).where(
            External.provider == "google",
            External.id_provider == sub
        )
    ).scalars().first()

    persona_id = ext.id_persona

    analista = db.execute(
        select(Analista).where(Analista.id_persona == persona_id)
    ).scalars().first()
    
    analista_id = str(analista.id)

    return {
        "persona_id": str(persona_id),
        "analista_id": str(analista_id) if analista_id else None,
        "nivel": analista.nivel if analista else None,
    }