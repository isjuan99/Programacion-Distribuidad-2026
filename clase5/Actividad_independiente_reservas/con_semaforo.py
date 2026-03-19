import threading
import time

 
# ============================================================
#   CONFIGURACIÓN GLOBAL
# ============================================================
usuarios = 50
cursos   = 10



# ============================================================
#   PARTE 3 — CON SEMÁFORO (máximo 3 reservas simultáneas)
# ============================================================
 
semaforo = threading.Semaphore(3)
 
def reservar_con_semaforo():
    global cursos
    with semaforo:
        if cursos > 0:
            cursos -= 1
            print(f"Reserva realizada, quedan {cursos} cursos disponibles.")
        else:
            print("No hay cursos disponibles.")
 
print("\n========== PARTE 3 - Con Semáforo ==========")
cursos = 10
hilos = []
for i in range(usuarios):
    hilo = threading.Thread(target=reservar_con_semaforo)
    hilos.append(hilo)
    hilo.start()
 
for hilo in hilos:
    hilo.join()
 
print("Cantidad de cursos disponibles:", cursos)