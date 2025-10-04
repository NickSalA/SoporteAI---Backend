# Modelo de lenguaje Azure OpenAI
from langchain_openai import AzureChatOpenAI

# Manejo de cadenas secretas
from pydantic import SecretStr
  
# Helpers propios
from backend.util.util_key import obtenerAPI

def obtenerModelo(temperature: float = 0.7) -> AzureChatOpenAI:
    return AzureChatOpenAI(
      api_version = "2024-12-01-preview",
      azure_endpoint = "https://AgenteAI-Instance.openai.azure.com/",
      api_key = SecretStr(obtenerAPI("CONF-OPENAI-API-KEY")),
      azure_deployment = "geopoint-agent-model",
      temperature= temperature
    )