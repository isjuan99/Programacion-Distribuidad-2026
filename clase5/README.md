# Grupo 3 - Microservicio de Creación de Citas

##  Integrantes
-  Juan David Rios
-  Juan Camilo Gonzalez
-  Juan Felipe Rojas
-  Sebastian Perez

## 📋 Descripción
Microservicio que implementa la funcionalidad completa de los 6 grupos del sistema de citas médicas. Este servicio maneja desde el registro de pacientes hasta la cancelación de citas.

## 🔗 Endpoint Implementados

| Grupo | Método | Endpoint | Descripción |
|-------|--------|----------|-------------|
| **Grupo 1** | `POST` | `/crear/pacientes` | Registrar un nuevo paciente |
| **Grupo 2** | `GET` | `/listar/pacientes/{id}` | Consultar información de un paciente |
| **Grupo 3** | `POST` | `/crear/citas` | Crear una nueva cita médica |
| **Grupo 4** | `GET` | `/listar/citas/{paciente_id}` | Listar todas las citas de un paciente |
| **Grupo 5** | `DELETE` | `/cancelar/citas/{id}` | Cancelar una cita existente |
| **Grupo 6** | `POST` | `/hacer/reservar-cita` | API Gateway para reservar citas |

---
`POST` | `/crear/pacientes`

###  Parámetros (TODOS)
| Parámetro | Tipo | Obligatorio | Descripción | Validación | Ejemplo |
|-----------|------|-------------|-------------|------------|---------|
| nombre | string | **SÍ** | Nombre completo del paciente | Mínimo 3 caracteres, máximo 100 | `Juan Carlos Perez Gomez` |
| email | string | **SÍ** | Correo electrónico del paciente | Formato email válido, único en BD | `juan.perez@email.com` |



`GET /listar/pacientes/{id}`

| Parámetro | Tipo | Obligatorio | Descripción | Validación | Ejemplo |
|-----------|------|-------------|-------------|------------|---------|
| id | integer | **SÍ** | ID único del paciente | • Debe ser un número entero positivo<br>• Debe existir en la base de datos<br>• Mayor a 0 | `5` |


`POST` | `/crear/citas`

| Parámetro | Tipo | Obligatorio | Descripción |
|-----------|------|-------------|-------------|
| paciente_id | integer | Sí | ID del paciente que solicita la cita |
| fecha | string | Sí | Fecha de la cita (formato: DD-MM-YYYY) |


`GET` | `/listar/citas/{paciente_id}`

| Parámetro | Tipo | Obligatorio | Descripción | Validación | Ejemplo |
|-----------|------|-------------|-------------|------------|---------|
| paciente_id | integer | **SÍ** | ID único del paciente | • Debe ser un número entero positivo<br>• Mayor a 0<br>• No necesariamente debe existir (retorna array vacío) | `5` |



`DELETE` | `/cancelar/citas/{id}`

| Parámetro | Tipo | Obligatorio | Descripción | Validación | Ejemplo |
|-----------|------|-------------|-------------|------------|---------|
| id | integer | **SÍ** | ID único de la cita a cancelar | • Debe ser un número entero positivo<br>• Mayor a 0<br>• Debe existir en la base de datos<br>• La cita debe existir | `1` |


##  Ejemplo de Request

# Crear paciente
- ```bash
curl -X POST "http://172.20.197.180:8001/crear/pacientes?nombre=Juan%20Carlos%20Perez%20Gomez&email=juan.perez@email.com"

# Listar paciente
-```bash
curl "http://172.20.197.180:8001/listar/pacientes/5"

#  Crear cita

- ```bash
curl -X POST "http://172.20.197.180:8001/crear/citas?paciente_id=1&fecha=15-03-2026"

# Listar cita

```bash
curl "http://172.20.197.180:8001/listar/citas/5"


#Eliminar cita

```bash
curl -X DELETE "http://172.20.197.180:8001/cancelar/citas/1"



## Ejemplo Response 

# Crear paciente
{
  "mensaje": "Paciente registrado"
}


# listar paciente

{
  "id": 5,
  "nombre": "Juan Carlos Perez Gomez",
  "email": "juan.perez@email.com"
} 


# Crear Cita 

{
  "mensaje": "Cita creada exitosamente",
  "paciente_id": 5,
  "fecha": "25-12-2026"
}


# Listar cita

[
  {
    "id": 1,
    "paciente_id": 5,
    "fecha": "25-12-2026",
    "estado": "activa"
  },
  {
    "id": 2,
    "paciente_id": 5,
    "fecha": "30-12-2026",
    "estado": "activa"
  },
  {
    "id": 3,
    "paciente_id": 5,
    "fecha": "05-01-2027",
    "estado": "cancelada"
  },
  {
    "id": 4,
    "paciente_id": 5,
    "fecha": "15-01-2027",
    "estado": "activa"
  }
]


# Eliminar cita

{
  "mensaje": "Cita cancelada"
} 


## **IP Y PUERTO DEL SERVICIO**

| **IP del Servidor** | `172.20.197.180` |
| **Puerto** | `8001` |
# Desde cualquier otro equipo en la red
curl http://172.16.0.40:8001/
