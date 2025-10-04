# Utilitario para crear tool de base de conocimientos
from langchain.tools.retriever import create_retriever_tool

# Manejo de herramientas y agentes
from langchain_core.tools import Tool

# Helpers propios
from backend.util.util_base_de_conocimientos import obtenerBaseDeConocimientos

retriever = obtenerBaseDeConocimientos()

def BC_Tool() -> Tool:
    return create_retriever_tool(
        retriever=retriever,
        name="BaseDeConocimientos",
        description=(
            "Eres BC_Tool. Sólo puedes buscar y devolver fragmentos de la base de conocimiento (FAQ, guías, SOPs)."
            "No inventes contenido. Devuelve texto y metadatos de la fuente."
            "Si no encuentras resultados relevantes, responde vacío."
        ),
    )
