from fastapi import FastAPI, HTTPException
import asyncio
from database import obtener_conexion
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timedelta
import bcrypt
import jwt
import os
import shutil
import uuid
from mysql.connector import Error as MySQLError
from perfumeria_api.redis_client import get_cache, set_cache, delete_cache

print("\n" + "="*60)
print("✓ MÓDULOS CARGADOS - REDIS INICIALIZANDO...")
print("="*60 + "\n")

# ✅ PRIMERO crear la app, LUEGO agregar middleware
app = FastAPI(title="E-commerce Perfumería")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "perfumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=os.path.join(BASE_DIR, "uploads")), name="uploads")


# Configuración JWT
SECRET_KEY = "aroma-distribuido-secret-key-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ==================== MODELOS PYDANTIC ====================

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    rol: str

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class PerfumeCreate(BaseModel):
    nombre: str
    marca: str
    precio: float
    stock: int
    descripcion: Optional[str] = None

class PerfumeUpdate(BaseModel):
    precio: Optional[float] = None
    stock: Optional[int] = None
    descripcion: Optional[str] = None

class PerfumeResponse(BaseModel):
    id: int
    nombre: str
    marca: str
    precio: float
    stock: int
    descripcion: Optional[str] = None
    activo: int


def ensure_image_column() -> bool:
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM inventario LIKE 'imagen'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE inventario ADD COLUMN imagen VARCHAR(255) NULL")
            conexion.commit()
        return True
    except MySQLError:
        return False
    finally:
        cursor.close()
        conexion.close()


ensure_image_column()

class CarritoItem(BaseModel):
    perfume_id: int
    cantidad: int

class OrdenCreate(BaseModel):
    direccion: Optional[str] = None
    metodo_pago: Optional[str] = None

class OrdenItemCreate(BaseModel):
    perfume_id: int
    cantidad: int
    precio_unit: float

class OrdenCreatePayload(BaseModel):
    items: List[OrdenItemCreate]
    total: float
    direccion: Optional[str] = None
    metodo_pago: Optional[str] = None
    telefono: Optional[str] = None
    notas: Optional[str] = None

class OrdenResponse(BaseModel):
    id: int
    usuario_id: int
    total: float
    estado: str
    creado_en: datetime


class OrdenEstadoUpdate(BaseModel):
    estado: str

class OrdenDetalleResponse(BaseModel):
    orden_id: int
    item_id: int
    perfume_nombre: str
    perfume_marca: str
    cantidad: int
    precio_unit: float
    subtotal: float
    orden_estado: str
    orden_fecha: datetime
    cliente_nombre: str


def ensure_orders_tables():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordenes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                total DECIMAL(12,2) NOT NULL DEFAULT 0,
                estado VARCHAR(30) NOT NULL DEFAULT 'confirmada',
                direccion VARCHAR(255) NULL,
                metodo_pago VARCHAR(80) NULL,
                telefono VARCHAR(30) NULL,
                notas TEXT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orden_detalles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                orden_id INT NOT NULL,
                perfume_id INT NOT NULL,
                cantidad INT NOT NULL,
                precio_unit DECIMAL(12,2) NOT NULL,
                subtotal DECIMAL(12,2) NOT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Si las tablas ya existian, aseguramos columnas nuevas necesarias.
        cursor.execute("SHOW COLUMNS FROM ordenes LIKE 'direccion'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE ordenes ADD COLUMN direccion VARCHAR(255) NULL")

        cursor.execute("SHOW COLUMNS FROM ordenes LIKE 'metodo_pago'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE ordenes ADD COLUMN metodo_pago VARCHAR(80) NULL")

        cursor.execute("SHOW COLUMNS FROM ordenes LIKE 'telefono'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE ordenes ADD COLUMN telefono VARCHAR(30) NULL")

        cursor.execute("SHOW COLUMNS FROM ordenes LIKE 'notas'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE ordenes ADD COLUMN notas TEXT NULL")

        cursor.execute("SHOW COLUMNS FROM ordenes LIKE 'creado_en'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE ordenes ADD COLUMN creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        cursor.execute("SHOW COLUMNS FROM orden_detalles LIKE 'subtotal'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE orden_detalles ADD COLUMN subtotal DECIMAL(12,2) NOT NULL DEFAULT 0")

        cursor.execute("SHOW COLUMNS FROM orden_detalles LIKE 'creado_en'")
        if cursor.fetchone() is None:
            cursor.execute("ALTER TABLE orden_detalles ADD COLUMN creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()


ensure_orders_tables()

ESTADOS_ORDEN = {"pendiente", "confirmada", "rechazada"}

# ==================== FUNCIONES AUXILIARES ====================

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def ajustar_stock_orden(cursor, orden_id: int, delta: int):
    cursor.execute(
        """
        SELECT perfume_id, cantidad
        FROM orden_detalles
        WHERE orden_id = %s
        """,
        (orden_id,),
    )
    detalles = cursor.fetchall()
    for detalle in detalles:
        cursor.execute(
            "UPDATE inventario SET stock = GREATEST(stock + %s, 0) WHERE id = %s",
            (delta * int(detalle["cantidad"]), int(detalle["perfume_id"])),
        )

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, email, rol FROM usuarios WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if user is None:
        raise credentials_exception
    return user
# ==================== ENDPOINTS DE USUARIOS ====================

@app.post("/register", response_model=UsuarioResponse)
async def register(usuario: UsuarioCreate):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # Verificar si el usuario ya existe
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (usuario.email,))
    if cursor.fetchone():
        cursor.close()
        conexion.close()
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Crear usuario
    hashed_password = hash_password(usuario.password)
    query = "INSERT INTO usuarios (nombre, email, password, rol) VALUES (%s, %s, %s, 'cliente')"
    cursor.execute(query, (usuario.nombre, usuario.email, hashed_password))
    conexion.commit()
    user_id = cursor.lastrowid
    
    cursor.close()
    conexion.close()
    
    return UsuarioResponse(id=user_id, nombre=usuario.nombre, email=usuario.email, rol="cliente")

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM usuarios WHERE email = %s AND activo = 1", (form_data.username,))
    user = cursor.fetchone()
    cursor.close()
    conexion.close()
    
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["email"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": user["id"],
            "nombre": user["nombre"],
            "email": user["email"],
            "rol": user["rol"]
        }
    }

@app.get("/usuarios/me", response_model=UsuarioResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UsuarioResponse(
        id=current_user["id"],
        nombre=current_user["nombre"],
        email=current_user["email"],
        rol=current_user["rol"]
    )

@app.get("/usuarios", response_model=List[UsuarioResponse])
async def listar_usuarios(current_user: dict = Depends(get_current_user)):
    # Solo admin puede listar usuarios
    if current_user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, email, rol FROM usuarios")
    usuarios = cursor.fetchall()
    cursor.close()
    conexion.close()
    return usuarios





# 1. LISTAR INVENTARIO
@app.get("/inventario")
def listar_inventario():
    cache_key = "inventario:todos"
    
    # Intentar obtener desde Redis
    cached = get_cache(cache_key)
    if cached is not None:
        print(f"✓ [REDIS CACHE HIT] Devolviendo desde caché: {cache_key}")
        return cached

    # Si no está en cache, consultar BD
    print(f"✗ [REDIS CACHE MISS] Consultando base de datos para: {cache_key}")
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM inventario")
    resultado = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Guardar en cache por 60 segundos
    set_cache(cache_key, resultado, ttl=60)
    print(f"✓ [REDIS] Datos guardados en caché: {cache_key} ({len(resultado)} items)")
    return resultado


@app.get("/inventario/resumen")
def resumen_inventario():
    # Nuevo endpoint: devuelve resumen y lo cachea en Redis (clave: inventario:resumen)
    # Archivo creado/modificado: main.py
    cache_key = "inventario:resumen"
    cached = get_cache(cache_key)
    if cached is not None:
        return cached

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total_perfumes, SUM(stock) AS total_stock, SUM(precio * stock) AS valor_total FROM inventario")
    resumen = cursor.fetchone()
    cursor.close()
    conexion.close()
    if resumen is None:
        resumen = {"total_perfumes": 0, "total_stock": 0, "valor_total": 0}

    set_cache(cache_key, resumen, ttl=60)
    return resumen

# 2. CREAR PERFUME
@app.post("/perfumes")
async def crear_perfume(
    nombre: str = Form(...),
    marca: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    imagen: Optional[UploadFile] = File(None),
):
    await asyncio.sleep(0)
    image_path = None
    if imagen and imagen.filename:
        _, ext = os.path.splitext(imagen.filename.lower())
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            raise HTTPException(status_code=400, detail="Formato de imagen no permitido")
        filename = f"{uuid.uuid4().hex}{ext}"
        destination = os.path.join(UPLOAD_DIR, filename)
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        image_path = f"/uploads/perfumes/{filename}"

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    query_with_image = "INSERT INTO inventario (nombre, marca, precio, stock, imagen) VALUES (%s, %s, %s, %s, %s)"
    query_without_image = "INSERT INTO inventario (nombre, marca, precio, stock) VALUES (%s, %s, %s, %s)"
    if image_path:
        try:
            cursor.execute(query_with_image, (nombre, marca, precio, stock, image_path))
        except MySQLError as err:
            # Si la columna no existe en runtime, intentamos crearla y reintentar.
            if getattr(err, "errno", None) == 1054 and ensure_image_column():
                cursor.execute(query_with_image, (nombre, marca, precio, stock, image_path))
            else:
                cursor.close()
                conexion.close()
                raise HTTPException(status_code=500, detail="No se pudo guardar la imagen del perfume")
    else:
        cursor.execute(query_without_image, (nombre, marca, precio, stock))
    conexion.commit()
    cursor.close()
    conexion.close()
    # Invalida caches de inventario al crear perfume
    # Archivo modificado: main.py
    try:
        delete_cache("inventario:todos", "inventario:resumen")
    except Exception:
        pass
    return {"mensaje": "Perfume registrado exitosamente", "imagen": image_path}

# 3. ACTUALIZAR STOCK
@app.put("/perfumes/{id}")
async def actualizar_perfume(
    id: int,
    precio: float = Form(...),
    stock: int = Form(...),
    imagen: Optional[UploadFile] = File(None),
):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    image_path = None
    if imagen and imagen.filename:
        _, ext = os.path.splitext(imagen.filename.lower())
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
            raise HTTPException(status_code=400, detail="Formato de imagen no permitido")
        filename = f"{uuid.uuid4().hex}{ext}"
        destination = os.path.join(UPLOAD_DIR, filename)
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)
        image_path = f"/uploads/perfumes/{filename}"

    if image_path:
        try:
            query = "UPDATE inventario SET precio=%s, stock=%s, imagen=%s WHERE id=%s"
            cursor.execute(query, (precio, stock, image_path, id))
        except MySQLError as err:
            if getattr(err, "errno", None) == 1054 and ensure_image_column():
                query = "UPDATE inventario SET precio=%s, stock=%s, imagen=%s WHERE id=%s"
                cursor.execute(query, (precio, stock, image_path, id))
            else:
                cursor.close()
                conexion.close()
                raise HTTPException(status_code=500, detail="No se pudo actualizar la imagen")
    else:
        query = "UPDATE inventario SET precio=%s, stock=%s WHERE id=%s"
        cursor.execute(query, (precio, stock, id))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    cursor.close()
    conexion.close()
    if filas_afectadas == 0:
        raise HTTPException(status_code=404, detail="Perfume no encontrado")
    # Invalida caches al actualizar perfume
    # Archivo modificado: main.py
    try:
        delete_cache("inventario:todos", "inventario:resumen")
    except Exception:
        pass
    return {"mensaje": "Inventario actualizado"}


@app.post("/ordenes")
async def crear_orden(payload: OrdenCreatePayload, current_user: dict = Depends(get_current_user)):
    if not payload.items:
        raise HTTPException(status_code=400, detail="La orden no tiene productos")
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
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

        for item in payload.items:
            subtotal = float(item.precio_unit) * int(item.cantidad)
            cursor.execute(
                """
                INSERT INTO orden_detalles (orden_id, perfume_id, cantidad, precio_unit, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (orden_id, item.perfume_id, item.cantidad, item.precio_unit, subtotal),
            )

        # Commit initial pending order and details
        conexion.commit()
        return {"orden_id": orden_id, "estado": "pendiente"}
    except Exception:
        conexion.rollback()
        raise HTTPException(status_code=500, detail="No se pudo registrar la orden")
    finally:
        cursor.close()
        conexion.close()


@app.get("/ordenes")
async def listar_mis_ordenes(current_user: dict = Depends(get_current_user)):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                id AS orden_id,
                total,
                estado,
                creado_en
            FROM ordenes
            WHERE usuario_id = %s
            ORDER BY id DESC
            """,
            (current_user["id"],),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


@app.get("/admin/ordenes")
async def listar_ordenes_admin(current_user: dict = Depends(get_current_user)):
    if current_user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT
                o.id AS orden_id,
                o.usuario_id,
                u.nombre AS usuario_nombre,
                u.email AS usuario_email,
                o.total,
                o.estado,
                o.creado_en
            FROM ordenes o
            LEFT JOIN usuarios u ON u.id = o.usuario_id
            ORDER BY o.id DESC
            """
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conexion.close()


@app.put("/admin/ordenes/{orden_id}/estado")
async def actualizar_estado_orden(
    orden_id: int,
    payload: OrdenEstadoUpdate,
    current_user: dict = Depends(get_current_user),
):
    if current_user["rol"] != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    nuevo_estado = payload.estado.strip().lower()
    if nuevo_estado not in ESTADOS_ORDEN:
        raise HTTPException(status_code=400, detail="Estado no válido")

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, estado FROM ordenes WHERE id = %s",
            (orden_id,),
        )
        orden = cursor.fetchone()
        if not orden:
            raise HTTPException(status_code=404, detail="Orden no encontrada")

        estado_anterior = orden["estado"]
        if estado_anterior == nuevo_estado:
            return {"orden_id": orden_id, "estado": nuevo_estado, "mensaje": "La orden ya tenía ese estado"}

        if estado_anterior == "confirmada" and nuevo_estado != "confirmada":
            ajustar_stock_orden(cursor, orden_id, 1)

        if estado_anterior != "confirmada" and nuevo_estado == "confirmada":
            ajustar_stock_orden(cursor, orden_id, -1)

        cursor.execute(
            "UPDATE ordenes SET estado = %s WHERE id = %s",
            (nuevo_estado, orden_id),
        )
        conexion.commit()
        return {"orden_id": orden_id, "estado": nuevo_estado, "mensaje": "Estado de la orden actualizado"}
    except HTTPException:
        conexion.rollback()
        raise
    except Exception:
        conexion.rollback()
        raise HTTPException(status_code=500, detail="No se pudo actualizar la orden")
    finally:
        cursor.close()
        conexion.close()


@app.get("/ordenes/{orden_id}/detalle")
async def detalle_orden(orden_id: int, current_user: dict = Depends(get_current_user)):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT id AS orden_id, usuario_id, total, estado, creado_en, direccion, metodo_pago, telefono, notas
            FROM ordenes
            WHERE id = %s
            """,
            (orden_id,),
        )
        orden = cursor.fetchone()
        if not orden:
            raise HTTPException(status_code=404, detail="Orden no encontrada")
        if orden["usuario_id"] != current_user["id"] and current_user["rol"] != "admin":
            raise HTTPException(status_code=403, detail="No autorizado")

        cursor.execute(
            """
            SELECT
                d.id AS item_id,
                d.orden_id,
                d.perfume_id,
                i.nombre AS perfume_nombre,
                i.marca AS perfume_marca,
                i.imagen AS perfume_imagen,
                d.cantidad,
                d.precio_unit,
                d.subtotal
            FROM orden_detalles d
            LEFT JOIN inventario i ON i.id = d.perfume_id
            WHERE d.orden_id = %s
            ORDER BY d.id ASC
            """,
            (orden_id,),
        )
        items = cursor.fetchall()

        return {"orden": orden, "items": items}
    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
