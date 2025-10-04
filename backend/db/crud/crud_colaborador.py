from backend.db.models import Colaborador

def obtener_colaboradores(db) :
    colaboradores = db.execute(Colaborador).all()
    return colaboradores