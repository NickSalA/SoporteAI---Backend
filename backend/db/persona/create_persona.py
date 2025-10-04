from backend.db.models import Persona, External, ClienteDominio, Colaborador
from sqlalchemy import select
from typing import Optional

def insertar_colaborador(db, sub: str, email: str | None, name: str | None, hd: str | None):
    # 1) Buscar external por (provider, id_provider)
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

    # 2) Resolver cliente por dominio y crear colaborador si aplica
    cliente_id: Optional[str] = None
    colaborador_id: Optional[str] = None
    domain = (email.split("@", 1)[1].lower() if email and "@" in email else None)

    if domain:
        cd = db.execute(select(ClienteDominio).where(ClienteDominio.dominio == domain)).scalars().first()
        if cd:
            cliente_id = cd.id_cliente
            col = db.execute(
                select(Colaborador).where(
                    Colaborador.id_persona== persona_id,
                    Colaborador.id_cliente== cliente_id
                )
            ).scalars().first()
            if not col:
                col = Colaborador(id_persona=persona_id, id_cliente=cliente_id)
                db.add(col); db.flush()
            colaborador_id = str(col.id)

    # No olvides: commit lo maneja quien llama (session_scope)
    return {
        "persona_id": str(persona_id),
        "cliente_id": str(cliente_id) if cliente_id else None,
        "colaborador_id": str(colaborador_id) if colaborador_id else None
    }
