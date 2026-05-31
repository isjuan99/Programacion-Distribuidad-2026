# ⚗ Aroma-Distribuido — Sistema Distribuido v2.0

Plataforma de e-commerce de perfumería de lujo implementada como **sistema distribuido** con FastAPI, Vue 3, Redis, RabbitMQ, Worker independiente, Docker, Dozzle, Portainer, GitHub Actions y observabilidad completa.

[![CI/CD](https://github.com/isjuan99/Programacion-Distribuidad-2026/actions/workflows/ci.yml/badge.svg)](https://github.com/isjuan99/Programacion-Distribuidad-2026/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/docker-compose-blue?logo=docker)](docker-compose.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](backend/)
[![Vue 3](https://img.shields.io/badge/Vue-3.4-brightgreen?logo=vue.js)](frontend/)

---

## Tabla de Contenidos

1. [Requisitos](#requisitos)
2. [Inicio Rápido](#inicio-rápido)
3. [Arquitectura](#arquitectura)
4. [Servicios](#servicios)
5. [Variables de Entorno](#variables-de-entorno)
6. [Redis — Caché](#redis--caché)
7. [RabbitMQ — Mensajería](#rabbitmq--mensajería)
8. [Worker Independiente](#worker-independiente)
9. [Swagger API](#swagger-api)
10. [Logs Estructurados](#logs-estructurados)
11. [Dozzle — Visualización de Logs](#dozzle--visualización-de-logs)
12. [Portainer — Gestión Docker](#portainer--gestión-docker)
13. [GitHub Actions CI/CD](#github-actions-cicd)
14. [Simulación de Fallos](#simulación-de-fallos)
15. [Checklist Sistemas Distribuidos](#checklist-sistemas-distribuidos)

---

## Requisitos

| Herramienta | Versión mínima |
|-------------|----------------|
| Docker Desktop | 24.x |
| Docker Compose | v2 (incluido en Docker Desktop) |
| Git | cualquier |
| RAM disponible | 4 GB mínimo, 8 GB recomendado |

---

## Inicio Rápido

```bash
# 1. Clonar el repositorio
git clone https://github.com/isjuan99/Programacion-Distribuidad-2026.git
cd aroma-distribuido

# 2. Levantar todos los servicios (8 contenedores)
docker compose up -d

# 3. Verificar estado
docker compose ps

# 4. Crear administrador inicial
docker compose exec backend python create_admin.py
```

### URLs del sistema

| Servicio | URL | Credenciales |
|----------|-----|-------------|
| Frontend (Vue 3) | http://localhost | — |
| Backend API | http://localhost:8000 | — |
| Swagger UI | http://localhost:8000/docs | JWT |
| Redoc | http://localhost:8000/redoc | — |
| RabbitMQ Management | http://localhost:15672 | aroma_user / aroma_secret |
| Dozzle (Logs) | http://localhost:8888 | Sin auth |
| Portainer | http://localhost:9000 | Configurar al inicio |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                   DOCKER NETWORK: aroma-network              │
│                                                              │
│  Browser → [Frontend :80] → /api/v1 → [Backend :8000]       │
│                                            │                 │
│                         ┌──────────────────┼──────────┐      │
│                         ▼                 ▼           ▼      │
│                    [PostgreSQL]        [Redis]   [RabbitMQ]  │
│                      :5432             :6379       :5672     │
│                                                    │         │
│                                              [Worker]        │
│                                                              │
│  [Dozzle :8888]                      [Portainer :9000]       │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de un pedido

```
Cliente → POST /api/v1/orders
         ↓
    FastAPI Backend
    ├── Valida stock (PostgreSQL)
    ├── Crea orden (PostgreSQL)
    ├── Publica evento order.created (RabbitMQ)
    └── Invalida caché de productos (Redis)
         ↓
    Worker consume order.created
    ├── Envía email de confirmación
    └── Registra en logs JSON
```

---

## Servicios

| Contenedor | Imagen | Puerto(s) | Rol |
|-----------|--------|-----------|-----|
| aroma-frontend | custom (Node→Nginx) | 80 | Vue 3 SPA |
| aroma-backend | custom (Python 3.11) | 8000 | FastAPI |
| aroma-db | postgres:15-alpine | 5432 | PostgreSQL |
| aroma-redis | redis:7-alpine | 6379 | Caché |
| aroma-rabbitmq | rabbitmq:3.13-management | 5672, 15672 | Mensajería |
| aroma-worker | custom (Python 3.11) | — | Consumer |
| aroma-dozzle | amir20/dozzle | 8888 | Log viewer |
| aroma-portainer | portainer/portainer-ce | 9000, 9443 | Docker mgmt |

---

## Variables de Entorno

### Backend (`backend/.env`)

```env
# Base de Datos
DATABASE_URL=postgresql://aroma_user:aroma_secret@db:5432/aroma_db

# Seguridad
SECRET_KEY=cambiar-esto-en-produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://redis:6379/0
CACHE_TTL_PRODUCTS=300
CACHE_TTL_CATEGORIES=600
CACHE_TTL_FEATURED=120
CACHE_TTL_SEARCH=180

# RabbitMQ
RABBITMQ_URL=amqp://aroma_user:aroma_secret@rabbitmq:5672/
RABBITMQ_EXCHANGE=aroma_events

# SMTP Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=aromadistribuido@gmail.com
SMTP_PASSWORD=your-app-password

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id

# Stripe
STRIPE_SECRET_KEY=sk_test_xxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxx

# Servicio
SERVICE_NAME=aroma-backend
ENVIRONMENT=production
UPLOAD_DIR=/app/uploads
FRONTEND_URL=http://localhost:80
```

### Frontend (`frontend/.env.local`)

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Redis — Caché

Redis se usa para cachear las respuestas más frecuentes del backend, reduciendo la carga sobre PostgreSQL.

### Estrategia de caché

| Patrón de clave | Contenido | TTL |
|----------------|-----------|-----|
| `products:list:*` | Listas paginadas con filtros | 5 min |
| `products:detail:{id}` | Detalle de producto | 5 min |
| `products:featured:*` | Productos destacados | 2 min |
| `products:related:{id}` | Productos relacionados | 5 min |
| `search:suggestions:*` | Autocompletado | 3 min |
| `categories:*` | Listas de categorías | 10 min |

### Invalidación automática

Al crear, actualizar o eliminar un producto, se invalidan automáticamente **todos** los patrones de caché relacionados usando `KEYS pattern` + `DEL`.

### Resiliencia (Degraded Mode)

Si Redis no está disponible, el backend **opera normalmente** consultando directamente PostgreSQL. El error se registra como `warning` en los logs JSON pero no interrumpe el servicio.

### Comandos útiles

```bash
# Conectar al CLI de Redis
docker compose exec redis redis-cli

# Ver todas las claves en caché
docker compose exec redis redis-cli KEYS "*"

# Estadísticas de Redis
docker compose exec redis redis-cli INFO stats

# Limpiar todo el caché
docker compose exec redis redis-cli FLUSHDB
```

---

## RabbitMQ — Mensajería

### Configuración

| Elemento | Valor |
|---------|-------|
| Exchange | `aroma_events` (topic, durable) |
| Queue — Orders | `aroma.orders` → routing: `order.*` |
| Queue — Users | `aroma.users` → routing: `user.*` |
| Queue — Inventory | `aroma.inventory` → routing: `inventory.*` |
| Queue — Notifications | `aroma.notifications` → routing: `#` (todos) |

### Eventos publicados

| Evento | Cuándo | Cola |
|--------|--------|------|
| `order.created` | Al crear un pedido | aroma.orders |
| `order.confirmed` | Al actualizar estado | aroma.orders |
| `order.shipped` | Al agregar tracking | aroma.orders |
| `user.registered` | Al registrar usuario | aroma.users |
| `inventory.updated` | Al modificar stock | aroma.inventory |

### Management UI

Accede a http://localhost:15672 con `aroma_user` / `aroma_secret` para ver:
- Exchanges y queues en tiempo real
- Mensajes encolados, consumidos y pendientes
- Gráficas de throughput
- Publicar mensajes de prueba manualmente

---

## Worker Independiente

El Worker es un servicio Python independiente que corre en su propio contenedor.

### Responsabilidades

- **Emails de confirmación**: Procesa `order.created` → envía email
- **Notificaciones de estado**: Procesa `order.confirmed` → notifica al cliente
- **Bienvenida**: Procesa `user.registered` → envía email de bienvenida
- **Inventario**: Procesa `inventory.updated` → invalida caché de Redis
- **Extensible**: Agregar handlers en `EVENT_HANDLERS` en `worker/main.py`

### Auto-reconexión

El worker se reconecta automáticamente a RabbitMQ si la conexión se pierde, con un delay de 5 segundos entre intentos.

### Ver logs del worker

```bash
# Logs en tiempo real
docker compose logs -f worker

# O desde Dozzle en http://localhost:8888
```

---

## Swagger API

La documentación automática de FastAPI está disponible en:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Tags organizativos

| Tag | Endpoints |
|-----|-----------|
| `Productos` | CRUD de productos, búsqueda, destacados |
| `Pedidos` | Crear orden, estado, tracking |
| `Autenticación` | Login, registro, tokens |
| `Observabilidad` | Health check, métricas |
| `Simulación de Fallos` | Redis, RabbitMQ, Worker |

---

## Logs Estructurados

Todos los logs del backend y worker usan formato JSON:

```json
{
  "asctime": "2026-05-30 10:15:23",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "service": "aroma-backend",
  "event": "request_completed",
  "endpoint": "/api/v1/products",
  "status": 200,
  "duration_ms": 45.2,
  "level": "INFO",
  "message": "Request completed",
  "environment": "production"
}
```

### Request ID

Cada solicitud HTTP recibe un UUID único (`X-Request-ID`) que aparece en:
- El header de respuesta: `X-Request-ID: uuid`
- Todos los logs relacionados con esa solicitud

---

## Dozzle — Visualización de Logs

Dozzle provee una interfaz web para ver los logs de todos los contenedores en tiempo real.

**URL**: http://localhost:8888

Características:
- Ver logs de múltiples contenedores simultáneamente
- Búsqueda y filtrado en tiempo real
- Auto-scroll y pausa
- Filtrado por contenedor `aroma-*`

---

## Portainer — Gestión Docker

Portainer provee una UI web para administrar el entorno Docker.

**URL**: http://localhost:9000

En el primer inicio, configura una contraseña de administrador.

Desde Portainer puedes:
- Ver, iniciar, detener y reiniciar contenedores
- Inspeccionar logs
- Ver estadísticas de CPU/Memoria
- Gestionar volúmenes y redes

---

## GitHub Actions CI/CD

El pipeline `.github/workflows/ci.yml` tiene 5 jobs:

| Job | Trigger | Qué hace |
|-----|---------|---------|
| `backend-test` | Todos los push/PR | Instala deps, smoke tests, verifica imports |
| `frontend-build` | Todos los push/PR | `npm ci`, `npm run build`, sube artefacto |
| `worker-test` | Todos los push/PR | Instala deps, verifica imports del worker |
| `docker-build-push` | Solo push a `main` | Build y push a Docker Hub |
| `deploy-pages` | Solo push a `main` | Despliega `docs/` en GitHub Pages |

### Configurar secrets en GitHub

Para el push a Docker Hub, configura en Settings → Secrets:

```
DOCKERHUB_USERNAME = tu-usuario
DOCKERHUB_TOKEN    = tu-access-token
```

---

## Simulación de Fallos

El endpoint `/api/v1/simulate/*` permite demostrar la resiliencia del sistema.

### 1. Caída de Redis

```bash
curl -X POST http://localhost:8000/api/v1/simulate/redis-failure
```

**Resultado**: El sistema opera en modo degradado. El tráfico va directo a PostgreSQL.

### 2. Caída de RabbitMQ

```bash
curl -X POST http://localhost:8000/api/v1/simulate/rabbitmq-failure
```

**Resultado**: El evento no se publica pero el pedido se guarda en DB.

### 3. Caída del Worker

```bash
# Detener el worker
docker compose stop worker

# Los mensajes quedan encolados en RabbitMQ (durables)
# Reiniciar — procesa los mensajes pendientes
docker compose start worker
docker compose logs -f worker
```

### 4. Estado del sistema distribuido

```bash
curl http://localhost:8000/api/v1/simulate/status
```

---

## Checklist Sistemas Distribuidos

| # | Requisito | Estado | Archivo |
|---|-----------|--------|---------|
| 1 | Redis | ✅ | `backend/app/core/redis_client.py` |
| 2 | RabbitMQ | ✅ | `backend/app/core/rabbitmq.py` |
| 3 | Worker independiente | ✅ | `worker/main.py` |
| 4 | Swagger mejorado | ✅ | Tags y descripciones en todos los routers |
| 5 | Logs estructurados JSON | ✅ | `backend/app/middleware/logging_setup.py` |
| 6 | Request ID | ✅ | `backend/app/middleware/request_id.py` |
| 7 | Dockerfiles optimizados | ✅ | backend, frontend, worker |
| 8 | Docker Compose | ✅ | `docker-compose.yml` — 8 servicios |
| 9 | Dozzle | ✅ | http://localhost:8888 |
| 10 | Portainer | ✅ | http://localhost:9000 |
| 11 | GitHub Actions | ✅ | `.github/workflows/ci.yml` — 5 jobs |
| 12 | Observabilidad básica | ✅ | `/api/v1/health` |
| 13 | Variables de entorno | ✅ | `pydantic-settings`, `.env.example` |
| 14 | README completo | ✅ | Este archivo |
| 15 | Simulación de fallos | ✅ | `backend/app/api/simulate.py` |

---

## Stack Tecnológico

**Backend**: Python 3.11, FastAPI 0.111, SQLAlchemy 2.0, Alembic, Uvicorn  
**Frontend**: Vue 3.4, Pinia, Vue Router 4, Axios, TailwindCSS, Vite  
**Base de datos**: PostgreSQL 15  
**Caché**: Redis 7 (LRU, 256 MB)  
**Mensajería**: RabbitMQ 3.13 (AMQP, topic exchange)  
**Worker**: Python 3.11, aio-pika  
**Infraestructura**: Docker, Docker Compose, Nginx  
**Observabilidad**: Dozzle, Portainer, JSON logging  
**CI/CD**: GitHub Actions, Docker Hub  
**Docs**: GitHub Pages
