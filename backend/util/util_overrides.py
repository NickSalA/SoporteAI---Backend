from typing import Any, Dict

from backend.util.util_conectar_orm import conectarORM
from backend.db.crud.crud_prompt import obtener_prompt


def _normalize(overrides: Dict[str, Any] | None) -> Dict[str, Any]:
    if not overrides:
        return {}
    return {k: v for k, v in overrides.items() if v is not None}


def get_overrides(app) -> Dict[str, Any]:
    """
    Obtiene overrides con caché en memoria a nivel de aplicación.
    Si no existe en caché, los carga desde la BD y los deja en app.state.overrides_cache.
    """
    cache = getattr(app.state, "overrides_cache", None)
    if isinstance(cache, dict) and cache:
        return cache

    with conectarORM() as db:
        contenido = obtener_prompt(db) or {}

    cache = _normalize(contenido)
    app.state.overrides_cache = cache
    return cache


def set_overrides(app, overrides: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Actualiza la caché de overrides en memoria a nivel de aplicación.
    Devuelve el dict normalizado que quedó en caché.
    """
    cache = _normalize(overrides)
    app.state.overrides_cache = cache
    return cache
