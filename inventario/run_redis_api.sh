#!/bin/bash
# Script para ejecutar Redis + API + diagnosticar problemas
# Archivo: run_redis_api.sh
# Uso: bash run_redis_api.sh

set -e

echo "=========================================="
echo "INICIANDO REDIS + API + DIAGNÓSTICO"
echo "=========================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "main.py" ]; then
    echo "✗ Error: main.py no encontrado"
    echo "  Ejecuta desde: /home/juan/programacion-distribuida/inventario"
    exit 1
fi

# 1. Matar procesos previos
echo ""
echo "1️⃣  Limpiando procesos previos..."
pkill -f "redis-server" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 1

# 2. Verificar Redis disponible
echo ""
echo "2️⃣  Verificando Redis..."
if ! command -v redis-server &> /dev/null; then
    echo "✗ Redis no está instalado"
    exit 1
fi
echo "✓ Redis encontrado"

# 3. Iniciar Redis
echo ""
echo "3️⃣  Iniciando Redis en puerto 6379..."
redis-server --daemonize yes --logfile /tmp/redis.log
sleep 2

# Verificar que Redis esté corriendo
if redis-cli ping &>/dev/null; then
    echo "✓ Redis está corriendo"
else
    echo "✗ Redis no responde"
    echo "  Log: $(cat /tmp/redis.log)"
    exit 1
fi

# 4. Verificar BD
echo ""
echo "4️⃣  Verificando base de datos..."
python3 -c "from database import obtener_conexion; c = obtener_conexion(); c.close(); print('✓ Base de datos conectada')" || echo "✗ Error de BD"

# 5. Activar venv e iniciar API
echo ""
echo "5️⃣  Iniciando API en puerto 8000..."
source venv/bin/activate
exec python main.py
