Taller Independiente: Investigacion

Este repositorio contiene el desarrollo del taller independiente, que incluye la investigación y la práctica de instalación y uso de Git y GitHub.

## Qué hice

En este taller realicé las siguientes actividades de investigacion sobre los siguientes temas:

## Qué es el modelo Cliente-Servidor

El modelo cliente-servidor es una arquitectura de comunicación en la que las tareas o cargas de trabajo se reparten entre los proveedores de un recurso o servicio, llamados servidores, y los solicitantes del servicio, llamados clientes.
•       Cliente: Es el programa o dispositivo que inicia la comunicación para solicitar un servicio.
Ejemplo:
•       El navegador web cuando querés ver una página.
•       La app del correo en tu celular cuando revisás tus mensajes.
•       Un videojuego online cuando te conectás a una partida.

•       Servidor: Es el programa o dispositivo que espera pasivamente las solicitudes de los clientes y ofrece el servicio.
Ejemplo:
•       La computadora donde está alojada una página web, que envía el contenido a tu navegador.
•       El sistema de Gmail que recibe tu pedido de mostrame los correos nuevos y te los entrega.
•       El servidor de un juego que sincroniza tu partida con la de otros jugadores.

Cómo se comunican
Para que cliente y servidor se entiendan, necesitan hablar el mismo idioma. Ese idioma se llama protocolo. En el caso de la web, usan HTTP el que hace que las páginas se vean como las conocemos. La comunicación viaja por la red, que puede ser Internet o una red local, y el cliente siempre es el que inicia la conversación.

## Diferencia entre Proceso e Hilo

Tanto los procesos como los hilos son unidades de ejecución en un sistema operativo, pero tienen diferencias fundamentales que serían las siguientes:

## Definición
Un proceso es, básicamente, un programa en ejecución. Cuando abrís el navegador, el editor de texto o cualquier aplicación, lo que está corriendo en tu computadora es un proceso. Es una entidad independiente y "pesada", porque el sistema operativo le asigna sus propios recursos.

Un hilo (o thread) es la unidad más pequeña de procesamiento. Un proceso puede tener uno o varios hilos ejecutándose dentro de él. Si el proceso fuera una fábrica, los hilos serían los trabajadores: cada uno hace una tarea distinta, pero todos trabajan para el mismo objetivo y comparten el mismo espacio.

## Memoria
Cada proceso tiene su propio espacio de memoria exclusivo. Esto significa que un proceso no puede acceder directamente a la memoria de otro. Si dos procesos necesitan compartir información, deben usar mecanismos especiales que ofrece el sistema operativo.

En cambio, los hilos que pertenecen a un mismo proceso comparten la memoria y los recursos de ese proceso. Esto les permite trabajar de forma más coordinada, pero también requiere cuidado, porque si un hilo modifica un dato, los otros lo ven al instante.

## Comunicación
La comunicación entre procesos (conocida como IPC, por sus siglas en inglés) es más compleja y lenta. Como cada proceso vive en su propio espacio de memoria aislado, el sistema operativo tiene que intervenir para que puedan intercambiar información, lo que consume tiempo y recursos.

Entre hilos, la comunicación es mucho más sencilla y rápida. Como comparten la misma memoria, pueden leer y modificar las mismas variables directamente, sin necesidad de intermediarios. Esto los hace ideales para tareas que necesitan trabajar juntas de forma ágil.

## Cambio de Contexto
Cuando el sistema operativo deja de ejecutar un proceso y pasa a otro, tiene que hacer un "cambio de contexto". Esto implica guardar toda la información del proceso actual (memoria, registros, estado) y cargar la del siguiente. Es un proceso costoso en tiempo y recursos.

En cambio, cambiar entre hilos de un mismo proceso es mucho más rápido. Como comparten el espacio de memoria, no hay que guardar y cargar tanta información. Por eso a los hilos se les llama también "procesos ligeros": son más ágiles y eficientes.

## Recursos
Crear y gestionar un proceso es costoso para el sistema operativo. Tiene que reservarle memoria, asignarle recursos y mantenerlo aislado de otros procesos. Es como abrir una nueva tienda: requiere su propio local, empleados y permisos.

Los hilos, en cambio, son más "baratos" de crear y administrar. Como ya existen dentro de un proceso, aprovechan los recursos que éste ya tiene asignados. Crear un hilo nuevo es mucho más rápido y liviano que crear un proceso completo.

**Subida de Archivos:** Aprendí a subir los archivos de la clase a este repositorio, ya sea a través de la interfaz web de GitHub o mediante comandos Git desde la terminal.
**Documentación:** Finalmente, redacté este archivo README.md para documentar el proceso, lo aprendido y las dificultades encontradas, cumpliendo con los requisitos del entregable.

## Qué aprendí
Realizar este taller me permitió aprender y afianzar los siguientes conceptos:

*   **Modelo Cliente-Servidor:** Comprendí que es una arquitectura fundamental en redes donde un cliente (solicitante) y un servidor (proveedor) interactúan para intercambiar información, como ocurre al navegar por internet.
*   **Procesos vs. Hilos:** Aprendí que un proceso es un programa en ejecución con su propio espacio de memoria, mientras que los hilos son subprocesos que viven dentro de un proceso y comparten su memoria, lo que los hace más ligeros y rápidos para tareas concurrentes.
*   **Manejo de Git:** Aprendí a instalar Git, configurarlo y a usar comandos básicos como git init, git add, git commit y git push para conectar un proyecto local con un repositorio remoto en GitHub.
*   **Uso de GitHub:** Aprendí a crear un repositorio, a subir archivos tanto por la web como por línea de comandos, y a editar el archivo README.md para documentar mis proyectos.

## Dificultades

**Comandos de Git:** Al principio, recordar la secuencia exacta de comandos para conectar el repositorio local con el remoto (git remote add origin [url] y git push -u origin main) fue un poco confuso, pero después de practicarlo un par de veces me quedo un poco mas claro por que me enredaba tambien con las rams si era main o master


## Cuestionario clase #3

FastAPI
## Preguntas sobre concurrencia

### ¿Es seguro usar variable global?
No es seguro. Cuando varios usuarios usan la API al mismo tiempo, las variables globales pueden causar problemas como condiciones de carrera donde los datos se corrompen.

### ¿Dónde aparece el recurso compartido?
Los recursos compartidos son la lista 'clientes' y el 'contador_clientes' que están en memoria y son accedidos por todas las peticiones.

### ¿Se debería usar lock en producción?
No es recomendable porque crea cuellos de botella. En producción se usan bases de datos como PostgreSQL o MySQL.


