
from clase6.fastapi import FastAPI
from clase6.fastapi import HTTPException
import asyncio


from database import get_connection

app = FastAPI(title="API de Gestión de Citas Mejorada", version="1.0")




#========================================
# CREAR CITAS
#========================================
@app.post("/citas")
async def crear_cita(paciente: str, fecha: str):
    conn = None
    cursor = None
    try:
        await asyncio.sleep(2)  # simulación de proceso lento
        
        conn = await get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
            
        cursor = await conn.cursor()
        
        query = """
            INSERT INTO citas (paciente, fecha, estado)
            VALUES (%s, %s, %s)
        """
        
        await cursor.execute(query, (paciente, fecha, "activa"))
        await conn.commit()
        
        return {"mensaje": "Cita creada correctamente"}
        
    except Exception as e:
        print(f"Error en crear_cita: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear cita: {str(e)}")
        
    finally:
        # Cerrar recursos en orden inverso
        if cursor:
            try:
                await cursor.close()  # cursor.close() SÍ lleva await
            except:
                pass
        if conn:
            try:
                conn.close()  # conn.close() NO lleva await
            except:
                pass

#======================================
# LISTAR CITAS
#======================================

@app.get("/citas/listar")
async def listar_citas():
    conn = None
    cursor = None
    try:
        conn = await get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
            
        cursor = await conn.cursor()
        
        query = "SELECT * FROM citas"
        
        await cursor.execute(query)
        citas = await cursor.fetchall()
        
        return citas
        
    except Exception as e:
        print(f"Error en listar_citas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al listar citas: {str(e)}")
        
    finally:
        # Cerrar recursos en orden inverso
        if cursor:
            try:
                await cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()  # Nota: ¡sin await! close() no es async
            except:
                pass
            




#=======================================
#  LISTA DE SOLO CITAS ACTIVAS
#=======================================

@app.get("/citas/activas")
async def listar_citas_activas():
    """
    Endpoint para listar solo citas activas
    GET /citas/activas
    """
    conn = None
    cursor = None
    try:
        conn = await get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
            
        cursor = await conn.cursor()
        
        query = "SELECT * FROM citas WHERE estado = 'activa' ORDER BY fecha DESC"
        
        await cursor.execute(query)
        citas_activas = await cursor.fetchall()
        
        return citas_activas
        
    except Exception as e:
        print(f"Error en listar_citas_activas: {e}")
        raise HTTPException(status_code=500, detail=f"Error al listar citas activas: {str(e)}")
        
    finally:
        if cursor:
            try:
                await cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass
            

 #=====================================
 # Contador de citas
 #=====================================           

@app.get("/citas/count")
async def contar_citas():
    """
    Endpoint para contar citas
    """
    conn = None
    cursor = None
    try:
        conn = await get_connection()
        cursor = await conn.cursor()
        
        # Una sola consulta para todo
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN estado = 'activa' THEN 1 ELSE 0 END) as activas,
                SUM(CASE WHEN estado = 'cancelada' THEN 1 ELSE 0 END) as canceladas
            FROM citas
        """
        
        await cursor.execute(query)
        resultado = await cursor.fetchone()
        
        return {
            "total_citas": resultado[0],
            "citas_activas": resultado[1],
            "citas_canceladas": resultado[2]
        }
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            await cursor.close()
        if conn:
            conn.close()



#===================================
# BUSCAR CITAS PACIENTE
#===================================


@app.get("/citas/id")
async def buscar_cita(id: str):
    conn = await get_connection()
    cursor = await conn.cursor()
    
    query = "SELECT * FROM citas WHERE id=%s"
    
    await cursor.execute(query, (id,))
    
    cita = await cursor.fetchone()
    
    await cursor.close()
    conn.close()
    
    if not cita:
        raise HTTPException(
            status_code=404,
            detail="Cita no encontrada"
        )
    return cita

#===========================================
 #  Cancelar citas
#===========================================           


@app.put("/citas/id/cancelar")
async def cancelar_cita(id: int):
    conn = await get_connection()
    cursor = await conn.cursor()
    
    query = "UPDATE citas SET estado='cancelada' WHERE id=%s"
    
    await cursor.execute(query, (id,))
    await conn.commit()
    
    await cursor.close()
    conn.close()
    
    return {"mensaje": "Cita cancelada"}


#===========================================
 #  Reactivar citas
#===========================================           

@app.put("/citas/reactivar/id")
async def reactivar_cita(id: int):
    """
    Endpoint para reactivar una cita cancelada
    PUT /citas/reactivar/{id}
    """
    conn = None
    cursor = None
    try:
        conn = await get_connection()
        if not conn:
            raise HTTPException(status_code=500, detail="No se pudo conectar a la base de datos")
            
        cursor = await conn.cursor()
        
        # Verificar si la cita existe y su estado actual
        check_query = "SELECT id, estado FROM citas WHERE id = %s"
        await cursor.execute(check_query, (id,))
        cita = await cursor.fetchone()
        
        if not cita:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontró la cita con id {id}"
            )
        
        if cita[1] == 'activa':
            return {"mensaje": f"La cita {id} ya está activa", "cita_id": id, "estado": "activa"}
        
        if cita[1] != 'cancelada':
            raise HTTPException(
                status_code=400,
                detail=f"La cita {id} no puede ser reactivada porque su estado es '{cita[1]}'"
            )
        
        # Reactivar la cita
        query = "UPDATE citas SET estado = 'activa' WHERE id = %s"
        await cursor.execute(query, (id,))
        await conn.commit()
        
        return {
            "mensaje": f"Cita {id} reactivada correctamente",
            "cita_id": id,
            "estado_anterior": "cancelada",
            "estado_nuevo": "activa"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en reactivar_cita: {e}")
        raise HTTPException(status_code=500, detail=f"Error al reactivar cita: {str(e)}")
        
    finally:
        if cursor:
            try:
                await cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass


#===========================================
 # Actualizar fecha de cita
#===========================================           


@app.put("/citas/{cita_id}/fecha")
async def actualizar_fecha_cita(cita_id: int, fecha: str):
    conn = None
    cursor = None
    
    try:
        conn = await get_connection()
        cursor = await conn.cursor()
        
        # Verificar si existe
        check_query = "SELECT id FROM citas WHERE id = %s"
        await cursor.execute(check_query, (cita_id,))
        existe = await cursor.fetchone()
        
        if not existe:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        # Actualizar
        update_query = "UPDATE citas SET fecha = %s WHERE id = %s"
        await cursor.execute(update_query, (fecha, cita_id))
        
        return {"mensaje": "Fecha actualizada"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            await cursor.close()
        if conn:
            conn.close()


#===========================================
 #  Eliminar citas
#===========================================           
@app.delete("/citas/id/Eliminar")
async def eliminar_cita(id: int):
    conn = None
    cursor = None
    
    try:
        conn = await get_connection()
        cursor = await conn.cursor()
        
        # Verificar si existe
        query = "SELECT id FROM citas WHERE id = %s"
        await cursor.execute(query, (id,))
        cita = await cursor.fetchone()
        
        if not cita:
            raise HTTPException(status_code=404, detail="Cita no encontrada")
        
        # Eliminar cita
        query = "DELETE FROM citas WHERE id = %s"
        await cursor.execute(query, (id,))
        
        return {"mensaje": "Cita eliminada correctamente"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            await cursor.close()
        if conn:
            conn.close()

#===========================================
 #  Listar citas por fechas
#===========================================           


@app.get("/citas/fecha/fecha")
async def listar_citas_por_fecha(fecha: str):
    conn = None
    cursor = None
    
    try:
        conn = await get_connection()
        cursor = await conn.cursor()
        
        query = "SELECT id, paciente, fecha FROM citas WHERE fecha = %s"
        await cursor.execute(query, (fecha,))
        
        citas = await cursor.fetchall()
        
        return {"citas": citas}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            await cursor.close()
        if conn:
            conn.close()