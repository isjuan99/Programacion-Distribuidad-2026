
# ============================================
# MICROSERVICIO DE CITAS MÉDICAS
# ============================================

# Importamos las herramientas que necesitamos
from fastapi import FastAPI, HTTPException  # FastAPI para el servidor, HTTPException para manejar errores
from typing import List, Optional  # Para definir tipos de datos (ayuda a documentar el código)
import asyncio  # Para simular delays sin bloquear el servidor
from datetime import datetime  # Para manejar fechas y horas de las citas

# ============================================
# CONFIGURACIÓN INICIAL
# ============================================

# Creamos la aplicación FastAPI
app = FastAPI(
    title="Sistema de Citas Médicas",
    description="API para gestionar citas médicas - Actividad independiente",
    
)

# ============================================
# BASE DE DATOS EN MEMORIA
# ============================================

# Esta lista actuará como nuestra "base de datos" temporal
# Cada cita será un diccionario con la información
citas = []

# Contador para generar IDs únicos automáticamente

contador_citas = 0


# ============================================
# FUNCIONES AUXILIARES
# ============================================

def buscar_cita_por_id(cita_id: int):
    
   # Función auxiliar para encontrar una cita por su ID si la encuentra Retorna la cita y si no la encuentra no existe
    
    for cita in citas:
        if cita["id"] == cita_id:
            print(f" Cita encontrada: ID {cita_id} - Paciente: {cita['paciente']}")
            return cita
   # Si llegamos aquí, no se encontró la cita
    print(f" No se encontró información para la cita con ID {cita_id}")
    return None

# ============================================
# ENDPOINT 1: CREAR CITA (POST)
# ============================================

@app.post("/citas")
async def crear_cita(
    paciente: str,      # Nombre del paciente (obligatorio)
    doctor: str,        # Nombre del doctor (obligatorio)
    fecha: str,         # Fecha de la cita (obligatorio)
    hora: str,          # Hora de la cita (obligatorio)
    motivo: str = "Consulta general"  # Motivo (opcional, valor por defecto)
):
   
    global contador_citas  # Necesario para modificar la variable global
    
    # ========================================
    # VALIDACIONES
    # ========================================
    
    # Validar que el nombre del paciente no esté vacío
    if not paciente or not paciente.strip():
        # HTTP 400 = Bad Request (error del cliente)
        raise HTTPException(
            status_code=400,
            detail="El nombre del paciente no puede estar vacío"
        )
    
    # Validar que el doctor no esté vacío
    if not doctor or not doctor.strip():
        raise HTTPException(
            status_code=400,
            detail="El nombre del doctor no puede estar vacío"
        )
    
    # Validar fecha (formato simple YYYY-MM-DD)
    if not fecha or len(fecha) != 10 or fecha.count("-") != 2:
        raise HTTPException(
            status_code=400,
            detail="La fecha debe tener formato YYYY-MM-DD (ej: 2024-03-20)"
        )
    
    # Validar hora (formato HH:MM)
    if not hora or len(hora) != 5 or hora[2] != ":":
        raise HTTPException(
            status_code=400,
            detail="La hora debe tener formato HH:MM (ej: 15:30)"
        )
    
    # ========================================
    # DELAY SIMULADO (2 segundos)
    # ========================================
    # Requisito de la actividad: simular delay en creación
    # await permite que el servidor siga respondiendo otras peticiones mientras espera los 2 segundos
    await asyncio.sleep(2)
    
    # ========================================
    # CREACIÓN DE LA CITA
    # ========================================
    
    # Incrementamos el contador para tener un nuevo ID
    contador_citas += 1
    
    # Obtenemos la fecha y hora actual para el registro
    ahora = datetime.now()
    fecha_creacion = ahora.strftime("%Y-%m-%d %H:%M:%S")
    
    # Creamos el diccionario con todos los datos de la cita
    nueva_cita = {
        "id": contador_citas,  # ID único generado automáticamente
        "paciente": paciente.strip(),  # Limpiamos espacios extras
        "doctor": doctor.strip(),
        "fecha": fecha,
        "hora": hora,
        "motivo": motivo,
        "estado": "activa",  # Por defecto, las citas nuevas están activas
        "fecha_creacion": fecha_creacion
    }
    
    # Agregamos la cita a nuestra "base de datos" (la lista)
    citas.append(nueva_cita)
    
    # ========================================
    # RESPUESTA
    # ========================================
    # Devolvemos la cita creada junto con un mensaje
    return {
        "mensaje": "Cita agendada exitosamente",
        "cita": nueva_cita,
        "nota": "La cita fue creada después de 2 segundos de procesamiento"
    }

# ============================================
# ENDPOINT 2: LISTAR CITAS (GET)
# ============================================

@app.get("/citas")
async def listar_citas(estado: Optional[str] = None):

    # Si no se pide filtro, devolvemos todas las citas
    if not estado:
        return {
            "total": len(citas),
            "citas": citas
        }
    
    # Si se pide filtrar por estado, filtramos la lista
    citas_filtradas = []
    for cita in citas:
        if cita["estado"] == estado.lower():  # Comparación sin importar mayúsculas
            citas_filtradas.append(cita)
    
    return {
        "filtro": f"estado = {estado}",
        "total": len(citas_filtradas),
        "citas": citas_filtradas
    }

# ============================================
# ENDPOINT 3: BUSCAR CITAS POR PACIENTE (GET)
# ============================================

@app.get("/citas/paciente/{nombre_paciente}")
async def buscar_citas_por_paciente(nombre_paciente: str):
    """
    Busca todas las citas de un paciente específico, La búsqueda no distingue entre mayúsculas/minúsculas
    y encuentra coincidencias parciales
    """
    
    # Validar que el nombre no esté vacío
    if not nombre_paciente or not nombre_paciente.strip():
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar un nombre para buscar"
        )
    
    # Convertimos a minúsculas para búsqueda sin distinción
    nombre_busqueda = nombre_paciente.lower().strip()
    
    # Lista para guardar las citas encontradas
    citas_encontradas = []
    
    # Buscamos citas donde el paciente coincida (parcialmente)
    for cita in citas:
        # Convertimos el nombre de la cita a minúsculas para comparar
        nombre_cita = cita["paciente"].lower()
        
        # Buscamos si el nombre buscado está contenido en el nombre de la cita
        if nombre_busqueda in nombre_cita:
            citas_encontradas.append(cita)
    
    # Si no se encontraron citas, lanzamos un error 404 (No encontrado)
    if not citas_encontradas:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron citas para el paciente '{nombre_paciente}'"
        )
    
    return {
        "paciente_buscado": nombre_paciente,
        "total_citas": len(citas_encontradas),
        "citas": citas_encontradas
    }

# ============================================
# ENDPOINT 4: CANCELAR CITA (DELETE)
# ============================================

@app.delete("/citas/{cita_id}")
async def cancelar_cita(cita_id: int):
    """
    Cancela (no elimina) una cita médica
    
    En lugar de borrar la cita, cambiamos su estado a "cancelada"
    Esto mantiene el historial de citas canceladas
    """
    
    # Buscamos la cita por su ID
    cita = buscar_cita_por_id(cita_id)
    
    # Si no existe, lanzamos error 404
    if not cita:
        raise HTTPException(
            status_code=404,
            detail=f"No existe ninguna cita con ID {cita_id}"
        )
    
    # Verificamos si la cita ya estaba cancelada
    if cita["estado"] == "cancelada":
        raise HTTPException(
            status_code=400,
            detail=f"La cita con ID {cita_id} ya estaba cancelada anteriormente"
        )
    
    # Cambiamos el estado de la cita
    cita["estado"] = "cancelada"
    
    # Agregamos información de cuándo se canceló
    cita["fecha_cancelacion"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return {
        "mensaje": "Cita cancelada exitosamente",
        "cita": cita
    }

