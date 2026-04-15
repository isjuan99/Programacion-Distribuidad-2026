import uuid

import redis
from fastapi import FastAPI, HTTPException
from redis.exceptions import RedisError

app = FastAPI()

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

LOCK_TTL_SECONDS = 10


def liberar_lock_seguro(lock_key: str, token: str) -> None:
    script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    try:
        r.eval(script, 1, lock_key, token)
    except RedisError:
        # Si falla la liberacion, el lock igual caduca por TTL.
        pass


@app.post("/crear_cita")
def crear_cita(horario: str = "10am", paciente: str = "juan", ttl_segundos: int = 10):
    horario_normalizado = horario.strip().lower()
    cita_key = f"cita_{horario_normalizado}"
    lock_key = f"lock_{cita_key}"
    token = str(uuid.uuid4())

    try:
        lock = r.set(lock_key, token, nx=True, ex=LOCK_TTL_SECONDS)
        if not lock:
            raise HTTPException(status_code=409, detail="Otro proceso esta reservando esta cita")

        try:
            # Guardado atomico: si ya existe la cita para esa hora, no la vuelve a crear.
            creada = r.set(cita_key, "ocupado", nx=True, ex=ttl_segundos)
            if not creada:
                raise HTTPException(status_code=409, detail="Cita ocupada")

            return {
                "mensaje": "Cita creada",
                "horario": horario_normalizado,
                "paciente": paciente,
                "estado": "ocupado",
                "expira_en": r.ttl(cita_key),
            }
        finally:
            liberar_lock_seguro(lock_key, token)

    except HTTPException:
        raise
    except RedisError as e:
        raise HTTPException(status_code=503, detail=f"Error Redis: {e}") from e


@app.get("/ver_cita")
def ver_cita(horario: str = "10am"):
    horario_normalizado = horario.strip().lower()
    cita_key = f"cita_{horario_normalizado}"

    try:
        data = r.get(cita_key)
        if not data:
            raise HTTPException(status_code=404, detail="Cita no encontrada")

        return {
            "horario": horario_normalizado,
            "estado": data,
            "expira_en": r.ttl(cita_key),
        }
    except HTTPException:
        raise
    except RedisError as e:
        raise HTTPException(status_code=503, detail=f"Error Redis: {e}") from e


@app.delete("/cancelar_cita")
def cancelar_cita(horario: str = "10am"):
    horario_normalizado = horario.strip().lower()
    cita_key = f"cita_{horario_normalizado}"
    lock_key = f"lock_{cita_key}"
    token = str(uuid.uuid4())

    try:
        lock = r.set(lock_key, token, nx=True, ex=LOCK_TTL_SECONDS)
        if not lock:
            raise HTTPException(status_code=409, detail="Otro proceso esta cancelando esta cita")

        try:
            deleted = r.delete(cita_key)
            if deleted == 0:
                raise HTTPException(status_code=404, detail="Cita no encontrada")

            return {"mensaje": "Cita cancelada"}
        finally:
            liberar_lock_seguro(lock_key, token)

    except HTTPException:
        raise
    except RedisError as e:
        raise HTTPException(status_code=503, detail=f"Error Redis: {e}") from e