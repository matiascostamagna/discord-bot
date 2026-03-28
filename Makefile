.PHONY: help install dev test lint format clean docker-build docker-up docker-down db-migrate

help:
	@echo "Music Bot - Comandos disponibles"
	@echo "================================"
	@echo "make install      - Instalar dependencias"
	@echo "make dev          - Ejecutar bot en modo desarrollo"
	@echo "make test         - Ejecutar tests"
	@echo "make lint         - Validar código con flake8"
	@echo "make format       - Formatear código con black"
	@echo "make clean        - Limpiar archivos generados"
	@echo "make docker-build - Construir imagen Docker"
	@echo "make docker-up    - Iniciar servicios con Docker Compose"
	@echo "make docker-down  - Detener servicios Docker"
	@echo "make db-migrate   - Ejecutar migraciones de BD"

install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	@echo "✅ Dependencias instaladas"

dev:
	@echo "🚀 Iniciando bot en modo desarrollo..."
	export NODE_ENV=development && python src/main.py

test:
	@echo "🧪 Ejecutando tests..."
	pytest -v --cov=src tests/

lint:
	@echo "🔍 Validando código..."
	flake8 src/ --max-line-length=120 --exclude=migrations,__pycache__

format:
	@echo "✨ Formateando código..."
	black src/ tests/

clean:
	@echo "🗑️  Limpiando archivos..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
	@echo "✅ Limpieza completada"

docker-build:
	@echo "🐳 Construyendo imagen Docker..."
	docker build -t musicbot:latest .
	@echo "✅ Imagen construida"

docker-up:
	@echo "🚀 Iniciando servicios Docker..."
	docker-compose up -d
	@echo "✅ Servicios iniciados"
	@echo "Bot disponible en los próximos momentos..."

docker-down:
	@echo "🛑 Deteniendo servicios Docker..."
	docker-compose down
	@echo "✅ Servicios detenidos"

docker-logs:
	docker-compose logs -f musicbot

db-migrate:
	@echo "🔄 Ejecutando migraciones..."
	alembic upgrade head
	@echo "✅ Migraciones completadas"

db-reset:
	@echo "⚠️  Reseteando base de datos..."
	python scripts/setup_db.py --reset
	@echo "✅ BD reseteada"
