from backend.util.util_sincronizacion import cargarArchivoDeCarpeta
import os

ruta = os.path.join(os.path.dirname(__file__), "backend", "files")
resultado = cargarArchivoDeCarpeta(ruta, ["servicios", "analytics"])
print(resultado)


