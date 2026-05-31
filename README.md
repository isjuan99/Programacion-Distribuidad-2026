# Aroma-Distribuido — E-commerce de Perfumería de Lujo

Stack completo: **Vue 3** + **FastAPI** + **PostgreSQL**

---

## 🚀 Arranque rápido (Docker)

```bash
# Clonar y levantar todo el stack
git clone <repo> && cd aroma-distribuido
docker-compose up --build
```

| Servicio   | URL                        |
|------------|---------------------------|
| Tienda     | http://localhost           |
| Admin      | http://localhost/admin     |
| API docs   | http://localhost:8000/docs |
| DB         | localhost:5432             |

---

## 🛠️ Desarrollo local

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # editar variables
uvicorn app.main:app --reload
```

**Migraciones con Alembic:**
```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local    # VITE_API_URL=http://localhost:8000/api/v1
npm run dev
```

---

## 📁 Estructura

```
aroma-distribuido/
├── backend/
│   ├── app/
│   │   ├── api/          # Routers FastAPI
│   │   │   ├── auth.py
│   │   │   ├── products.py
│   │   │   ├── orders.py
│   │   │   ├── categories.py
│   │   │   ├── upload.py
│   │   │   ├── reports.py
│   │   │   └── admin.py  ← usuarios + reseñas globales
│   │   ├── core/         # Config, DB, Security, Deps
│   │   ├── models/       # SQLAlchemy ORM
│   │   ├── schemas/      # Pydantic
│   │   └── utils/        # Email
│   ├── alembic/          # Migraciones DB
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── HomePage.vue
    │   │   ├── ShopPage.vue
    │   │   ├── ProductPage.vue
    │   │   ├── CartPage.vue
    │   │   ├── CheckoutPage.vue
    │   │   ├── AccountPage.vue
    │   │   ├── LoginPage.vue
    │   │   ├── RegisterPage.vue
    │   │   ├── ForgotPasswordPage.vue
    │   │   └── admin/    # Panel completo
    │   ├── stores/       # Pinia: auth, cart, products, wishlist
    │   ├── components/   # Header, Footer, AdminSidebar, ProductCard
    │   ├── locales/      # i18n es.json + en.json
    │   └── router/       # Vue Router + Axios instance
    └── package.json
```

---

## 🔑 Variables de entorno clave

### Backend `.env`
| Variable | Descripción |
|---|---|
| `DATABASE_URL` | `postgresql://user:pass@host/db` |
| `SECRET_KEY` | JWT secret (usar `openssl rand -hex 32`) |
| `STRIPE_SECRET_KEY` | Clave Stripe para pagos |
| `SMTP_HOST/USER/PASSWORD` | Configuración de emails |

### Frontend `.env.local`
| Variable | Descripción |
|---|---|
| `VITE_API_URL` | URL base del API (ej: `http://localhost:8000/api/v1`) |

---

## 📦 Funcionalidades implementadas

- ✅ Catálogo con filtros (categoría, precio, tamaño, marca)
- ✅ Detalle de producto con variantes
- ✅ Carrito persistente (localStorage)
- ✅ Wishlist (localStorage)
- ✅ Checkout con cálculo de impuestos, cupones, envío
- ✅ Auth JWT (registro, login, refresh, forgot/reset password)
- ✅ Cuenta de usuario con historial de pedidos
- ✅ Panel admin completo (productos, órdenes, clientes, inventario, reseñas, reportes)
- ✅ Subida de imágenes (resize automático a 1200px)
- ✅ i18n ES/EN
- ✅ Docker Compose listo para producción

## ⚠️ Pendiente para producción

- [ ] Configurar Stripe webhooks para confirmar pagos
- [ ] OAuth Google/Apple (botones UI listos, lógica backend pendiente)
- [ ] Emails transaccionales (configurar SMTP/SendGrid)
- [ ] HTTPS / dominio propio
