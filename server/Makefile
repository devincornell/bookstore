# Makefile for Bookstore FastAPI Server

# Variables
PYTHON = python3
PIP = pip3
UVICORN = uvicorn
ALEMBIC = alembic

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help setup install migration migrate-create migrate-upgrade migrate-downgrade run dev test clean lint format check-env

help: ## Show this help message
	@echo "$(BLUE)Bookstore FastAPI Server - Available Commands:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## Complete project setup (install dependencies, copy env file)
	@echo "$(YELLOW)Setting up the project...$(NC)"
	@$(MAKE) install
	@$(MAKE) check-env
	@echo "$(GREEN)✓ Project setup complete!$(NC)"
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  1. Edit .env file with your database credentials"
	@echo "  2. Run 'make migrate-create' to create initial migration"
	@echo "  3. Run 'make migrate-upgrade' to apply migrations"
	@echo "  4. Run 'make dev' to start the development server"

install: ## Install Python dependencies
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	@$(PIP) install -r requirements.txt

check-env: ## Check if .env file exists, create from template if not
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file from template...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✓ .env file created. Please edit it with your database credentials.$(NC)"; \
	else \
		echo "$(GREEN)✓ .env file already exists.$(NC)"; \
	fi

migration: migrate-create ## Alias for migrate-create

migrate-create: ## Create a new database migration
	@echo "$(YELLOW)Creating new migration...$(NC)"
	@$(ALEMBIC) revision --autogenerate -m "$(if $(MSG),$(MSG),Auto-generated migration)"
	@echo "$(GREEN)✓ Migration created successfully!$(NC)"

migrate-upgrade: ## Apply database migrations
	@echo "$(YELLOW)Applying database migrations...$(NC)"
	@$(ALEMBIC) upgrade head
	@echo "$(GREEN)✓ Migrations applied successfully!$(NC)"

migrate-downgrade: ## Downgrade database by one migration
	@echo "$(YELLOW)Downgrading database...$(NC)"
	@$(ALEMBIC) downgrade -1
	@echo "$(GREEN)✓ Database downgraded successfully!$(NC)"

migrate-history: ## Show migration history
	@echo "$(BLUE)Migration history:$(NC)"
	@$(ALEMBIC) history

migrate-current: ## Show current migration
	@echo "$(BLUE)Current migration:$(NC)"
	@$(ALEMBIC) current

run: ## Run the server in production mode
	@echo "$(YELLOW)Starting production server...$(NC)"
	@$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

dev: ## Run the server in development mode with auto-reload
	@echo "$(YELLOW)Starting development server...$(NC)"
	@$(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests (placeholder for future implementation)
	@echo "$(RED)Tests not implemented yet$(NC)"

lint: ## Run linting with flake8
	@echo "$(YELLOW)Running linter...$(NC)"
	@$(PYTHON) -m flake8 app/ --max-line-length=88 --exclude=__pycache__,migrations

format: ## Format code with black
	@echo "$(YELLOW)Formatting code...$(NC)"
	@$(PYTHON) -m black app/ --line-length=88

format-check: ## Check code formatting without making changes
	@echo "$(YELLOW)Checking code formatting...$(NC)"
	@$(PYTHON) -m black app/ --check --line-length=88

clean: ## Clean up cache files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@echo "$(GREEN)✓ Cleanup complete!$(NC)"

db-reset: ## Reset database (downgrade all, then upgrade)
	@echo "$(RED)Resetting database...$(NC)"
	@$(ALEMBIC) downgrade base
	@$(ALEMBIC) upgrade head
	@echo "$(GREEN)✓ Database reset complete!$(NC)"

logs: ## View application logs (if running with docker)
	@echo "$(BLUE)Application logs:$(NC)"
	@tail -f app.log 2>/dev/null || echo "No log file found"

requirements: ## Update requirements.txt
	@echo "$(YELLOW)Updating requirements.txt...$(NC)"
	@$(PIP) freeze > requirements.txt
	@echo "$(GREEN)✓ Requirements updated!$(NC)"

shell: ## Open Python shell with app context
	@echo "$(YELLOW)Opening Python shell...$(NC)"
	@$(PYTHON) -c "from app.database import SessionLocal; from app.models import *; print('Database session available as SessionLocal()')"

# Development helpers
install-dev: ## Install development dependencies
	@echo "$(YELLOW)Installing development dependencies...$(NC)"
	@$(PIP) install black flake8 pytest pytest-asyncio httpx
	@echo "$(GREEN)✓ Development dependencies installed!$(NC)"

quick-start: ## Quick start: setup + migrate + run
	@$(MAKE) setup
	@$(MAKE) migrate-create MSG="Initial migration"
	@$(MAKE) migrate-upgrade
	@$(MAKE) dev