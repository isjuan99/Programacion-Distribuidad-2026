#=================================
# IMPORTACIONES
#=================================

import aiomysql # libreria async para Mysql

#=================================
# CONFIGURACION DE  CONEXION
#=================================

"""DB_CONFIG = {
     "host": "localhost",
     "port": 3306,
     "user": "admin",
     "password": "juan",
     "db": "citas_db"
"""
import aiomysql

# Configuración actualizada para MariaDB
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Nuevo usuario creado
    'password': '',  # Contraseña que definiste
    'db': 'citas_db',  # Tu base de datos
    'port': 3306,
    'autocommit': False
}

async def get_connection():
    """Obtiene una conexión a la base de datos"""
    try:
        conn = await aiomysql.connect(**DB_CONFIG)
        print("✅ Conexión exitosa a la base de datos")
        return conn
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        raise e


#=================================
# FUNCION DE CONEXION
#=================================

async def get_connection():
   """
   crear una conexion async con la base de datos
   """
   return await aiomysql.connect(**DB_CONFIG)
