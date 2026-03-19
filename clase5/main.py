import threading

asientos = 10
lock = threading.Lock()

def reservar () :
  global asientos
   
  with lock:    # El lock se libera automáticamente al salir del bloque
    if asientos > 0:
         asientos -= 1
         print (f"Reserva realizada, quedan {asientos} asientos disponibles.")
    else:
         print ("No hay asientos disponibles.")
    

# Crear 50 hilos
hilos = []
for i in range(50):
    hilo = threading.Thread(target=reservar)
    hilos.append(hilo)
    hilo.start()

# Esperar a que todos terminen
for hilo in hilos:
    hilo.join()


print ("cantidad de asientos disponibles:", asientos)