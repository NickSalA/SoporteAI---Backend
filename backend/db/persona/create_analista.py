from backend.db.models import External, Analista, Persona
from sqlalchemy import select

def insertar_analista(db, sub: str, email: str | None, name: str | None, hd: str | None):
    ext = db.execute(
        select(External).where(
            External.provider == "google",
            External.id_provider == sub
        )
    ).scalars().first()
    if ext:
        # actualizar datos no críticos
        ext.correo = email
        ext.nombre = name
        ext.hd = hd
        persona_id = ext.id_persona
    else:
        # crear persona
        persona = Persona()
        db.add(persona); db.flush()              # ahora persona.id_persona existe
        persona_id = persona.id

        # crear external
        ext = External(
            id_persona=persona_id,
            provider="google",
            id_provider=sub,
            correo=email,
            nombre=name,
            hd=hd
        )
        db.add(ext)
    
    analista = db.execute(
        select(Analista).where(Analista.id_persona == persona_id)
    ).scalars().first()
    
    if not analista:
        analista = Analista(id_persona=persona_id, nivel=1)
        db.add(analista)
        db.flush()
    
    analista_id = str(analista.id)

    return {
        "persona_id": str(persona_id),
        "analista_id": str(analista_id) if analista_id else None,
        "nivel": analista.nivel if analista else None,
    }