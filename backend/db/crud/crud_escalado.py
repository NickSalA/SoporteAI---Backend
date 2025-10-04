from backend.db.models import Escalado

def crear_escalado(bd, idTicket: int, id_analista_der, id_analista_soli, motivo: str) -> Escalado:
    try:
        new_escalado = Escalado(
            id_ticket = idTicket,
            id_analista_solicitante = id_analista_soli,
            id_analista_derivado = id_analista_der,
            motivo = motivo,
        )
        
        bd.add(new_escalado)
        bd.flush()
        return new_escalado
    except Exception as e:
        raise ValueError(f"Error al crear escalado: {str(e)}")

def obtener_escalado_por_ticket(bd, idTicket: int) -> Escalado | None:
    try:
        escalado = bd.execute(
            bd.select(Escalado).where(Escalado.id_ticket == idTicket).order_by(Escalado.created_at.desc())
            ).scalar_one_or_none()
        return escalado
    except Exception as e:
        raise ValueError(f"Error al obtener escalado: {str(e)}")