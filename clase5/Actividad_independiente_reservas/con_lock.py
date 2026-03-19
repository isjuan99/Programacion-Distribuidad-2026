import threading


 
# ============================================================
#   CONFIGURACIÓN GLOBAL
# ============================================================
usuarios = 50
cursos   = 10


# ============================================================
#   PARTE 2 — CON LOCK
# ============================================================
 
lock = threading.Lock()
 
def reservar_con_lock():
    global cursos
    with lock:
        if cursos > 0:
            cursos -= 1
            print(f"Reserva realizada, quedan {cursos} cursos disponibles.")
        else:
            print("No hay cursos disponibles.")
 
print("\n========== PARTE 2 - Con Lock ==========")
cursos = 10
hilos = []
for i in range(usuarios):
    hilo = threading.Thread(target=reservar_con_lock)
    hilos.append(hilo)
    hilo.start()
 
for hilo in hilos:
    hilo.join()
 
print("Cantidad de cursos disponibles:", cursos)
 