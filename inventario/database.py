import mysql.connector

def obtener_conexion():
    # Configuración local
    config = {
        "host": "localhost",
        "user": "root",
        "password": "juan",
        "database": "perfumeria_db"
    }
    return mysql.connector.connect(**config)