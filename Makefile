# Down&Conv - Development Makefile
# Windows: usare Git Bash, WSL o "make" da Chocolatey

PYTHON ?= python
VENV ?= .venv
PY ?= $(VENV)/Scripts/python
PIP ?= $(VENV)/Scripts/pip

# Windows vs Unix
ifeq ($(OS),Windows_NT)
	ACTIVATE = $(VENV)\Scripts\activate
	PY = $(VENV)/Scripts/python.exe
	PIP = $(VENV)/Scripts/pip.exe
else
	ACTIVATE = . $(VENV)/bin/activate
	PY = $(VENV)/bin/python
	PIP = $(VENV)/bin/pip
endif

.PHONY: help install run lint format test check clean build

help:
	@echo "Down&Conv - Comandi sviluppo"
	@echo ""
	@echo "  make install   - Crea venv e installa dipendenze"
	@echo "  make run       - Avvia applicazione"
	@echo "  make lint      - ruff check"
	@echo "  make format    - ruff format"
	@echo "  make test      - pytest"
	@echo "  make check     - lint + format + test"
	@echo "  make clean     - Rimuove cache e build"
	@echo "  make build     - Build PyInstaller"

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install -r requirements.txt
	$(PIP) install ruff pytest pre-commit
	@echo "Run: pre-commit install"

run:
	cd src && $(PY) -m downconv.main

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

test:
	pytest tests/ -v

check: lint format test

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build dist *.spec 2>/dev/null || true

build:
	$(PIP) install pyinstaller
	pyinstaller --onefile --windowed --name DownConv \
		--hidden-import=PySide6.QtCore --hidden-import=PySide6.QtGui --hidden-import=PySide6.QtWidgets \
		--add-data "src/downconv/resources;downconv/resources" \
		src/downconv/main.py
