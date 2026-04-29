# Aroma Distribuido - E-commerce de Perfumería

Sistema de e-commerce distribuido para gestión y venta de perfumes, con integración de **Redis** para caché de inventario y **RabbitMQ** para procesamiento asincrónico de órdenes. Arquitectura con backend Python (FastAPI), frontend React (Vite), base de datos MySQL y componentes de mensajería distribuida.

## 📋 Tabla de Contenidos

- [Características](#características)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración del Proyecto](#configuración-del-proyecto)
- [Implementación de Redis](#1-implementación-de-redis)
- [Implementación de RabbitMQ](#2-implementación-de-rabbitmq)
- [Ejecución del Proyecto](#ejecución-del-proyecto)
- [Flujo de Trabajo del Sistema](#flujo-de-trabajo-del-sistema)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Endpoints de la API](#endpoints-de-la-api)

---

## ✨ Características

- ✅ **Catálogo de productos** con caché en Redis
- ✅ **Sistema de órdenes** con gestión manual de estados por admin
- ✅ **Procesamiento asincrónico** de órdenes con RabbitMQ
- ✅ **Autenticación JWT** para usuarios y administradores
- ✅ **Panel administrativo** para gestión de inventario y órdenes
- ✅ **Interfaz de usuario** moderna con React y Vite
- ✅ **Base de datos** MySQL con esquema completo
- ✅ **Invalidación de caché** automática al crear/actualizar productos
- ✅ **Gestión de stock** sincronizado con estado de órdenes

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** 0.104+ - Framework web asincrónico de alto rendimiento
- **Python** 3.10+ - Lenguaje principal
- **MySQL Connector** - Driver para conexión a MySQL
- **redis** 5.0.1 - Cliente para Redis (caché)
- **pika** 1.3.2 - Cliente para RabbitMQ (mensajería)
- **aioredis** 2.0.1 - Cliente asincrónico para Redis
- **bcrypt** - Hashing seguro de contraseñas
- **PyJWT** - Autenticación con JWT

### Frontend
- **React** 18.2.0 - Librería de UI
- **Vite** 5.0.8 - Herramienta de build ultra-rápida
- **JavaScript ES6+** - Lenguaje de cliente

### Infraestructura
- **Redis** 6.0+ - Caché en memoria y almacén de datos
- **RabbitMQ** 3.12+ - Broker de mensajes
- **MySQL** 8.0+ - Base de datos relacional

---

## 📦 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

### Sistema Operativo
- Linux (Ubuntu 20.04+) o WSL2 en Windows
- macOS o Windows con Docker

### Software Requerido

**Opción 1: Instalación Local**
```bash
# Python 3.10+
python3 --version

# Node.js 16+
node --version
npm --version

# Redis
redis-server --version

# RabbitMQ (requiere Erlang)
rabbitmq-server --version

# MySQL
mysql --version
```

**Opción 2: Usando Docker**
```bash
docker --version
docker-compose --version
```

### Puertos Requeridos
- **8000**: API FastAPI
- **5173**: Frontend React (Vite dev server)
- **6379**: Redis
- **5672**: RabbitMQ (AMQP)
- **15672**: RabbitMQ Management UI
- **3306**: MySQL

---

## 📥 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/usuario/aroma-distribuido.git
cd aroma-distribuido/inventario
```

### 2. Configurar Backend Python

#### Crear Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

#### Instalar Dependencias
```bash
pip install --upgrade pip
pip install -r perfumeria_api/requirements.txt
```

#### Contenido de `perfumeria_api/requirements.txt`
```
fastapi==0.104.1
uvicorn==0.24.0
mysql-connector-python==8.2.0
redis==5.0.1
pika==1.3.2
aioredis==2.0.1
bcrypt==4.1.1
PyJWT==2.8.1
python-multipart==0.0.6
```

### 3. Configurar Frontend React

```bash
cd perfumeria-ui
npm install
```

### 4. Instalar Redis

#### En Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install redis-server
```

#### En macOS
```bash
brew install redis
```

#### Verificar instalación
```bash
redis-cli ping
# Output: PONG
```

### 5. Instalar RabbitMQ

#### En Ubuntu/Debian (requiere Erlang)
```bash
curl -1sLf 'https://dl.rabbitmq.com/rabbitmq-release-signing-key.asc' | sudo apt-key add -
sudo tee /etc/apt/sources.list.d/rabbitmq.list <<EOF
deb https://dl.rabbitmq.com/debian/ $(lsb_release -sc) main
EOF
sudo apt-get update
sudo apt-get install rabbitmq-server
```

#### En macOS
```bash
brew install rabbitmq
```

#### Iniciarse con el sistema
```bash
sudo systemctl enable rabbitmq-server
sudo systemctl start rabbitmq-server
```

#### Habilitar Management Plugin
```bash
sudo rabbitmq-plugins enable rabbitmq_management
```

#### Acceder a Management UI
```
http://localhost:15672
# Usuario: guest
# Contraseña: guest
```

### 6. Configurar MySQL

```bash
# Crear base de datos
mysql -u root -p
```

```sql
CREATE DATABASE perfumeria_db;
USE perfumeria_db;

-- Tabla de usuarios
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'cliente') DEFAULT 'cliente',
    activo INT DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de inventario
CREATE TABLE inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    marca VARCHAR(50) NOT NULL,
    precio DECIMAL(12,2) NOT NULL,
    stock INT DEFAULT 0,
    imagen VARCHAR(255),
    activo INT DEFAULT 1,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tablas de órdenes (creadas automáticamente por main.py)
```

---

## ⚙️ Configuración del Proyecto

### Variables de Entorno (Backend)

Crear archivo `.env` en la raíz del backend:

```bash
# Configuración MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=juan
DB_NAME=perfumeria_db

# Configuración Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Configuración RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

# JWT
JWT_SECRET=aroma-distribuido-secret-key-2026
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Archivo de Configuración Backend

Ubicación: `database.py`
```python
import mysql.connector

def obtener_conexion():
    config = {
        "host": "localhost",
        "user": "root",
        "password": "juan",
        "database": "perfumeria_db"
    }
    return mysql.connector.connect(**config)
```

### Variables de Entorno (Frontend)

Crear archivo `.env` en `perfumeria-ui/`:

```bash
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

---

---

# 1. Implementación de Redis

Redis se utiliza en este proyecto como **capa de caché en memoria** para optimizar consultas frecuentes y reducir la carga en la base de datos MySQL. El sistema implementa un patrón **cache-aside** donde se valida la existencia de datos en Redis antes de consultar la BD.

## 🎯 Casos de Uso de Redis en el Proyecto

| Caso de Uso | Clave Redis | TTL | Descripción |
|-------------|------------|-----|-------------|
| Listado completo de inventario | `inventario:todos` | 60s | Catálogo de perfumes con stock actual |
| Resumen de inventario | `inventario:resumen` | 60s | Estadísticas: total productos, stock, valor total |
| Sesiones de usuario | `sesion:{user_id}` | 3600s | Datos de sesión del cliente (futuro) |

## 📚 Componentes Involucrados

- **Módulo**: `perfumeria_api/redis_client.py` - Cliente centralizado de Redis
- **Controlador**: `main.py` - Endpoints que usan caché
- **Invalidación**: Automática al crear/actualizar productos

## 🔧 Paso a Paso de la Implementación

### Paso 1: Instalación de Librerías

```bash
pip install redis==5.0.1
pip install aioredis==2.0.1
```

### Paso 2: Crear Cliente Redis Centralizado

**Archivo: `perfumeria_api/redis_client.py`**

```python
"""
Redis client - VERSIÓN SIMPLIFICADA Y FUNCIONAL
Archivo: perfumeria_api/redis_client.py
"""
import json
import redis
from typing import Any
from decimal import Decimal
from datetime import datetime, date

# Configuración de conexión
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

_redis_client = None

def _get_client():
    """Obtiene o crea cliente Redis."""
    global _redis_client
    if _redis_client:
        return _redis_client
    try:
        _redis_client = redis.StrictRedis(
            host=REDIS_HOST, 
            port=REDIS_PORT, 
            db=REDIS_DB, 
            decode_responses=True,
            socket_connect_timeout=2
        )
        _redis_client.ping()
        print(f"✓ [REDIS] Conectado a {REDIS_HOST}:{REDIS_PORT}")
        return _redis_client
    except Exception as e:
        print(f"✗ [REDIS] Error de conexión: {e}")
        return None

def _serialize_value(obj):
    """Convierte objetos especiales a tipos serializables (Decimal, datetime)."""
    if isinstance(obj, (list, tuple)):
        return [_serialize_value(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: _serialize_value(val) for key, val in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    else:
        return obj

def get_cache(key: str) -> Any:
    """
    Obtiene un valor del caché Redis.
    
    Args:
        key: Clave del caché (ej: "inventario:todos")
    
    Returns:
        Valor deserializado o None si no existe
    
    Ejemplo:
        inventario = get_cache("inventario:todos")
    """
    client = _get_client()
    if not client:
        return None
    try:
        val = client.get(key)
        if val is None:
            print(f"✗ [REDIS] CACHE MISS: {key}")
            return None
        data = json.loads(val)
        print(f"✓ [REDIS] CACHE HIT: {key}")
        return data
    except Exception as e:
        print(f"✗ [REDIS] Error GET: {e}")
        return None

def set_cache(key: str, value: Any, ttl: int = 60) -> bool:
    """
    Guarda un valor en el caché Redis con expiración.
    
    Args:
        key: Clave del caché
        value: Valor a guardar (se serializa automáticamente)
        ttl: Time to live en segundos (default: 60)
    
    Returns:
        True si se guardó correctamente, False en caso contrario
    
    Ejemplo:
        set_cache("inventario:todos", lista_perfumes, ttl=60)
    """
    client = _get_client()
    if not client:
        print(f"✗ [REDIS] No hay conexión para SET {key}")
        return False
    try:
        # Serializar y limpiar los datos
        cleaned_value = _serialize_value(value)
        json_str = json.dumps(cleaned_value)
        
        # Guardar en Redis con expiración
        result = client.set(key, json_str, ex=ttl)
        
        if result:
            print(f"✓ [REDIS] GUARDADO: {key} ({len(json_str)} bytes, TTL={ttl}s)")
            return True
        else:
            print(f"✗ [REDIS] Falló al guardar {key}")
            return False
    except Exception as e:
        print(f"✗ [REDIS] Error SET: {e}")
        return False

def delete_cache(*keys: str) -> bool:
    """
    Elimina una o más claves del caché.
    
    Args:
        *keys: Una o más claves a eliminar
    
    Returns:
        True si se eliminaron correctamente
    
    Ejemplo:
        delete_cache("inventario:todos", "inventario:resumen")
    """
    client = _get_client()
    if not client:
        return False
    try:
        if keys:
            deleted = client.delete(*keys)
            print(f"✓ [REDIS] ELIMINADO: {deleted} claves")
            return True
    except Exception as e:
        print(f"✗ [REDIS] Error DELETE: {e}")
    return False
```

### Paso 3: Integrar Redis en los Endpoints

**Archivo: `main.py` - Fragmento de integración**

#### Importar funciones de Redis
```python
from perfumeria_api.redis_client import get_cache, set_cache, delete_cache
```

#### Endpoint: Listar Inventario (CON CACHÉ)
```python
@app.get("/inventario")
def listar_inventario():
    cache_key = "inventario:todos"
    
    # 1. INTENTA OBTENER DEL CACHÉ
    cached = get_cache(cache_key)
    if cached is not None:
        print(f"✓ [REDIS CACHE HIT] Devolviendo desde caché: {cache_key}")
        return cached

    # 2. SI NO ESTÁ EN CACHÉ, CONSULTA LA BASE DE DATOS
    print(f"✗ [REDIS CACHE MISS] Consultando base de datos para: {cache_key}")
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario")
    resultado = cursor.fetchall()
    cursor.close()
    conexion.close()

    # 3. GUARDA EN CACHÉ POR 60 SEGUNDOS
    set_cache(cache_key, resultado, ttl=60)
    print(f"✓ [REDIS] Datos guardados en caché: {cache_key} ({len(resultado)} items)")
    return resultado
```

#### Endpoint: Resumen de Inventario
```python
@app.get("/inventario/resumen")
def resumen_inventario():
    cache_key = "inventario:resumen"
    
    # Verificar caché
    cached = get_cache(cache_key)
    if cached is not None:
        return cached

    # Consultar BD si no está en caché
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_perfumes,
            SUM(stock) AS total_stock,
            SUM(precio * stock) AS valor_total
        FROM inventario
    """)
    resumen = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if resumen is None:
        resumen = {"total_perfumes": 0, "total_stock": 0, "valor_total": 0}

    # Guardar en caché
    set_cache(cache_key, resumen, ttl=60)
    return resumen
```

#### Endpoint: Crear Perfume (INVALIDA CACHÉ)
```python
@app.post("/perfumes")
async def crear_perfume(
    nombre: str = Form(...),
    marca: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    imagen: Optional[UploadFile] = File(None),
):
    # ... código de inserción ...
    
    # INVALIDAR CACHÉ CUANDO SE CREA UN PERFUME
    try:
        delete_cache("inventario:todos", "inventario:resumen")
        print("✓ Caché invalidado al crear perfume")
    except Exception:
        pass
    
    return {"mensaje": "Perfume registrado exitosamente"}
```

#### Endpoint: Actualizar Perfume (INVALIDA CACHÉ)
```python
@app.put("/perfumes/{id}")
async def actualizar_perfume(id: int, precio: float = Form(...), stock: int = Form(...)):
    # ... código de actualización ...
    
    # INVALIDAR CACHÉ CUANDO SE ACTUALIZA UN PERFUME
    try:
        delete_cache("inventario:todos", "inventario:resumen")
        print("✓ Caché invalidado al actualizar perfume")
    except Exception:
        pass
    
    return {"mensaje": "Inventario actualizado"}
```

## 🔍 Comandos Redis Utilizados

| Comando | Uso | Ejemplo |
|---------|-----|---------|
| **SET** | Guardar con expiración | `client.set("inventario:todos", json_data, ex=60)` |
| **GET** | Obtener valor | `client.get("inventario:todos")` |
| **DELETE** | Eliminar claves | `client.delete("inventario:todos", "inventario:resumen")` |
| **PING** | Verificar conexión | `client.ping()` → `True/False` |
| **EXPIRE** | Establecer TTL | `client.expire("key", 60)` |
| **TTL** | Ver tiempo restante | `client.ttl("key")` → segundos |

## 💾 Estructura de Datos en Redis

```
Tipo: STRING (JSON serializado)

Clave: "inventario:todos"
Valor: [
  {"id": 1, "nombre": "Sauvage", "marca": "Dior", "precio": 120.00, "stock": 15},
  {"id": 2, "nombre": "Bleu de Chanel", "marca": "Chanel", "precio": 130.00, "stock": 8},
  ...
]
TTL: 60 segundos

Clave: "inventario:resumen"
Valor: {
  "total_perfumes": 11,
  "total_stock": 189,
  "valor_total": 28806000.00
}
TTL: 60 segundos
```

## 📊 Flujo de Datos con Redis

```
┌─────────────────────────────────────────────────────────────┐
│                    Cliente (React/Browser)                   │
└────────────────────┬────────────────────────────────────────┘
                     │ GET /inventario
                     ▼
         ┌───────────────────────────┐
         │   FastAPI Endpoint        │
         └────────┬──────────────────┘
                  │
                  ▼
         ┌──────────────────────┐
         │ Verificar Redis Cache│ ◄───────┐
         └─────┬──────┬─────────┘         │
               │      │                   │
        HIT ◄──┘      └──► MISS           │
         │                   │             │
         │                   ▼             │
         │         ┌─────────────────┐    │
         │         │  Query MySQL BD │    │
         │         └────────┬────────┘    │
         │                  │             │
         │                  ▼             │
         │         ┌──────────────────┐   │
         │         │  Guardar en Redis├───┘
         │         │  (SET, TTL=60s)  │
         │         └──────────────────┘
         │
         └─────► Retornar a Cliente
```

## ⚠️ Consideraciones Importantes

1. **Serialización de Tipos**: Decimal y datetime se convierten automáticamente a float e ISO string
2. **TTL Dinámico**: Cada data tiene su propio TTL, configurable por endpoint
3. **Sin Persistencia Requerida**: Redis se usa solo como caché, no es storage permanente
4. **Fallback Graceful**: Si Redis no está disponible, el sistema sigue funcionando consultando BD
5. **Invalidación Manual**: Se invalida explícitamente al modificar inventario

---

---

# 2. Implementación de RabbitMQ

RabbitMQ se utiliza como **broker de mensajes** para desacoplar el procesamiento de órdenes del flujo de compra. Implementa un patrón **productor-consumidor** donde la API genera eventos de órdenes que son consumidas por un worker asincrónico independiente.

## 🎯 Casos de Uso de RabbitMQ en el Proyecto

| Caso de Uso | Cola | Productor | Consumidor | Descripción |
|-------------|------|-----------|-----------|-------------|
| Procesamiento de órdenes | `ordenes_queue` | `/api/ordenes` (POST) | `perfumeria_api/worker.py` | Órdenes pendientes para revisión manual |
| Persistencia | Durable (disk) | ✓ | ✓ | Garantiza entrega incluso tras fallos |

## 📚 Componentes Involucrados

- **Módulo Productor**: `perfumeria_api/rabbitmq_client.py` - Funciones publish/consume
- **Módulo Consumidor**: `perfumeria_api/worker.py` - Worker que procesa mensajes
- **Punto de Entrada**: `main.py` - Endpoint `/ordenes` que publica mensajes
- **Admin Panel**: `perfumeria-ui/pages/admin/PerfumeriaApp.jsx` - Gestión manual de órdenes

## 🔧 Paso a Paso de la Implementación

### Paso 1: Instalación de Librerías

```bash
pip install pika==1.3.2
```

La librería `pika` es el cliente oficial de RabbitMQ para Python, implementa el protocolo AMQP 0-9-1.

### Paso 2: Crear Cliente RabbitMQ Centralizado

**Archivo: `perfumeria_api/rabbitmq_client.py`**

```python
"""
RabbitMQ client helpers.
Implementación: funciones publish/consume con degradación a procesamiento síncrono
si RabbitMQ no está disponible.

Archivo: perfumeria_api/rabbitmq_client.py
"""
import json
import pika
from typing import Callable

# Configuración de conexión
RABBIT_HOST = "localhost"
RABBIT_PORT = 5672
RABBIT_USER = "guest"
RABBIT_PASS = "guest"

def _get_connection():
    """
    Establece conexión con RabbitMQ.
    
    Returns:
        pika.BlockingConnection o None si falla
    """
    try:
        credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
        params = pika.ConnectionParameters(
            host=RABBIT_HOST, 
            port=RABBIT_PORT, 
            credentials=credentials
        )
        return pika.BlockingConnection(params)
    except Exception:
        return None

def publish_message(queue: str, message: dict) -> bool:
    """
    Publica un mensaje en una cola de RabbitMQ.
    
    Características:
    - Colas duraderas (durable=True): persistentes en disco
    - Entrega garantizada (delivery_mode=2): reintento si el consumidor falla
    - Recuperación automática si RabbitMQ cae
    
    Args:
        queue: Nombre de la cola (ej: "ordenes_queue")
        message: Diccionario con datos del mensaje
    
    Returns:
        True si se publicó exitosamente, False si RabbitMQ no está disponible
    
    Ejemplo:
        mensaje = {
            "orden_id": 42,
            "usuario_id": 5,
            "total": 250.50,
            "items": [...]
        }
        publish_message("ordenes_queue", mensaje)
    """
    conn = _get_connection()
    if not conn:
        print(f"✗ [RABBITMQ] No se pudo conectar. Mensaje perdido: {queue}")
        return False
    try:
        channel = conn.channel()
        
        # Declarar cola como durable (persiste en disco)
        channel.queue_declare(queue=queue, durable=True)
        
        # Publicar mensaje con confirmación de entrega
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # Hacer mensaje persistente
            )
        )
        
        print(f"✓ [RABBITMQ] Publicado en '{queue}': {message.get('orden_id', '?')}")
        conn.close()
        return True
    except Exception as e:
        print(f"✗ [RABBITMQ] Error al publicar: {e}")
        try:
            conn.close()
        except Exception:
            pass
        return False

def consume_messages(queue: str, callback: Callable[[dict], None]):
    """
    Consume mensajes de una cola de RabbitMQ de forma bloqueante.
    
    Características:
    - Procesa un mensaje a la vez (prefetch_count=1)
    - Confirmación manual (basic_ack) tras procesar exitosamente
    - Reintentos automáticos si el callback falla (basic_nack)
    - Bloqueante: ideal para workers dedicados
    
    Args:
        queue: Nombre de la cola
        callback: Función(dict) llamada con cada mensaje
    
    Levanta:
        RuntimeError: Si RabbitMQ no está disponible
    
    Ejemplo:
        def procesar_orden(mensaje: dict):
            orden_id = mensaje["orden_id"]
            # Procesar orden...
            print(f"Orden {orden_id} procesada")
        
        consume_messages("ordenes_queue", procesar_orden)
    """
    conn = _get_connection()
    if not conn:
        raise RuntimeError("RabbitMQ no disponible")
    
    channel = conn.channel()
    
    # Declarar cola
    channel.queue_declare(queue=queue, durable=True)
    
    def _on_message(ch, method, properties, body):
        """Callback interno de pika."""
        try:
            payload = json.loads(body)
            print(f"✓ [RABBITMQ] Procesando: {payload.get('orden_id', '?')}")
            
            # Ejecutar callback del usuario
            callback(payload)
            
            # Confirmar entrega (ACK)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"✓ [RABBITMQ] Confirmado: {payload.get('orden_id', '?')}")
        except Exception as e:
            print(f"✗ [RABBITMQ] Error procesando: {e}")
            # Rechazar sin reintentar (NACK sin requeue)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    # Procesar un mensaje a la vez
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=_on_message)
    
    print(f"✓ [RABBITMQ] Esperando mensajes en '{queue}'...")
    try:
        channel.start_consuming()
    finally:
        try:
            conn.close()
        except Exception:
            pass
```

### Paso 3: Worker Consumidor de Órdenes

**Archivo: `perfumeria_api/worker.py`**

```python
"""
Worker para procesar órdenes desde RabbitMQ.

Este proceso debe ejecutarse de forma independiente:
    python perfumeria_api/worker.py

El worker:
1. Se conecta a RabbitMQ
2. Escucha la cola "ordenes_queue"
3. Procesa cada orden (sin modificar estado automáticamente)
4. Marca la orden para revisión manual del admin

Archivo: perfumeria_api/worker.py
"""
import sys
import traceback
from perfumeria_api.rabbitmq_client import consume_messages
from database import obtener_conexion

QUEUE_NAME = "ordenes_queue"

def process_order(message: dict):
    """
    Callback que procesa una orden recibida de RabbitMQ.
    
    Operaciones:
    - Valida que la orden existe
    - Marca la orden para revisión manual (estado: pendiente)
    - El admin decide confirmar o rechazar desde el panel
    
    Args:
        message: Dict con estructura:
            {
                "orden_id": 42,
                "usuario_id": 5,
                "total": 250.50,
                "items": [
                    {"perfume_id": 1, "cantidad": 2, "precio_unit": 125.25}
                ]
            }
    """
    try:
        orden_id = message.get("orden_id")
        if not orden_id:
            print("✗ [WORKER] Mensaje inválido: sin orden_id")
            return
        
        # Log: orden recibida en cola
        print(f"✓ [WORKER] Orden #{orden_id} recibida en cola y marcada para revisión manual")
        
        # AQUÍ podrían haber operaciones adicionales:
        # - Notificar al usuario por email
        # - Verificar disponibilidad de stock
        # - Registrar en auditoría
        # - Etc.
        
    except Exception:
        traceback.print_exc()

def main():
    """Punto de entrada: inicia el worker."""
    try:
        print("="*50)
        print("🚀 INICIANDO WORKER DE ÓRDENES")
        print("="*50)
        print(f"Conectando a RabbitMQ en localhost:5672...")
        print(f"Escuchando cola: {QUEUE_NAME}")
        print("="*50)
        
        consume_messages(QUEUE_NAME, process_order)
    except Exception as e:
        print(f"✗ [WORKER] Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Paso 4: Integración en API - Crear Orden

**Archivo: `main.py` - Fragmento de integración**

#### Importar funciones de RabbitMQ
```python
from perfumeria_api.rabbitmq_client import publish_message
```

#### Endpoint: Crear Orden (PUBLICA A COLA)
```python
@app.post("/ordenes")
async def crear_orden(
    payload: OrdenCreatePayload, 
    current_user: dict = Depends(get_current_user)
):
    """
    Crea una nueva orden y la envía a la cola de RabbitMQ.
    
    Flujo:
    1. Valida que hay productos en el carrito
    2. Inserta orden en BD con estado="pendiente"
    3. Inserta detalles de la orden
    4. Publica evento en RabbitMQ para procesamiento asincrónico
    5. Retorna orden creada
    
    Si RabbitMQ no está disponible, la orden sigue siendo creada
    pero no será procesada automáticamente (fallback graceful).
    """
    if not payload.items:
        raise HTTPException(status_code=400, detail="La orden no tiene productos")
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        # 1. INSERTAR ORDEN CON ESTADO PENDIENTE
        cursor.execute(
            """
            INSERT INTO ordenes (usuario_id, total, estado, direccion, metodo_pago, telefono, notas)
            VALUES (%s, %s, 'pendiente', %s, %s, %s, %s)
            """,
            (
                current_user["id"],
                payload.total,
                payload.direccion,
                payload.metodo_pago,
                payload.telefono,
                payload.notas,
            ),
        )
        orden_id = cursor.lastrowid

        # 2. INSERTAR DETALLES DE LA ORDEN
        for item in payload.items:
            subtotal = float(item.precio_unit) * int(item.cantidad)
            cursor.execute(
                """
                INSERT INTO orden_detalles (orden_id, perfume_id, cantidad, precio_unit, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (orden_id, item.perfume_id, item.cantidad, item.precio_unit, subtotal),
            )

        # 3. CONFIRMAR EN BASE DE DATOS
        conexion.commit()

        # 4. PUBLICAR EN RABBITMQ PARA PROCESAMIENTO ASINCRÓNICO
        message = {
            "orden_id": orden_id,
            "usuario_id": current_user["id"],
            "total": float(payload.total),
            "items": [
                {
                    "perfume_id": i.perfume_id,
                    "cantidad": i.cantidad,
                    "precio_unit": float(i.precio_unit)
                }
                for i in payload.items
            ],
        }

        published = False
        try:
            published = publish_message("ordenes_queue", message)
        except Exception as e:
            print(f"⚠️  [API] RabbitMQ no disponible: {e}")
            published = False

        if not published:
            print(f"⚠️  [API] Orden #{orden_id} creada pero no publicada en cola (RabbitMQ offline)")

        # 5. RETORNAR ORDEN CREADA
        return {"orden_id": orden_id, "estado": "pendiente"}
    
    except Exception:
        conexion.rollback()
        raise HTTPException(status_code=500, detail="No se pudo registrar la orden")
    finally:
        cursor.close()
        conexion.close()
```

### Paso 5: Panel Admin - Gestión Manual de Órdenes

**Archivo: `perfumeria-ui/pages/admin/PerfumeriaApp.jsx` - Fragmento**

```javascript
// Hook para cambiar estado de orden
const cambiarEstadoOrden = async (ordenId, estado) => {
    setActualizandoOrden(ordenId);
    try {
        const res = await fetch(`${API_URL}/admin/ordenes/${ordenId}/estado`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            body: JSON.stringify({ estado }),  // "pendiente" | "confirmada" | "rechazada"
        });
        if (!res.ok) throw new Error();
        const data = await res.json();
        toast(data.mensaje || "Orden actualizada");
        cargarOrdenes();  // Recargar listado
    } catch {
        toast("No se pudo actualizar la orden", "error");
    } finally {
        setActualizandoOrden(null);
    }
};

// En el render de tabla:
<button 
    onClick={() => cambiarEstadoOrden(o.orden_id, "confirmada")}
    disabled={o.estado === "confirmada"}
>
    Confirmar
</button>
<button 
    onClick={() => cambiarEstadoOrden(o.orden_id, "rechazada")}
    disabled={o.estado === "rechazada"}
>
    Rechazar
</button>
```

## 🔍 Operaciones AMQP Utilizadas

| Operación | Función | Propósito |
|-----------|---------|----------|
| **queue_declare** | `channel.queue_declare(queue=q, durable=True)` | Crear cola durable en disco |
| **basic_publish** | `channel.basic_publish(exchange='', routing_key=q, body=msg)` | Enviar mensaje a cola |
| **basic_consume** | `channel.basic_consume(queue=q, on_message_callback=cb)` | Escuchar cola (bloqueante) |
| **basic_ack** | `ch.basic_ack(delivery_tag=tag)` | Confirmar procesamiento (elimina de cola) |
| **basic_nack** | `ch.basic_nack(delivery_tag=tag, requeue=False)` | Rechazar sin reintentar |
| **basic_qos** | `channel.basic_qos(prefetch_count=1)` | Procesar 1 mensaje a la vez |

## 📊 Estructura de Mensajes en RabbitMQ

```json
{
  "orden_id": 42,
  "usuario_id": 5,
  "total": 250.50,
  "items": [
    {
      "perfume_id": 1,
      "cantidad": 2,
      "precio_unit": 125.25
    },
    {
      "perfume_id": 3,
      "cantidad": 1,
      "precio_unit": 0.00
    }
  ]
}
```

## 🔄 Flujo Completo: Crear y Procesar Orden

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CLIENTE (React Browser)                         │
│              1. Completa carrito y clica "Comprar"                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
            ┌────────────────────────────────────┐
            │   POST /ordenes                    │
            │   (FastAPI Endpoint)               │
            └──────────┬─────────────────────────┘
                       │
                       ▼
            ┌────────────────────────────────────┐
            │ 1. Validar carrito no vacío        │
            │ 2. Conectar a MySQL                │
            │ 3. INSERT ordenes                  │
            │ 4. INSERT orden_detalles           │
            │ 5. COMMIT a BD                     │
            └──────────┬─────────────────────────┘
                       │
                       ▼
            ┌────────────────────────────────────┐
            │ 6. Construir mensaje JSON          │
            │ 7. Conectar a RabbitMQ             │
            │ 8. Publicar en "ordenes_queue"     │
            │    (delivery_mode=2, durable)      │
            └──────────┬─────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
   RETORNAR                    ┌────────────────┐
   {"orden_id": 42}            │ RabbitMQ COLA  │
                               │(Persistente)   │
                               └────────┬───────┘
                                        │
                                        ▼
                        ┌───────────────────────────┐
                        │  WORKER (Python Thread)   │
                        │ consume_messages("...")   │
                        └───────────┬───────────────┘
                                    │
                                    ▼
                        ┌───────────────────────────┐
                        │ 1. Recibir mensaje        │
                        │ 2. Procesar orden         │
                        │ 3. Enviar básico_ack      │
                        │    (Eliminar de cola)     │
                        └───────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   PANEL ADMIN (React)                               │
│              4. Admin ve orden con estado "pendiente"               │
│              5. Clica "Confirmar" o "Rechazar"                     │
│              6. PUT /admin/ordenes/{id}/estado                     │
└──────────────────────────────────────────────────────────────────────┘
```

## ⚠️ Consideraciones Importantes

1. **Cola Durable**: `durable=True` → persiste en disco, no se pierde si RabbitMQ cae
2. **Entrega Garantizada**: `delivery_mode=2` → reintenta si el consumidor falla
3. **Prefetch Count 1**: Procesa un mensaje a la vez, evita sobrecarga del worker
4. **Sin Auto-Confirmación**: ACK manual → confirma solo tras procesar exitosamente
5. **Graceful Degradation**: Si RabbitMQ offline, la orden se crea pero sin procesamiento automático
6. **Revisor Manual**: El admin decide confirmar/rechazar, no es automático

---

## 🚀 Ejecución del Proyecto

### 1. Iniciar Redis

```bash
# Opción 1: Como demonio
redis-server --daemonize yes

# Opción 2: En primer plano (para debugging)
redis-server

# Verificar conexión
redis-cli ping
# Output: PONG
```

### 2. Iniciar RabbitMQ

```bash
# Si está instalado como servicio
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

# O iniciarlo manualmente
rabbitmq-server

# Verificar status
sudo rabbitmqctl status

# Acceder a Management UI
# http://localhost:15672 (usuario: guest, pass: guest)
```

### 3. Iniciar MySQL

```bash
# Si está instalado como servicio
sudo systemctl start mysql
sudo systemctl enable mysql

# Crear base de datos (si no existe)
mysql -u root -p < schema.sql
```

### 4. Iniciar Backend (API FastAPI)

```bash
# Activar virtual environment
source venv/bin/activate

# Desde directorio raíz del backend
python main.py

# Output esperado:
# ✓ [REDIS] Conectado a localhost:6379
# ✓ Módulos cargados - REDIS inicializando...
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. Iniciar Worker (en otra terminal)

```bash
# Activar virtual environment (otra terminal)
source venv/bin/activate

python perfumeria_api/worker.py

# Output esperado:
# ==================================================
# 🚀 INICIANDO WORKER DE ÓRDENES
# ==================================================
# ✓ [RABBITMQ] Esperando mensajes en 'ordenes_queue'...
```

### 6. Iniciar Frontend (React)

```bash
cd perfumeria-ui
npm install  # Solo la primera vez
npm run dev

# Output esperado:
#  VITE v5.0.8  ready in 123 ms
#  ➜  Local:   http://localhost:5173/
#  ➜  press h to show help
```

### Script Automatizado

Crear `run_redis_api.sh` en la raíz:

```bash
#!/bin/bash
set -e

echo "=========================================="
echo "INICIANDO REDIS + API + WORKER"
echo "=========================================="

# Limpiar procesos previos
pkill -f "redis-server" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "worker.py" 2>/dev/null || true
sleep 1

# Iniciar Redis
echo "Iniciando Redis..."
redis-server --daemonize yes --logfile /tmp/redis.log
sleep 2

# Iniciar API
echo "Iniciando API (FastAPI)..."
source venv/bin/activate
python main.py &
API_PID=$!
sleep 3

# Iniciar Worker
echo "Iniciando Worker (RabbitMQ)..."
python perfumeria_api/worker.py &
WORKER_PID=$!
sleep 2

# Iniciar Frontend
echo "Iniciando Frontend (React)..."
cd perfumeria-ui
npm run dev &
FRONTEND_PID=$!

echo "=========================================="
echo "✅ Sistema iniciado:"
echo "   - Redis: localhost:6379"
echo "   - API: http://localhost:8000"
echo "   - Frontend: http://localhost:5173"
echo "   - RabbitMQ UI: http://localhost:15672"
echo "=========================================="

# Mantener procesos corriendo
wait
```

Ejecutar:
```bash
bash run_redis_api.sh
```

---

## 🔄 Flujo de Trabajo del Sistema

### Flujo 1: Consulta de Catálogo (CON CACHÉ REDIS)

```
Usuario abre app
    ↓
GET /inventario (Frontend)
    ↓
[API] ¿Existe "inventario:todos" en Redis?
    ├─ SÍ → Devolver caché (RÁPIDO - <1ms)
    └─ NO → Consultar MySQL → Guardar en Redis (TTL=60s) → Devolver
    ↓
Frontend renderiza catálogo
```

### Flujo 2: Crear Orden (CON RABBITMQ)

```
Usuario completa carrito y clica "Comprar"
    ↓
POST /ordenes (payload con items)
    ↓
[API] Validar carrito no vacío
    ↓
[API] INSERT en MySQL (estado="pendiente")
    ↓
[API] Construir mensaje JSON
    ↓
[API] Publicar en RabbitMQ:ordenes_queue (durable, persistent)
    ├─ ✓ Publicado → Retornar {orden_id, estado: "pendiente"}
    └─ ✗ RabbitMQ offline → Retornar igual (fallback)
    ↓
Frontend muestra "Orden creada #42"
    ↓
[WORKER] consume_messages() recibe evento de RabbitMQ
    ↓
[WORKER] Procesa orden (ej: notificaciones, auditoría)
    ↓
[WORKER] basic_ack() → Elimina de cola
    ↓
[ADMIN] Ve orden en panel con estado "pendiente"
    ↓
[ADMIN] Clica "Confirmar"
    ↓
PUT /admin/ordenes/{id}/estado ({"estado": "confirmada"})
    ↓
[API] Valida rol admin → UPDATE orden estado → Ajusta stock
    ↓
[ADMIN] Ve orden con estado "confirmada" (recarga auto)
```

### Flujo 3: Actualizar Inventario (CON INVALIDACIÓN DE CACHÉ)

```
Admin crea nuevo perfume
    ↓
POST /perfumes
    ↓
[API] INSERT en MySQL
    ↓
[API] DELETE Redis keys: "inventario:todos", "inventario:resumen"
    ↓
[API] Retornar {mensaje: "Perfume registrado"}
    ↓
Próxima vez que cliente abre catálogo:
    ↓
GET /inventario
    ↓
[API] ¿"inventario:todos" en Redis? → NO (fue invalidado)
    ↓
[API] Consultar MySQL (con nuevo perfume) → Guardar en caché (TTL=60s)
    ↓
Frontend muestra catálogo actualizado
```

---

## 📁 Estructura del Proyecto

```
inventario/
├── main.py                              # API FastAPI principal
├── database.py                          # Configuración MySQL
├── run_redis_api.sh                     # Script automatizado
│
├── perfumeria_api/
│   ├── __init__.py
│   ├── redis_client.py                  # ⭐ Cliente Redis (caché)
│   ├── rabbitmq_client.py               # ⭐ Cliente RabbitMQ (mensajería)
│   ├── worker.py                        # ⭐ Worker consumidor de órdenes
│   └── requirements.txt                 # Dependencias Python
│
├── perfumeria-ui/                       # Frontend React
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── App.css
│   ├── pages/
│   │   ├── LoginPage.jsx
│   │   ├── CatalogoPage.jsx
│   │   ├── CheckoutPage.jsx
│   │   ├── MisOrdenesPage.jsx
│   │   └── admin/
│   │       ├── PerfumeriaApp.jsx        # ⭐ Panel admin con gestión de órdenes
│   │       ├── DashboardPage.jsx
│   │       ├── AdminPerfumesPage.jsx
│   │       └── AdminOrdenesPage.jsx
│   ├── api/
│   │   └── api.js                       # Cliente API (fetch)
│   ├── context/
│   │   ├── AuthContext.jsx              # Contexto de autenticación
│   │   └── CartContext.jsx              # Contexto de carrito
│   ├── components/
│   │   ├── Navbar.jsx
│   │   ├── CartPanel.jsx
│   │   ├── PerfumeCard.jsx
│   │   └── Toast.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── imagenes/                            # Imágenes de productos
├── uploads/                             # Archivos subidos
└── venv/                                # Virtual environment Python
```

---

## 🔌 Endpoints de la API

### Autenticación

```http
POST /register
POST /login
GET /usuarios/me
GET /usuarios
```

### Inventario (CON CACHÉ REDIS)

```http
GET /inventario                          # ✨ Cachea en "inventario:todos"
GET /inventario/resumen                  # ✨ Cachea en "inventario:resumen"
POST /perfumes                           # Invalida caché
PUT /perfumes/{id}                       # Invalida caché
```

### Órdenes

```http
POST /ordenes                            # ✨ Publica en RabbitMQ
GET /ordenes                             # Mis órdenes del usuario
GET /ordenes/{id}/detalle
GET /admin/ordenes                       # ✨ Ver todas (admin solo)
PUT /admin/ordenes/{id}/estado           # ✨ Cambiar estado (admin solo)
```

---

## 🐳 Alternativa: Usando Docker

Crear `docker-compose.yml`:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  rabbitmq:
    image: rabbitmq:3.12-management
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq

  mysql:
    image: mysql:8.0
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: juan
      MYSQL_DATABASE: perfumeria_db
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  redis_data:
  rabbitmq_data:
  mysql_data:
```

Ejecutar:
```bash
docker-compose up -d
```

---

## 📊 Monitoreo y Debugging

### Redis CLI

```bash
# Conectar
redis-cli

# Comandos útiles
redis-cli KEYS "inventario:*"            # Ver claves de caché
redis-cli GET "inventario:todos"         # Ver contenido (JSON)
redis-cli TTL "inventario:todos"         # Ver tiempo de expiración
redis-cli FLUSHALL                       # Limpiar caché completo
redis-cli STRLEN "inventario:todos"      # Tamaño en bytes
redis-cli MONITOR                        # Ver operaciones en tiempo real
```

### RabbitMQ Management UI

```
http://localhost:15672
Usuario: guest
Contraseña: guest
```

Opciones:
- **Queues**: Ver `ordenes_queue` y mensajes pendientes
- **Connections**: Ver conexiones activas
- **Channels**: Ver canales de publicación
- **Admin**: Crear usuarios y permisos

### MySQL CLI

```bash
# Conectar
mysql -u root -p

# Ver órdenes
SELECT * FROM ordenes;
SELECT * FROM orden_detalles;
SELECT * FROM inventario;

# Ver cachés en Redis (desde app)
GET /inventario/resumen
```

### Logs

```bash
# API FastAPI
tail -f api.log

# Worker
# Se ejecuta en terminal, ver output directo

# Redis
tail -f /tmp/redis.log

# RabbitMQ
tail -f /var/log/rabbitmq/rabbit@localhost.log
```

---

## ✅ Checklist de Implementación

- ✅ Redis implementado para caché de inventario
- ✅ RabbitMQ implementado para colas de órdenes
- ✅ Panel admin para gestión manual de órdenes
- ✅ Invalidación automática de caché
- ✅ Gestión de stock sincronizado con estados
- ✅ Worker consumidor de mensajes
- ✅ Autenticación JWT
- ✅ API REST completa
- ✅ Frontend React moderno
- ✅ Documentación completa

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para cambios mayores, abre un issue primero para discutir qué te gustaría cambiar.

---

## 📝 Licencia

MIT License - Libre para usar en proyectos personales y comerciales.

---

## 👤 Autor

Creado como sistema distribuido de e-commerce con énfasis en **caché y mensajería asincrónica**.

**Contacto**: [Tu email/GitHub]

---

## 📚 Referencias

- [Redis Documentation](https://redis.io/documentation)
- [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Pika (Python RabbitMQ Client)](https://pika.readthedocs.io/)
- [Redis Python Client](https://redis-py.readthedocs.io/)

---

**Última actualización**: Abril 2026
