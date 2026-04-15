from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib import error, request


def crear_cita(intento: int, horario: str = "10am") -> tuple[int, int, str]:
    url = f"http://127.0.0.1:8000/crear_cita?horario={horario}&paciente=paciente_{intento}&ttl_segundos=10"
    peticion = request.Request(url, method="POST")

    try:
        with request.urlopen(peticion, timeout=5) as resp:
            cuerpo = resp.read().decode("utf-8")
            return intento, resp.getcode(), cuerpo
    except error.HTTPError as exc:
        cuerpo = exc.read().decode("utf-8")
        return intento, exc.code, cuerpo
    except Exception as exc:
        return intento, 0, str(exc)


def prueba_concurrencia() -> None:
    horario = "10am"
    total = 10

    print("\nINICIANDO PRUEBA DE CONCURRENCIA")
    print(f"Horario: {horario}")
    print(f"Lanzando {total} peticiones simultaneas...\n")

    resultados = []

    with ThreadPoolExecutor(max_workers=total) as executor:
        futuros = [executor.submit(crear_cita, i, horario) for i in range(total)]
        for futuro in as_completed(futuros):
            resultados.append(futuro.result())

    exitos = sum(1 for _, status, _ in resultados if status == 200)
    fallidas = total - exitos

    print("RESULTADOS:")
    for intento, status, cuerpo in sorted(resultados, key=lambda item: item[0]):
        if status == 200:
            print(f"Intento {intento}: EXITO - {cuerpo}")
        else:
            print(f"Intento {intento}: FALLO ({status}) - {cuerpo}")

    print(f"\nPeticiones exitosas: {exitos}")
    print(f"Peticiones fallidas: {fallidas}")
    print("Verificacion: solo una cita deberia crearse correctamente")


if __name__ == "__main__":
    prueba_concurrencia()