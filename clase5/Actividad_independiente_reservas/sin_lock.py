import threading

 
# ============================================================
#   CONFIGURACIÓN GLOBAL
# ============================================================
usuarios = 50
cursos   = 10

 
# ============================================================
#   PARTE 1 — SIN LOCK (condición de carrera)
# ============================================================
 
def reservar_sin_lock():
    global cursos
    if cursos > 0:
        cursos -= 1
        print(f"Reserva realizada, quedan {cursos} cursos disponibles.")
    else:
        print("No hay cursos disponibles.")


print("\n========== PARTE 2 - sin Lock ==========") 
cursos = 10
hilos = []
for i in range(usuarios):
    hilo = threading.Thread(target=reservar_sin_lock)
    hilos.append(hilo)
    hilo.start()
 
for hilo in hilos:
    hilo.join()
 
print("Cantidad de cursos disponibles:", cursos)

 
