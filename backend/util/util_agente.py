# Utilitario para crear y ejecutar agentes
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent

# Utilitario para el modelo de lenguaje
from langchain_openai import AzureChatOpenAI

# Manejo de memoria del agente
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.prompts import ChatPromptTemplate
def crearAgente(
    llm: AzureChatOpenAI, contexto: ChatPromptTemplate, tools: list | None = None, memoria=None
):
    if tools is None:
        tools = []
    if memoria is None:
        memoria = InMemorySaver()
    agente = create_react_agent(
        model=llm, tools=tools, checkpointer=memoria, prompt=contexto,
    )
    return agente

def ejecutar(agente, consulta: str = "", config=None, verbose: bool = True):
    try:
        respuesta = agente.invoke({"messages": [{"role": "user", "content": consulta}]}, config=config)
        if not verbose:
            return respuesta
        return respuesta["messages"][-1].content
    except Exception as e:
        raise Exception(f'Error en la ejecución del agente: {e}')
