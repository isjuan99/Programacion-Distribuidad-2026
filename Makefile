# ══════════════════════════════════════════════════════════════════════════════
# Aroma-Distribuido — Makefile
# ══════════════════════════════════════════════════════════════════════════════
#
# Uso rápido:
#   make start       →  Levanta todo (primera vez o después de cambios)
#   make stop        →  Detiene todos los contenedores
#   make restart     →  Reinicia todo
#   make logs        →  Muestra logs en tiempo real
#   make status      →  Estado de los contenedores
#   make help        →  Lista todos los comandos disponibles
#
# ══════════════════════════════════════════════════════════════════════════════

COMPOSE  = docker compose
BACKEND  = aroma-backend
FRONTEND = aroma-frontend
DB       = aroma-db
REDIS    = aroma-redis

# Colores para output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
RED    := \033[0;31m
RESET  := \033[0m
BOLD   := \033[1m

.DEFAULT_GOAL := help
.PHONY: help start stop down restart build rebuild fresh install \
        logs logs-backend logs-frontend logs-worker logs-db \
        status ps shell-backend shell-frontend shell-worker \
        db-shell db-backup db-restore \
        redis-cli flush-cache \
        health clean clean-all lint test

# ── Ayuda ─────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "$(BOLD)$(CYAN)╔══════════════════════════════════════════════╗$(RESET)"
	@echo "$(BOLD)$(CYAN)║       Aroma-Distribuido — Comandos           ║$(RESET)"
	@echo "$(BOLD)$(CYAN)╚══════════════════════════════════════════════╝$(RESET)"
	@echo ""
	@echo "$(BOLD)$(YELLOW)▶ INICIO / PARADA$(RESET)"
	@echo "  $(GREEN)make start$(RESET)          Levanta todo (build + up)"
	@echo "  $(GREEN)make stop$(RESET)           Detiene todos los contenedores"
	@echo "  $(GREEN)make restart$(RESET)        Reinicia todos los contenedores"
	@echo "  $(GREEN)make rebuild$(RESET)        Reconstruye imágenes y reinicia"
	@echo "  $(GREEN)make fresh$(RESET)          Borra todo y arranca desde cero"
	@echo ""
	@echo "$(BOLD)$(YELLOW)▶ LOGS$(RESET)"
	@echo "  $(GREEN)make logs$(RESET)           Todos los logs en tiempo real"
	@echo "  $(GREEN)make logs-backend$(RESET)   Logs del backend (FastAPI)"
	@echo "  $(GREEN)make logs-frontend$(RESET)  Logs del frontend (Nginx)"
	@echo "  $(GREEN)make logs-worker$(RESET)    Logs del worker (RabbitMQ consumer)"
	@echo "  $(GREEN)make logs-db$(RESET)        Logs de PostgreSQL"
	@echo ""
	@echo "$(BOLD)$(YELLOW)▶ ESTADO$(RESET)"
	@echo "  $(GREEN)make status$(RESET)         Estado de los contenedores"
	@echo "  $(GREEN)make health$(RESET)         Health check de todos los servicios"
	@echo ""
	@echo "$(BOLD)$(YELLOW)▶ CONSOLAS$(RESET)"
	@echo "  $(GREEN)make shell-backend$(RESET)  Shell dentro del contenedor backend"
	@echo "  $(GREEN)make shell-frontend$(RESET) Shell dentro del contenedor frontend"
	@echo "  $(GREEN)make shell-worker$(RESET)   Shell dentro del contenedor worker"
	@echo "  $(GREEN)make db-shell$(RESET)       Consola PostgreSQL (psql)"
	@echo "  $(GREEN)make redis-cli$(RESET)      Consola Redis"
	@echo ""
	@echo "$(BOLD)$(YELLOW)▶ BASE DE DATOS$(RESET)"
	@echo "  $(GREEN)make db-backup$(RESET)      Exporta un backup de la BD"
	@echo "  $(GREEN)make db-restore$(RESET)     Restaura desde un backup (FILE=ruta)"
	@echo "  $(GREEN)make flush-cache$(RESET)    Limpia el caché de Redis"
	@echo ""
	@echo "$(BOLD)$(YELLOW)▶ LIMPIEZA$(RESET)"
	@echo "  $(GREEN)make clean$(RESET)          Detiene y elimina contenedores"
	@echo "  $(GREEN)make clean-all$(RESET)      Elimina contenedores, imágenes y volúmenes"
	@echo ""
	@echo "$(BOLD)$(YELLOW)▶ URLS$(RESET)"
	@echo "  Frontend    →  http://localhost"
	@echo "  API docs    →  http://localhost:8000/docs"
	@echo "  RabbitMQ    →  http://localhost:15672  (aroma_user / aroma_secret)"
	@echo "  Logs        →  http://localhost:8888"
	@echo "  Portainer   →  http://localhost:9000"
	@echo ""

# ── Inicio / Parada ───────────────────────────────────────────────────────────
start:
	@echo "$(CYAN)▶ Construyendo imágenes y levantando servicios...$(RESET)"
	$(COMPOSE) up -d --build
	@echo ""
	@echo "$(GREEN)✓ Aroma-Distribuido está corriendo$(RESET)"
	@echo ""
	@echo "  Frontend  →  http://localhost"
	@echo "  API docs  →  http://localhost:8000/docs"
	@echo "  RabbitMQ  →  http://localhost:15672"
	@echo "  Dozzle    →  http://localhost:8888"
	@echo "  Portainer →  http://localhost:9000"
	@echo ""

up:
	@echo "$(CYAN)▶ Levantando servicios...$(RESET)"
	$(COMPOSE) up -d
	@echo "$(GREEN)✓ Servicios activos$(RESET)"

stop:
	@echo "$(YELLOW)▶ Deteniendo servicios...$(RESET)"
	$(COMPOSE) stop
	@echo "$(GREEN)✓ Servicios detenidos$(RESET)"

down:
	@echo "$(YELLOW)▶ Bajando servicios...$(RESET)"
	$(COMPOSE) down
	@echo "$(GREEN)✓ Contenedores eliminados$(RESET)"

restart:
	@echo "$(CYAN)▶ Reiniciando servicios...$(RESET)"
	$(COMPOSE) restart
	@echo "$(GREEN)✓ Servicios reiniciados$(RESET)"

restart-backend:
	@echo "$(CYAN)▶ Reiniciando backend...$(RESET)"
	$(COMPOSE) restart backend
	@echo "$(GREEN)✓ Backend reiniciado$(RESET)"

restart-frontend:
	@echo "$(CYAN)▶ Reiniciando frontend...$(RESET)"
	$(COMPOSE) restart frontend
	@echo "$(GREEN)✓ Frontend reiniciado$(RESET)"

# ── Build ─────────────────────────────────────────────────────────────────────
build:
	@echo "$(CYAN)▶ Construyendo imágenes...$(RESET)"
	$(COMPOSE) build
	@echo "$(GREEN)✓ Imágenes construidas$(RESET)"

rebuild:
	@echo "$(CYAN)▶ Reconstruyendo imágenes y reiniciando...$(RESET)"
	$(COMPOSE) up -d --build --force-recreate
	@echo "$(GREEN)✓ Reconstrucción completa$(RESET)"

rebuild-backend:
	@echo "$(CYAN)▶ Reconstruyendo backend...$(RESET)"
	$(COMPOSE) up -d --build --force-recreate backend
	@echo "$(GREEN)✓ Backend reconstruido$(RESET)"

rebuild-frontend:
	@echo "$(CYAN)▶ Reconstruyendo frontend...$(RESET)"
	$(COMPOSE) up -d --build --force-recreate frontend
	@echo "$(GREEN)✓ Frontend reconstruido$(RESET)"

# ── Fresh (desde cero) ────────────────────────────────────────────────────────
fresh:
	@echo "$(RED)▶ Eliminando todo y arrancando desde cero...$(RESET)"
	@echo "$(RED)  ADVERTENCIA: se borrarán los volúmenes (datos de BD)$(RESET)"
	@read -p "  ¿Continuar? [s/N] " confirm && [ "$$confirm" = "s" ] || exit 1
	$(COMPOSE) down -v --remove-orphans
	$(COMPOSE) up -d --build
	@echo "$(GREEN)✓ Instalación limpia completada$(RESET)"

install: start

# ── Logs ──────────────────────────────────────────────────────────────────────
logs:
	$(COMPOSE) logs -f --tail=100

logs-backend:
	$(COMPOSE) logs -f --tail=100 backend

logs-frontend:
	$(COMPOSE) logs -f --tail=50 frontend

logs-worker:
	$(COMPOSE) logs -f --tail=100 worker

logs-db:
	$(COMPOSE) logs -f --tail=50 db

logs-redis:
	$(COMPOSE) logs -f --tail=50 redis

logs-rabbit:
	$(COMPOSE) logs -f --tail=50 rabbitmq

# ── Estado ────────────────────────────────────────────────────────────────────
status:
	@echo ""
	@echo "$(BOLD)$(CYAN)Estado de los contenedores:$(RESET)"
	@echo ""
	$(COMPOSE) ps
	@echo ""

ps: status

health:
	@echo ""
	@echo "$(BOLD)$(CYAN)Health check:$(RESET)"
	@echo ""
	@curl -sf http://localhost:8000/api/v1/health | python -m json.tool 2>/dev/null \
		|| echo "$(RED)  Backend no responde$(RESET)"
	@echo ""
	@docker exec $(REDIS) redis-cli ping 2>/dev/null \
		&& echo "$(GREEN)  Redis: OK$(RESET)" \
		|| echo "$(RED)  Redis: no responde$(RESET)"
	@docker exec $(DB) pg_isready -U aroma_user -d aroma_db 2>/dev/null \
		&& echo "$(GREEN)  PostgreSQL: OK$(RESET)" \
		|| echo "$(RED)  PostgreSQL: no responde$(RESET)"
	@echo ""

# ── Consolas ──────────────────────────────────────────────────────────────────
shell-backend:
	docker exec -it $(BACKEND) bash

shell-frontend:
	docker exec -it $(FRONTEND) sh

shell-worker:
	docker exec -it aroma-worker bash

db-shell:
	docker exec -it $(DB) psql -U aroma_user -d aroma_db

redis-cli:
	docker exec -it $(REDIS) redis-cli

# ── Base de datos ─────────────────────────────────────────────────────────────
db-backup:
	@mkdir -p backups
	@FILENAME="backups/aroma_db_$$(date +%Y%m%d_%H%M%S).sql"; \
	docker exec $(DB) pg_dump -U aroma_user aroma_db > $$FILENAME; \
	echo "$(GREEN)✓ Backup guardado en: $$FILENAME$(RESET)"

db-restore:
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Debes indicar el archivo: make db-restore FILE=backups/archivo.sql$(RESET)"; \
		exit 1; \
	fi
	@echo "$(CYAN)▶ Restaurando desde $(FILE)...$(RESET)"
	docker exec -i $(DB) psql -U aroma_user -d aroma_db < $(FILE)
	@echo "$(GREEN)✓ Restauración completada$(RESET)"

flush-cache:
	@echo "$(CYAN)▶ Limpiando caché de Redis...$(RESET)"
	docker exec $(REDIS) redis-cli FLUSHDB
	@echo "$(GREEN)✓ Caché limpiado$(RESET)"

# ── Limpieza ──────────────────────────────────────────────────────────────────
clean:
	@echo "$(YELLOW)▶ Deteniendo y eliminando contenedores...$(RESET)"
	$(COMPOSE) down --remove-orphans
	@echo "$(GREEN)✓ Limpieza completada$(RESET)"

clean-all:
	@echo "$(RED)▶ Eliminando contenedores, imágenes y volúmenes...$(RESET)"
	@echo "$(RED)  ADVERTENCIA: se perderán todos los datos de la BD$(RESET)"
	@read -p "  ¿Continuar? [s/N] " confirm && [ "$$confirm" = "s" ] || exit 1
	$(COMPOSE) down -v --remove-orphans --rmi local
	@echo "$(GREEN)✓ Todo eliminado$(RESET)"
