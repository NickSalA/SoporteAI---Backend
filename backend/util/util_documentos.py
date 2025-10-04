# Cliente para Azure Document Intelligence
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Helpers propios
from backend.util.util_key import obtenerAPI

def conectarDocumentIntelligence():
    return DocumentAnalysisClient(
        endpoint="https://sopport-di.cognitiveservices.azure.com/",
        credential=AzureKeyCredential(obtenerAPI("CONF-AZURE-FORM-RECOGNIZER-KEY")),
    )