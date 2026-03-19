# Sistema de Reservas Concurrente

Actividad Independiente — Programación Concurrente
Institución: COTECNOVA
Lenguaje: Python 3

---

## Descripción del Problema

Cuando varios usuarios intentan reservar cursos al mismo tiempo, pueden ocurrir condiciones de carrera: dos hilos leen el mismo valor, ambos creen que hay cupo disponible y ambos reservan, dejando el contador en un estado inválido.

Este proyecto simula 50 usuarios intentando reservar 10 cursos, comparando tres enfoques.

---

## Estructura del Repositorio

sistema_reservas/
├── sistema_reservas.py
└── README.md

---

## Requisitos

- Python 3.6 o superior
- Librería threading (incluida en Python)

## Cómo ejecutar

python sistema_reservas.py

---

## Parte 1 — Sin Lock

### ¿Qué hace?
50 hilos acceden y modifican la variable cursos sin ninguna protección.

### Código

    import threading

    cursos = 10
    usuarios = 50

    def reservar_sin_lock():
        global cursos
        if cursos > 0:
            cursos -= 1
            print(f"Reserva realizada, quedan {cursos} cursos disponibles.")
        else:
            print("No hay cursos disponibles.")

    hilos = []
    for i in range(usuarios):
        hilo = threading.Thread(target=reservar_sin_lock)
        hilos.append(hilo)
        hilo.start()

    for hilo in hilos:
        hilo.join()

    print("Cantidad de cursos disponibles:", cursos)

### Problema
Dos hilos pueden leer el mismo valor antes de que alguno escriba, lo que puede dejar el contador en un valor incorrecto. Los datos son inconsistentes e impredecibles.

---

## Parte 2 — Con Lock

### ¿Qué hace?
Se usa un Lock para garantizar que solo un hilo a la vez pueda leer y modificar los cursos.

### Código

    import threading

    cursos = 10
    usuarios = 50
    lock = threading.Lock()

    def reservar_con_lock():
        global cursos
        with lock:
            if cursos > 0:
                cursos -= 1
                print(f"Reserva realizada, quedan {cursos} cursos disponibles.")
            else:
                print("No hay cursos disponibles.")

    hilos = []
    for i in range(usuarios):
        hilo = threading.Thread(target=reservar_con_lock)
        hilos.append(hilo)
        hilo.start()

    for hilo in hilos:
        hilo.join()

    print("Cantidad de cursos disponibles:", cursos)

### Ventaja
Solo un hilo entra al bloque with lock a la vez. Los cursos nunca quedan en un valor incorrecto y los datos son siempre consistentes.

---

## Parte 3 — Con Semáforo

### ¿Qué hace?
Se usa un Semaphore(3) para permitir que máximo 3 hilos accedan al mismo tiempo. El cuarto hilo espera hasta que uno de los tres salga.

### Código

    import threading

    cursos = 10
    usuarios = 50
    semaforo = threading.Semaphore(3)

    def reservar_con_semaforo():
        global cursos
        with semaforo:
            if cursos > 0:
                cursos -= 1
                print(f"Reserva realizada, quedan {cursos} cursos disponibles.")
            else:
                print("No hay cursos disponibles.")

    hilos = []
    for i in range(usuarios):
        hilo = threading.Thread(target=reservar_con_semaforo)
        hilos.append(hilo)
        hilo.start()

    for hilo in hilos:
        hilo.join()

    print("Cantidad de cursos disponibles:", cursos)

### Diferencia con Lock

- Lock: solo 1 hilo a la vez
- Semáforo: hasta N hilos al mismo tiempo (en este caso 3)
- El semáforo es útil cuando el recurso puede tolerar cierto nivel de concurrencia

---

## Resultados

Sin Lock     — Condición de carrera, datos inconsistentes
Con Lock     — Un hilo a la vez, datos siempre correctos
Con Semáforo — Hasta 3 hilos simultáneos, datos controlados

### Conclusión

- Sin Lock: nunca debe usarse cuando hay recursos compartidos.
- Lock: la solución más simple y segura para exclusión mutua total.
- Semáforo: ideal cuando se quiere limitar la concurrencia sin eliminarla.

---

Desarrollado como actividad independiente — COTECNOVA 2025
