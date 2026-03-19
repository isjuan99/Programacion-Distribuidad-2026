#importaciones


from clase6.fastapi import FastAPI # import propio del framework FasAPI
from typing import List     # import estandar de python para tipado


#==========================================
# creacion de la aplicacion
#=========================================


app = FastAPI() #objeto principal de la API (instancia del framework)

#=========================================
# Base de  datos
#=========================================

clientes = [] #variable global lista para almacenar clientes en memoria

@app.get("/") #decorador propio de FastAPI apara metodo GET
def home(): # funcion normal (no asincrona por simplicidad)
    return {"mensaje": "API del banco funcionando"}



#=====================
# crear clientes
#======================

@app.post("/clientes") # Decorador para método POST
def crear_cliente (nombre: str) : # Parámetro recibido por query
    cliente = {
        "id": len(clientes) + 1, # Generación simple de ID
        "nombre": nombre
    }
    clientes.append(cliente) # Agrega cliente a lista global

    return cliente # Devuelve cliente creado

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
