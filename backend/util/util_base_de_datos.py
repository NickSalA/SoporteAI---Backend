# Utilitario para manejar la conexión a la base de datos PostgreSQL
from langgraph.checkpoint.postgres import PostgresSaver

# Helpers propios
from backend.util.util_key import obtenerAPI

def obtenerConexionBaseDeDatos():
    try:
        conn = PostgresSaver.from_conn_string(obtenerAPI("CONF-DATABASE-URL"))
        saver = conn.__enter__()
        saver.setup()
        print("Conexión a la base de datos establecida.")
        return conn, saver
    except Exception as e:
        raise Exception(f'Error al conectar a la base de datos: {e}')