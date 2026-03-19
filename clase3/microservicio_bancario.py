from clase6.fastapi import FastAPI, HTTPException
from clase6.fastapi import FastAPI # import propio del framework FasAPI
from typing import List     # import estandar de python para tipado
import asyncio

#==========================================
# creacion de la aplicacion
#=========================================


app = FastAPI() #objeto principal de la API (instancia del framework)

#=========================================
# Base de  datos
#=========================================

clientes = [] #variable global lista para almacenar clientes en memoria
contador_clientes = 0

@app.get("/") #decorador propio de FastAPI apara metodo GET
def home(): # funcion normal (no asincrona por simplicidad)
    return {"mensaje": "API del banco funcionando"}


#========================================
# Validacion de para el campo nombre
#========================================

# Función de validación para el nombre
def validar_nombre(nombre: str):
    
     #"" Valida que el nombre no esté vacío ni sea solo espacios
     # PUNTO 3: Validación básica 
    if not nombre or not nombre.strip():  # strip() elimina espacios al inicio y final
        raise HTTPException(
            status_code=400, 
            detail="El nombre no puede estar vacío o contener solo espacios"
        )
    return nombre.strip()  # Devuelve el nombre sin espacios extras




#====================================
# crear clientes con delay asincrono
#====================================

@app.post("/clientes")
async def crear_cliente(nombre: str):
    global contador_clientes
    
    # Validación nombre
    nombre_validado = validar_nombre(nombre)
    
    # Simulamos un delay de 3 sg
    await asyncio.sleep(3)
    
    # Incremento de contador global de los clientes
    contador_clientes += 1
    
    # Crear cliente
    cliente = {
        "id": len(clientes) + 1,
        "nombre": nombre_validado,
        
    }
    
    clientes.append(cliente)  # ← Este estaba mal indentado
    
    return cliente
#=========================================
# PUNTO 2: Endpoint PUT para actualizar nombre
#=========================================
@app.put("/clientes/{cliente_id}")
async def actualizar_cliente(cliente_id: int, nombre: str):
    
    #Actualiza el nombre de un cliente existente
    
    #- Valida que el nombre no esté vacío
    #- Busca el cliente por ID
    #- Actualiza solo el nombre
    
    # 1. Validar el nuevo nombre
    nombre_validado = validar_nombre(nombre)
    
    # 2. Buscar el cliente
    for cliente in clientes:
        if cliente["id"] == cliente_id:
            # Guardar nombre anterior para mensaje
            nombre_anterior = cliente["nombre"]
            
            # Actualizar el nombre
            cliente["nombre"] = nombre_validado
            
            return {
                "mensaje": "Cliente actualizado exitosamente",
                "cliente": cliente,
                "cambio": f"'{nombre_anterior}' → '{nombre_validado}'"
            }
    
    # 3. Si no encuentra el cliente
    raise HTTPException(
        status_code=404,  # 404 = Not Found
        detail=f"No se encontró el cliente con ID {cliente_id}"
    )

#=========================================
# PUNTO 1: Endpoint DELETE para eliminar cliente
#=========================================
@app.delete("/clientes/{cliente_id}")
async def eliminar_cliente(cliente_id: int):
    """
    Elimina un cliente por su ID
    - Busca el cliente
    - Lo elimina de la lista
    - Retorna confirmación
    """
    # 1. Buscar el índice del cliente
    for i, cliente in enumerate(clientes):  # enumerate da índice y valor
        if cliente["id"] == cliente_id:
            # Guardar info antes de eliminar
            cliente_eliminado = cliente
            
            # Eliminar de la lista (pop por índice)
            clientes.pop(i)
            
            return {
                "mensaje": "Cliente eliminado exitosamente",
                "cliente_eliminado": cliente_eliminado,
                "clientes_restantes": len(clientes)
            }
    
    # 2. Si no encuentra el cliente
    raise HTTPException(
        status_code=404,
        detail=f"No se encontró el cliente con ID {cliente_id} para eliminar"
    )
#==================================
# listar clientes
#==================================

@app.get("/clientes", response_model=List[dict]) # definir tipo de respuesta
def listar_clientes():
    return clientes # Devuelve lista completa


#==========================
#obtener cliente por iD
#=========================

@app.get("/clientes/{clientes_id}") #ruta con parametro dinamico
def obtener_cliente(cliente_id: int): #tipo entero
    for cliente in clientes: #recorrer lista 
        if cliente["id"] == cliente_id: 
            return cliente # retornar si encuentra 
        
    return {"error": "cliente no encontrado"} #manejo basico de error   
