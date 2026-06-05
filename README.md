# Aroma-Distribuido 🌸

[![CI/CD](https://github.com/isjuan99/Programacion-Distribuidad-2026/actions/workflows/ci.yml/badge.svg)](https://github.com/isjuan99/Programacion-Distribuidad-2026/actions/workflows/ci.yml)

**Plataforma de e-commerce de perfumería de lujo con arquitectura de sistemas distribuidos.**

Desarrollada con FastAPI + Vue 3, incluye Redis para caché, RabbitMQ para mensajería asíncrona, worker de procesamiento en segundo plano, y toda la infraestructura orquestada con Docker Compose.

---

## Tabla de contenidos

- [Demo y URLs](#demo-y-urls)
- [Arquitectura](#arquitectura)
- [Stack tecnológico](#stack-tecnológico)
- [Funcionalidades](#funcionalidades)
- [Guía de instalación desde cero](#guía-de-instalación-desde-cero)
- [Variables de entorno](#variables-de-entorno)
- [Comandos Make](#comandos-make)
- [API REST](#api-rest)
- [Estructura del proyecto](#estructura-del-proyecto)
- [CI/CD](#cicd)

---

## Demo y URLs

Una vez levantado el proyecto con `make start`:

| Servicio     | URL                          | Descripción                                  |
|--------------|------------------------------|----------------------------------------------|
| Frontend     | http://localhost             | Tienda + Panel admin                         |
| API REST     | http://localhost:8000/api/v1 | Backend FastAPI                              |
| Docs Swagger | http://localhost:8000/docs   | Documentación interactiva de la API          |
| Docs ReDoc   | http://localhost:8000/redoc  | Documentación alternativa                    |
| RabbitMQ UI  | http://localhost:15672       | Gestión de colas (aroma_user / aroma_secret) |
| Dozzle       | http://localhost:8888        | Visor de logs en tiempo real                 |
| Portainer    | http://localhost:9000        | Gestión visual de Docker                     |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Browser)                         │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP :80
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              NGINX (aroma-frontend :80)                          │
│   /          → Vue 3 SPA (build estático)                        │
│   /api/*     → proxy → backend:8000                              │
│   /uploads/* → proxy → backend:8000                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI (aroma-backend :8000)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │   Auth   │  │ Products │  │  Orders  │  │    Returns     │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ Loyalty  │  │ Wishlist │  │ Payments │  │    Reports     │  │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
└────────┬──────────────────────────┬────────────────────────────┘
         │                          │
         ▼                          ▼
┌────────────────┐       ┌──────────────────────┐
│  PostgreSQL    │       │  Redis               │
│  aroma-db:5432 │       │  aroma-redis:6379    │
│  (datos)       │       │  (caché + sesiones)  │
└────────────────┘       └──────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  RabbitMQ            │
                         │  aroma-rabbitmq:5672 │
                         │  (eventos asíncronos)│
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Worker              │
                         │  aroma-worker        │
                         │  (emails, notif.)    │
                         └──────────────────────┘
```

---

## Stack tecnológico

### Backend

| Tecnología          | Versión | Uso                            |
|---------------------|---------|--------------------------------|
| Python              | 3.11    | Lenguaje principal             |
| FastAPI             | 0.111   | Framework API REST             |
| SQLAlchemy          | 2.0     | ORM para PostgreSQL            |
| Alembic             | 1.13    | Migraciones de BD              |
| Pydantic v2         | 2.7     | Validación de datos            |
| Redis               | 5.0     | Caché (productos, búsquedas)   |
| aio-pika            | 9.4     | Cliente RabbitMQ async         |
| python-jose         | 3.3     | JWT tokens                     |
| passlib + bcrypt    | —       | Hash de contraseñas            |
| google-auth         | 2.29    | Verificación OAuth Google      |
| Pillow              | 10.3    | Procesamiento de imágenes      |
| aiosmtplib          | 3.0     | Envío de emails async          |
| Stripe              | 9.5     | Procesamiento de pagos         |
| python-json-logger  | 2.0     | Logs estructurados JSON        |

### Frontend

| Tecnología  | Versión | Uso                            |
|-------------|---------|--------------------------------|
| Vue 3       | 3.4     | Framework UI (Composition API) |
| Vite        | 5.2     | Build tool                     |
| Vue Router  | 4.3     | Enrutamiento SPA               |
| Pinia       | 2.1     | Estado global                  |
| Vue i18n    | 9.13    | Internacionalización (ES/EN)   |
| Axios       | 1.7     | HTTP client con interceptors   |
| Tailwind CSS| 3.4     | Estilos utilitarios            |
| VueUse      | 10.9    | Composables utilitarios        |
| Swiper      | 11.1    | Carruseles                     |

### Infraestructura

| Servicio   | Imagen                       | Puerto         |
|------------|------------------------------|----------------|
| PostgreSQL | postgres:15-alpine           | 5432           |
| Redis      | redis:7-alpine               | 6379           |
| RabbitMQ   | rabbitmq:3.13-management     | 5672, 15672    |
| Nginx      | nginx:alpine                 | 80             |
| Dozzle     | amir20/dozzle                | 8888           |
| Portainer  | portainer/portainer-ce       | 9000, 9443     |

---

## Funcionalidades

### Tienda (cliente)

- **Catálogo** con filtros por marca, categoría, precio, tamaño, género y notas olfativas
- **Búsqueda** con autocompletado en tiempo real
- **Página de producto** con galería de imágenes, variantes de tamaño, perfil olfativo y productos relacionados
- **Carrito** persistente con gestión de cantidades
- **Checkout** completo con dirección de envío, aplicación de cupones y resumen de pedido
- **Ofertas** — página dedicada con badge de descuento y ordenamiento por % de descuento
- **Lista de deseos** (wishlist) sincronizada con la cuenta

### Autenticación

- Registro con verificación de correo electrónico
- Login con email/contraseña + JWT (access + refresh token)
- Login con Google OAuth 2.0 (Google Identity Services)
- Recuperación de contraseña por email
- Modal global de autenticación (sin redirigir a /login)

### Cuenta de usuario (`/account`)

- **Mis pedidos** — historial con expansión inline: fotos, cantidades, costos, dirección, tracking
- **Devoluciones** — flujo completo: crear solicitud, subir fotos, tracking de envío, estados con timeline
- **Favoritos** — lista de deseos guardada
- **Puntos de lealtad** — historial de transacciones y saldo actual
- **Mis datos** — edición de perfil

### Panel de administración (`/admin`)

| Módulo        | Descripción                                                                 |
|---------------|-----------------------------------------------------------------------------|
| Dashboard     | KPIs en tiempo real (ventas, pedidos, clientes, inventario)                 |
| Productos     | CRUD completo con subida de imágenes, variantes y precio de oferta          |
| Marcas        | Gestión de casas de perfumería                                              |
| Categorías    | Árbol de categorías de productos                                            |
| Pedidos       | Listado con filtros, cambio de estado y asignación de tracking              |
| Devoluciones  | Gestión de solicitudes con fotos, tracking y tipo de reembolso              |
| Clientes      | Listado de usuarios registrados                                             |
| Inventario    | Control de stock con alertas de stock bajo                                  |
| Cupones       | Creación y gestión de códigos de descuento                                  |
| Reseñas       | Moderación de reseñas de productos                                          |
| Reportes      | Ventas por período, productos más vendidos, exportación a Excel             |
| Ajustes       | Configuración general de la tienda                                          |

### Sistemas distribuidos

- **Redis**: Caché de productos, categorías, búsquedas y destacados con TTL configurable. Invalidación automática al crear/editar/eliminar.
- **RabbitMQ**: Exchange de eventos `aroma_events`. Publica eventos de pedidos, usuarios e inventario.
- **Worker**: Consumidor de RabbitMQ que procesa emails de forma asíncrona (bienvenida, verificación, confirmación de pedido, envío, devolución).
- **Logs estructurados**: JSON logging con Request-ID por solicitud para trazabilidad distribuida.
- **Health checks**: Endpoint `/api/v1/health` con estado de Redis, RabbitMQ y base de datos.
- **Simulación de fallos**: Endpoint `/api/v1/simulate/*` para pruebas de resiliencia.

---

## Guía de instalación desde cero

### Requisitos previos

Antes de clonar el repositorio necesitas tener instalado:

| Herramienta    | Versión mínima | Verificar                  |
|----------------|----------------|----------------------------|
| Git            | 2.x            | `git --version`            |
| Docker Desktop | 4.x            | `docker --version`         |
| Docker Compose | 2.x            | `docker compose version`   |
| Make           | cualquiera     | `make --version`           |

> **Windows**: Docker Desktop incluye Docker Compose v2. Para `make`, instala [Make for Windows](https://gnuwin32.sourceforge.net/packages/make.htm) o usa Git Bash / WSL2.
>
> **macOS**: Instala Make con `brew install make` si no está disponible.
>
> **Linux**: `sudo apt install make` (Debian/Ubuntu) o `sudo dnf install make` (Fedora).

---

### Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/isjuan99/aroma-distribuido.git
cd aroma-distribuido
```

---

### Paso 2 — Configurar variables de entorno del backend

Copia el archivo de ejemplo y edítalo:

```bash
cp backend/.env.example backend/.env
```

Abre `backend/.env` y configura los siguientes valores:

```env
# ── Base de datos (Docker la maneja) ──────────────────────────────────────────
DATABASE_URL=postgresql://aroma_user:aroma_secret@db:5432/aroma_db

# ── Seguridad JWT ─────────────────────────────────────────────────────────────
# Genera una clave segura con: openssl rand -hex 32
SECRET_KEY=CAMBIA-ESTO-CON-UNA-CLAVE-SEGURA

# ── Redis y RabbitMQ (Docker los maneja) ──────────────────────────────────────
REDIS_URL=redis://redis:6379/0
RABBITMQ_URL=amqp://aroma_user:aroma_secret@rabbitmq:5672/

# ── Email SMTP ────────────────────────────────────────────────────────────────
# Con Gmail: activa "Contraseñas de aplicación" en tu cuenta Google
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-correo@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
EMAILS_FROM=tu-correo@gmail.com
EMAILS_FROM_NAME=Aroma-Distribuido

# ── Google OAuth (opcional) ───────────────────────────────────────────────────
GOOGLE_CLIENT_ID=

# ── Stripe (opcional) ─────────────────────────────────────────────────────────
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# ── Configuración del servicio ────────────────────────────────────────────────
FRONTEND_URL=http://localhost
ENVIRONMENT=production
```

> **¿Cómo generar SECRET_KEY?**
> ```bash
> # Linux / macOS:
> openssl rand -hex 32
>
> # Windows PowerShell:
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

---

### Paso 3 — Configurar variables de entorno del frontend

```bash
cp frontend/.env.example frontend/.env.local
```

Edita `frontend/.env.local`:

```env
# Client ID de Google (el mismo que pusiste en backend/.env)
VITE_GOOGLE_CLIENT_ID=tu-google-client-id.apps.googleusercontent.com
```

> Si no usas Google OAuth, puedes dejar este valor vacío.

---

### Paso 4 — Configurar Google OAuth (opcional)

Para activar el login con Google:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto o selecciona uno existente
3. Ve a **APIs y Servicios → Credenciales**
4. Clic en **Crear credenciales → ID de cliente OAuth 2.0**
5. Tipo de aplicación: **Aplicación web**
6. En **Orígenes de JavaScript autorizados** agrega: `http://localhost`
7. Copia el **Client ID** y pégalo en `backend/.env` y `frontend/.env.local`

---

### Paso 5 — Levantar el proyecto

```bash
make start
```

Este comando ejecuta `docker compose up -d --build` que:

1. Descarga las imágenes base (Python 3.11, Node 20, Nginx, PostgreSQL, Redis, RabbitMQ)
2. Construye las imágenes del backend y frontend
3. Crea la base de datos y todas las tablas automáticamente
4. Inicia los 8 servicios en segundo plano

> **Primera vez**: puede tardar entre 3 y 8 minutos según tu conexión a internet.

Verifica que todo esté corriendo:

```bash
make status
```

Deberías ver todos los servicios con estado `Up (healthy)`:

```
NAME              STATUS          PORTS
aroma-backend     Up (healthy)    0.0.0.0:8000->8000/tcp
aroma-db          Up (healthy)    0.0.0.0:5432->5432/tcp
aroma-dozzle      Up              0.0.0.0:8888->8080/tcp
aroma-frontend    Up              0.0.0.0:80->80/tcp
aroma-portainer   Up              0.0.0.0:9000->9000/tcp
aroma-rabbitmq    Up (healthy)    0.0.0.0:5672->5672/tcp
aroma-redis       Up (healthy)    0.0.0.0:6379->6379/tcp
aroma-worker      Up (healthy)
```

---

### Paso 6 — Crear el usuario administrador

Conéctate a la base de datos:

```bash
make db-shell
```

Dentro de psql ejecuta:

```sql
INSERT INTO users (
  email, first_name, last_name,
  hashed_password, is_active, is_admin, is_verified
) VALUES (
  'admin@tutienda.com',
  'Admin',
  'Principal',
  '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
  true, true, true
);
```

> Esto crea un admin con contraseña `secret`. **Cámbiala inmediatamente** después de tu primer ingreso.
>
> Para generar el hash de tu propia contraseña:
> ```bash
> docker exec aroma-backend python -c \
>   "from passlib.context import CryptContext; \
>    ctx = CryptContext(schemes=['bcrypt']); \
>    print(ctx.hash('tu-contraseña-aqui'))"
> ```

Escribe `\q` para salir de psql.

---

### Paso 7 — Abrir la aplicación

| Destino       | URL                         |
|---------------|-----------------------------|
| Tienda        | http://localhost            |
| Panel admin   | http://localhost/admin      |
| API docs      | http://localhost:8000/docs  |
| Logs          | http://localhost:8888       |
| Portainer     | http://localhost:9000       |

---

### Solución de problemas comunes

#### Los contenedores no levantan

```bash
make logs          # Ver todos los logs
make logs-backend  # Ver solo logs del backend
```

#### El backend tarda en estar "healthy"

Es normal en el primer arranque. El backend espera a que PostgreSQL, Redis y RabbitMQ pasen sus health checks, lo que puede tardar hasta 60 segundos.

#### Error "port already in use"

Alguno de los puertos (80, 8000, 5432, 6379, 5672, 15672) está ocupado por otro proceso.

```bash
# Windows (PowerShell)
netstat -ano | findstr :80

# macOS / Linux
lsof -i :80
```

Detén el proceso que usa ese puerto o cambia el mapeo en `docker-compose.yml`.

#### Quiero empezar desde cero (borrar todos los datos)

```bash
make fresh
```

> ⚠️ Este comando elimina todos los volúmenes Docker, incluyendo la base de datos.

#### Actualicé código del backend o frontend

```bash
make rebuild-backend    # Solo reconstruye el backend
make rebuild-frontend   # Solo reconstruye el frontend
make rebuild            # Reconstruye todo
```

---

## Variables de entorno

### `backend/.env`

| Variable                | Descripción                               | Requerida |
|-------------------------|-------------------------------------------|-----------|
| `DATABASE_URL`          | URL de conexión a PostgreSQL              | ✅        |
| `SECRET_KEY`            | Clave secreta para JWT (mín. 32 chars)    | ✅        |
| `REDIS_URL`             | URL de Redis                              | ✅        |
| `RABBITMQ_URL`          | URL de RabbitMQ con credenciales          | ✅        |
| `SMTP_HOST`             | Servidor SMTP                             | ✅        |
| `SMTP_PORT`             | Puerto SMTP (587 para TLS)                | ✅        |
| `SMTP_USER`             | Usuario/correo SMTP                       | ✅        |
| `SMTP_PASSWORD`         | Contraseña de aplicación SMTP             | ✅        |
| `EMAILS_FROM`           | Correo remitente                          | ✅        |
| `FRONTEND_URL`          | URL del frontend (para CORS)              | ✅        |
| `ENVIRONMENT`           | `development` o `production`              | ✅        |
| `GOOGLE_CLIENT_ID`      | Client ID de Google OAuth                 | Opcional  |
| `STRIPE_SECRET_KEY`     | Clave secreta de Stripe                   | Opcional  |
| `STRIPE_WEBHOOK_SECRET` | Secreto del webhook de Stripe             | Opcional  |

### `frontend/.env.local`

| Variable               | Descripción                  | Requerida |
|------------------------|------------------------------|-----------|
| `VITE_GOOGLE_CLIENT_ID`| Client ID de Google OAuth    | Opcional  |

---

## Comandos Make

```bash
# ── Inicio / Parada ───────────────────────────────────────────────
make start               # Build + levanta todo
make stop                # Detiene los contenedores
make restart             # Reinicia todos los contenedores
make rebuild             # Reconstruye imágenes y reinicia
make rebuild-backend     # Solo reconstruye el backend
make rebuild-frontend    # Solo reconstruye el frontend
make fresh               # Borra todo y arranca desde cero

# ── Logs ──────────────────────────────────────────────────────────
make logs                # Todos los servicios en tiempo real
make logs-backend        # Solo backend (FastAPI)
make logs-frontend       # Solo frontend (Nginx)
make logs-worker         # Solo worker (consumer RabbitMQ)
make logs-db             # Solo PostgreSQL

# ── Estado ────────────────────────────────────────────────────────
make status              # Estado de los contenedores
make health              # Health check de backend, Redis y PostgreSQL

# ── Consolas ──────────────────────────────────────────────────────
make shell-backend       # Shell bash dentro del contenedor backend
make shell-frontend      # Shell sh dentro del contenedor frontend
make db-shell            # Consola PostgreSQL (psql)
make redis-cli           # Consola Redis

# ── Base de datos ─────────────────────────────────────────────────
make db-backup                          # Exporta backup a ./backups/
make db-restore FILE=backups/arch.sql   # Restaura desde un backup
make flush-cache                        # Limpia toda la caché de Redis

# ── Limpieza ──────────────────────────────────────────────────────
make clean               # Detiene y elimina contenedores
make clean-all           # Elimina contenedores + imágenes + volúmenes
```

---

## API REST

La documentación completa está disponible en Swagger: **http://localhost:8000/docs**

### Endpoints principales

| Método | Ruta                              | Descripción                        |
|--------|-----------------------------------|------------------------------------|
| POST   | `/api/v1/auth/register`           | Registro de usuario                |
| POST   | `/api/v1/auth/login`              | Login → devuelve JWT               |
| POST   | `/api/v1/auth/google`             | Login con Google OAuth             |
| POST   | `/api/v1/auth/refresh`            | Refrescar access token             |
| GET    | `/api/v1/auth/me`                 | Perfil del usuario autenticado     |
| GET    | `/api/v1/products`                | Listado paginado con filtros       |
| GET    | `/api/v1/products/{id}`           | Detalle de producto                |
| GET    | `/api/v1/products/featured`       | Productos destacados               |
| GET    | `/api/v1/products/suggestions`    | Autocompletado de búsqueda         |
| GET    | `/api/v1/categories`              | Listado de categorías              |
| GET    | `/api/v1/brands`                  | Listado de marcas                  |
| POST   | `/api/v1/orders`                  | Crear pedido                       |
| GET    | `/api/v1/orders/my-orders`        | Pedidos del usuario autenticado    |
| POST   | `/api/v1/coupons/validate`        | Validar cupón de descuento         |
| GET    | `/api/v1/users/me/wishlist`       | Lista de deseos                    |
| GET    | `/api/v1/users/me/loyalty`        | Puntos de lealtad e historial      |
| POST   | `/api/v1/returns`                 | Crear solicitud de devolución      |
| GET    | `/api/v1/health`                  | Health check del sistema           |

### Autenticación

La API usa JWT Bearer tokens. Incluye el header en cada petición protegida:

```
Authorization: Bearer <tu-access-token>
```

---

## Estructura del proyecto

```
aroma-distribuido/
│
├── backend/                        # API FastAPI
│   ├── app/
│   │   ├── api/                    # Endpoints por recurso
│   │   │   ├── auth.py             # Registro, login, Google OAuth
│   │   │   ├── products.py         # CRUD productos + caché Redis
│   │   │   ├── orders.py           # Pedidos + loyalty points
│   │   │   ├── returns.py          # Devoluciones
│   │   │   ├── categories.py       # Categorías, marcas, cupones, reseñas
│   │   │   ├── wishlist.py         # Lista de deseos
│   │   │   ├── loyalty.py          # Puntos de lealtad
│   │   │   ├── payments.py         # Stripe
│   │   │   ├── upload.py           # Subida de imágenes
│   │   │   ├── reports.py          # Reportes + exportación Excel
│   │   │   ├── admin.py            # Endpoints exclusivos admin
│   │   │   ├── addresses.py        # Direcciones de envío
│   │   │   ├── contact.py          # Formulario de contacto
│   │   │   └── simulate.py         # Simulación de fallos
│   │   ├── core/
│   │   │   ├── config.py           # Settings con pydantic-settings
│   │   │   ├── database.py         # SQLAlchemy engine + session
│   │   │   ├── security.py         # JWT, hash de contraseñas
│   │   │   ├── dependencies.py     # get_current_user, get_current_admin
│   │   │   ├── redis_client.py     # Cliente Redis + helpers de caché
│   │   │   └── rabbitmq.py         # Cliente aio-pika + publicación eventos
│   │   ├── models/                 # Modelos SQLAlchemy (ORM)
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── order.py
│   │   │   ├── category.py
│   │   │   ├── returns.py
│   │   │   └── wishlist.py
│   │   ├── schemas/                # Schemas Pydantic (request/response)
│   │   ├── middleware/             # Request ID + logging estructurado
│   │   ├── utils/                  # Envío de emails
│   │   └── main.py                 # App FastAPI + CORS + routers
│   ├── alembic/                    # Migraciones de BD
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                       # SPA Vue 3
│   ├── src/
│   │   ├── pages/
│   │   │   ├── HomePage.vue
│   │   │   ├── ShopPage.vue        # Catálogo con filtros avanzados
│   │   │   ├── ProductPage.vue     # Detalle + perfil olfativo
│   │   │   ├── CartPage.vue
│   │   │   ├── CheckoutPage.vue
│   │   │   ├── OffersPage.vue      # Productos en oferta
│   │   │   ├── AccountPage.vue     # Mi cuenta completa
│   │   │   ├── LoginPage.vue
│   │   │   ├── RegisterPage.vue
│   │   │   └── admin/
│   │   │       ├── AdminDashboard.vue
│   │   │       ├── AdminProducts.vue
│   │   │       ├── AdminOrders.vue
│   │   │       ├── AdminReturns.vue
│   │   │       └── ...
│   │   ├── components/
│   │   │   ├── layout/             # Header, Footer, AdminSidebar
│   │   │   ├── ui/                 # ProductCard, SearchAutocomplete, etc.
│   │   │   └── auth/               # AuthModal global, OAuthButtons
│   │   ├── stores/                 # Estado global con Pinia
│   │   │   ├── auth.js             # Auth + modal global de login
│   │   │   ├── cart.js
│   │   │   ├── products.js
│   │   │   └── wishlist.js
│   │   ├── router/
│   │   │   ├── index.js            # Rutas + guards de autenticación
│   │   │   └── api.js              # Axios instance + interceptors JWT
│   │   ├── locales/                # Traducciones ES / EN
│   │   └── utils/                  # Helpers (currency, etc.)
│   ├── nginx.conf                  # Nginx con proxy al backend
│   ├── Dockerfile
│   └── .env.example
│
├── worker/
│   └── main.py                     # Consumer RabbitMQ (emails async)
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  # CI en cada push/PR a main
│       └── pages.yml               # Deploy GitHub Pages
│
├── docker-compose.yml              # Orquestación de 8 servicios
├── Makefile                        # Comandos de gestión del proyecto
└── README.md
```

---

## CI/CD

### `ci.yml` — Integración continua

Se ejecuta en cada push o pull request a `main`:
- Levanta los servicios necesarios con Docker Compose
- Ejecuta linting del backend
- Ejecuta pruebas de la API

### `pages.yml` — GitHub Pages

Publica documentación del proyecto automáticamente en GitHub Pages al hacer push a `main`.

---

## Créditos

Desarrollado por **Juan David Ríos** como proyecto de Programación Distribuida 2026.

- Backend: FastAPI + SQLAlchemy + Redis + RabbitMQ
- Frontend: Vue 3 + Pinia + Tailwind CSS
- Infraestructura: Docker Compose + Nginx
