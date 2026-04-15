# Evidencias - Parte Independiente

## 1. Objetivo del trabajo

Implementar una API de citas que permita:
- crear una cita,
- consultar una cita,
- cancelar una cita,

y controlar que no se pueda reservar dos veces el mismo horario cuando hay varias peticiones al mismo tiempo.

## 2. Archivos del desarrollo

- test_api.py: API principal con los endpoints.
- test_redis.py: prueba basica de conexion y lock en Redis.
- prueba_concurrencia.py: prueba de multiples peticiones simultaneas.

## 3. Endpoints implementados

- POST /crear_cita
- GET /ver_cita
- DELETE /cancelar_cita

## 4. Como se uso Redis

Redis se uso para coordinar el acceso a las citas:

- Lock distribuido: evita que dos procesos creen o cancelen la misma cita al mismo tiempo.
- Expiracion (TTL): la cita queda en estado ocupado por un tiempo y luego se elimina sola.
- Manejo de errores: respuestas claras cuando hay conflicto, cuando la cita no existe o cuando falla Redis.

## 5. Prueba de concurrencia

Se ejecuta el script prueba_concurrencia.py para lanzar varias peticiones sobre la misma hora.

Resultado esperado:
- solo una peticion crea la cita,
- las demas responden que la cita esta ocupada.

Con esto se demuestra que el sistema evita doble reserva.

## 6. Evidencias (capturas sugeridas)

1. Redis activo y API levantada en terminal.
2. Primera creacion de cita con respuesta correcta.
3. Segundo intento de la misma hora con mensaje Cita ocupada.
4. Redis Commander mostrando la clave de la cita en estado ocupado.
5. La misma clave desapareciendo despues del TTL.
6. Resultado de prueba_concurrencia.py mostrando una creacion y varios conflictos.

## 7. Comandos usados

Levantar API:

```bash
uvicorn test_api:app --reload
```

Crear cita:

```bash
curl -X POST "http://127.0.0.1:8000/crear_cita?horario=10am&paciente=juan&ttl_segundos=20"
```

Ver cita:

```bash
curl "http://127.0.0.1:8000/ver_cita?horario=10am"
```

Cancelar cita:

```bash
curl -X DELETE "http://127.0.0.1:8000/cancelar_cita?horario=10am"
```

Prueba de concurrencia:

```bash
python3 prueba_concurrencia.py
```

## 8. Conexion con SSDD

Que problema se resolvio?

Se resolvio la condicion de carrera: varios clientes intentando reservar la misma hora al mismo tiempo.

Como actua Redis como coordinador?

Redis actua como coordinador central. Define quien reserva primero, bloquea los demas intentos mientras la cita esta ocupada y libera automaticamente por tiempo de expiracion.

## 9. Conclusion breve

La solucion funciona para escenarios concurrentes simples. Se evita la doble reserva, la cita se mantiene ocupada durante el TTL y luego se libera sola, lo que mantiene consistencia en el sistema.

