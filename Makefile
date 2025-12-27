.PHONY: install dev build test clean setup-descope seed-db help

# Colors for terminal output
BLUE := \033[34m
GREEN := \033[32m
YELLOW := \033[33m
RESET := \033[0m

help:
	@echo "$(BLUE)IntelliFlow - Distributed Multi-Agent System$(RESET)"
	@echo ""
	@echo "$(GREEN)Available commands:$(RESET)"
	@echo "  make install        - Install all dependencies"
	@echo "  make dev            - Start development environment"
	@echo "  make build          - Build all Docker images"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests"
	@echo "  make clean          - Clean up containers and caches"
	@echo "  make setup-descope  - Configure Descope project"
	@echo "  make seed-db        - Seed database with test data"
	@echo "  make lint           - Run linters"
	@echo "  make format         - Format code"

install:
	@echo "$(BLUE)Installing backend dependencies...$(RESET)"
	cd backend/shared && pip install -e .
	cd backend/agent-a-summarizer && pip install -r requirements.txt
	cd backend/agent-b-calendar && pip install -r requirements.txt
	@echo "$(BLUE)Installing API gateway dependencies...$(RESET)"
	cd backend/api-gateway && npm install
	@echo "$(BLUE)Installing frontend dependencies...$(RESET)"
	cd frontend && npm install
	@echo "$(GREEN)All dependencies installed!$(RESET)"

dev:
	@echo "$(BLUE)Starting development environment...$(RESET)"
	docker-compose -f docker-compose.dev.yml up --build

dev-services:
	@echo "$(BLUE)Starting background services (DB, Redis)...$(RESET)"
	docker-compose -f docker-compose.dev.yml up -d postgres redis

build:
	@echo "$(BLUE)Building all Docker images...$(RESET)"
	docker-compose build

up:
	@echo "$(BLUE)Starting all services...$(RESET)"
	docker-compose up -d

down:
	@echo "$(BLUE)Stopping all services...$(RESET)"
	docker-compose down

test:
	@echo "$(BLUE)Running all tests...$(RESET)"
	cd backend/agent-a-summarizer && pytest tests/ -v
	cd backend/agent-b-calendar && pytest tests/ -v
	cd frontend && npm test

test-unit:
	@echo "$(BLUE)Running unit tests...$(RESET)"
	cd backend/agent-a-summarizer && pytest tests/unit/ -v
	cd backend/agent-b-calendar && pytest tests/unit/ -v

test-integration:
	@echo "$(BLUE)Running integration tests...$(RESET)"
	cd backend/agent-a-summarizer && pytest tests/integration/ -v
	cd backend/agent-b-calendar && pytest tests/integration/ -v

test-e2e:
	@echo "$(BLUE)Running end-to-end tests...$(RESET)"
	./scripts/test-e2e.sh

clean:
	@echo "$(YELLOW)Cleaning up...$(RESET)"
	docker-compose down -v --remove-orphans
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name dist -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Cleanup complete!$(RESET)"

setup-descope:
	@echo "$(BLUE)Setting up Descope...$(RESET)"
	python scripts/setup-descope.py

seed-db:
	@echo "$(BLUE)Seeding database...$(RESET)"
	python scripts/seed-db.py

lint:
	@echo "$(BLUE)Running linters...$(RESET)"
	cd backend/agent-a-summarizer && ruff check src/
	cd backend/agent-b-calendar && ruff check src/
	cd frontend && npm run lint

format:
	@echo "$(BLUE)Formatting code...$(RESET)"
	cd backend/agent-a-summarizer && ruff format src/
	cd backend/agent-b-calendar && ruff format src/
	cd frontend && npm run format

logs:
	docker-compose logs -f

logs-agent-a:
	docker-compose logs -f agent-a

logs-agent-b:
	docker-compose logs -f agent-b

logs-gateway:
	docker-compose logs -f api-gateway

migrate:
	@echo "$(BLUE)Running database migrations...$(RESET)"
	cd backend/shared && alembic upgrade head

migrate-create:
	@echo "$(BLUE)Creating new migration...$(RESET)"
	cd backend/shared && alembic revision --autogenerate -m "$(msg)"
