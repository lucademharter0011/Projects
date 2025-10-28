# Detect OS for venv paths and python command
ifeq ($(OS),Windows_NT)
  PYTHON_SYS       := python
  VENV_DIR         := backend\.venv
  VENV_BIN         := $(VENV_DIR)\Scripts
  PYTHON           := $(VENV_BIN)\python.exe
  PIP              := $(VENV_BIN)\pip.exe
else
  PYTHON_SYS       := python3
  VENV_DIR         := backend/.venv
  VENV_BIN         := $(VENV_DIR)/bin
  PYTHON           := $(VENV_BIN)/python
  PIP              := $(VENV_BIN)/pip
endif

.PHONY: install install-backend install-frontend \
        build build-backend build-frontend \
        test test-backend test-frontend \
        lint lint-backend lint-frontend \
        clean

install: install-backend install-frontend
	@echo "\n✅ All dependencies installed."

install-backend:
	@echo "\n🔧 Setting up Python venv & installing backend deps…"
	@if [ ! -d "$(VENV_DIR)" ]; then \
	  $(PYTHON_SYS) -m venv "$(VENV_DIR)"; \
	else \
	  echo "    • venv already exists"; \
	fi
	@"$(PIP)" install --upgrade pip
	@"$(PIP)" install -r backend/requirements.txt

install-frontend:
	@echo "\n📦 Installing frontend deps…"
	npm install
	cd frontend && npm install

build: build-backend build-frontend
	@echo "\n🚀 Full build complete."

build-backend:
	@echo "\n🔨 Flask backend has no build step; ready to run."

build-frontend:
	@echo "\n🔨 Building Next.js frontend…"
	cd frontend && npm run build

test: test-backend test-frontend
	@echo "\n✅ All tests passed."

test-backend:
	@echo "\n🧪 Running backend tests…"
	@"$(PYTHON)" -m pytest -q

test-frontend:
	@echo "\n🧪 Running frontend tests…"
	cd frontend && npm test

lint: lint-frontend
	@echo "\n✅ Linting complete."

lint-frontend:
	@echo "\n🔍 Linting frontend (ESLint)…"
	cd frontend && npm run lint

clean:
ifeq ($(OS),Windows_NT)
	@echo "\n🧹 Cleaning on Windows…"
	@rmdir /S /Q "$(VENV_DIR)"          >nul 2>&1 || true
	@rmdir /S /Q "backend\__pycache__" >nul 2>&1 || true
	@del    /Q "backend\*.pyc"         >nul 2>&1 || true
	@rmdir /S /Q "frontend\node_modules">nul 2>&1 || true
	@rmdir /S /Q "frontend\.next"      >nul 2>&1 || true
else
	@echo "\n🧹 Cleaning on UNIX…"
	@rm -rf "$(VENV_DIR)" backend/__pycache__ backend/*.pyc
	@rm -rf frontend/node_modules frontend/.next
endif
	@echo "\n🧹 Clean complete."
