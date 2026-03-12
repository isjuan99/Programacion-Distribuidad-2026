from fastapi import FastAPI, HTTPException
import mysql.connector
import requests
import asyncio

app = FastAPI()

# ============================================================
# CONFIGURACION DE BASE DE DATOS
# ============================================================
conexion = mysql.connector.connect(
    host="172.20.197.180",
    user="clase",
    password="1234",
    database="citas_medicas"
)

# ============================================================
# GRUPO 1 - Registro de pacientes (prefijo /grupo1)
# ============================================================
@app.post("/crear/pacientes")
def crear_paciente(nombre: str, email: str):
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO pacientes(nombre, email) VALUES (%s, %s)",
        (nombre, email)
    )
    conexion.commit()
    return {"mensaje": "Paciente registrado"}

# ============================================================
# GRUPO 2 - Consulta de pacientes (prefijo /grupo2)
# ============================================================
@app.get("/listar/pacientes/{id}")
def obtener_paciente(id: int):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM pacientes WHERE id = %s",
        (id,)
    )
    paciente = cursor.fetchone()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente

# ============================================================
# GRUPO 3 - Crear cita (prefijo /grupo3)
# ============================================================
# Agrega esto en tu archivo, preferiblemente en el Grupo 3
@app.post("/crear/citas")
async def crear_citas(paciente_id: int, fecha: str):
    # Verificar que el paciente existe
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pacientes WHERE id = %s", (paciente_id,))
    paciente = cursor.fetchone()
    
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no existe")
    
    # Crear la cita
    cursor.execute(
        "INSERT INTO citas(paciente_id, fecha, estado) VALUES (%s, %s, 'activa')",
        (paciente_id, fecha)
    )
    conexion.commit()
    
    return {"mensaje": "Cita creada exitosamente", "paciente_id": paciente_id, "fecha": fecha}
# ============================================================
# GRUPO 4 - Consultar citas (prefijo /grupo4)
# ============================================================
@app.get("/listar/citas/{paciente_id}")
def listar_citas(paciente_id: int):
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM citas WHERE paciente_id = %s",
        (paciente_id,)
    )
    return cursor.fetchall()

# ============================================================
# GRUPO 5 - Cancelar cita (prefijo /grupo5)
# ============================================================
@app.delete("/cancelar/citas/{id}")
def cancelar_cita(id: int):
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE citas SET estado = 'cancelada' WHERE id = %s",
        (id,)
    )
    conexion.commit()
    return {"mensaje": "Cita cancelada"}

# ============================================================
# GRUPO 6 - API Gateway (prefijo /grupo6)
# ============================================================
@app.post("/hacer/reservar-cita")
def reservar(paciente_id: int, fecha: str):
    r = requests.post(
        "http://localhost:8001/crear/citas",
        params={"paciente_id": paciente_id, "fecha": fecha}
    )
    return r.json()


# ============================================================
# este comando no se me puede olvidar : python3 -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
# ============================================================