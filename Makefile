# HexAgents — Makefile
# Orchestrate the backend + flutter workflow, and the guards.
#
#   make install   -> poetry install (dev deps)
#   make check     -> ruff + mypy (strict)
#   make test      -> pytest (unit)
#   make coverage  -> pytest with coverage report
#   make guard     -> hexa_guard.py (purity of backend domain)
#   make agent-guard -> agent_guard.py (territories)
#   make update-badge -> refresh test-count badge in README.md
#   make web       -> run the Flutter mobile app in the browser (Chrome)
#   make flutter-check -> flutter analyze
#   make flutter-test -> flutter test
#   make run-backend -> run the HexAgents FastAPI backend (reads src/backend/.env)

PY ?= poetry run
BACKEND := src/backend
CLI_PKG := hexagents/infrastructure/presenters/cli
REACT_DIR := react
FLUTTER_DIR := flutter
RUST_DIR := rust
HEXAGUARD := tools/hexa_guard.py
AGENTGUARD := tools/agent_guard.py
PYTHON := python

.PHONY: help install check lint fmt test test-all coverage guard agent-guard update-badge all \
	run-cli run-chat cli-check cli-test \
	web-dev web-check web-test \
	web flutter-check flutter-test run-backend \
	rust-build rust-check rust-test

help:
	@echo ""
	@echo "══════════════════════════════════════════"
	@echo "     🧩 HEXAGENTS — AI Agents Assistant"
	@echo "══════════════════════════════════════════"
	@echo ""
	@echo "📦 BACKEND SETUP"
	@echo "  make install           → Install Poetry dependencies (src/backend)"
	@echo "  make run-backend       → Launch the FastAPI backend (uvicorn, reads src/backend/.env)"
	@echo ""
	@echo "🧪 CODE QUALITY (backend)"
	@echo "  make lint              → Lint Python with ruff"
	@echo "  make fmt               → Check formatting with ruff"
	@echo "  make check             → Run ruff + strict mypy"
	@echo "  make guard             → Run hexa_guard.py (architecture purity)"
	@echo "  make agent-guard       → Run agent_guard.py (territories)"
	@echo ""
	@echo "🧪 TESTS (backend)"
	@echo "  make test              → Run unit tests (pytest)"
	@echo "  make test-all          → Run all tests (backend + web + flutter)"
	@echo "  make coverage          → Run tests with coverage (≥90%)"
	@echo "  make update-badge      → Update test count badge in README.md"
	@echo ""
	@echo "📱 FLUTTER APP"
	@echo "  make web               → Run the Flutter app in the browser (Chrome)"
	@echo "  make flutter-check     → flutter analyze"
	@echo "  make flutter-test      → flutter test"
	@echo ""
	@echo "🔨 HEXA CLI (hexagents/infrastructure/presenters/cli — presenter, part of backend)"
	@echo "  make run-cli           → Run the hexa CLI (violet group)"
	@echo "  make run-chat          → Chat with the agent interactively (hexa chat)"
	@echo "  make cli-check         → ruff + strict mypy on the CLI presenter"
	@echo "  make cli-test          → pytest + coverage on the CLI presenter"
	@echo ""
	@echo "🌐 REACT UI (react — dashboard hexagonal)"
	@echo "  make web-dev           → Start the Vite dev server for the React UI"
	@echo "  make web-check         → tsc --strict + eslint on the React UI"
	@echo "  make web-test          → vitest (domain/application coverage)"
	@echo ""
	@echo "🦀 RUST (rust — hotspots behind driven ports, optional toolchain)"
	@echo "  make rust-build        → maturin develop (builds hexagents_rust into src/backend/.venv)"
	@echo "  make rust-check        → cargo fmt --check + cargo clippy -D warnings"
	@echo "  make rust-test         → cargo test --workspace (pure Rust, no Python needed)"
	@echo ""
	@echo "🔨 ALL"
	@echo "  make all               → check + test + guard + agent-guard + cli + web"
	@echo ""

install:
	cd $(BACKEND) && poetry install

run-backend:
	cd $(BACKEND) && poetry run uvicorn hexagents.main:app --host 0.0.0.0 --port 8000 --reload

check:
	cd $(BACKEND) && poetry run ruff check hexagents
	cd $(BACKEND) && poetry run mypy hexagents

lint:
	cd $(BACKEND) && poetry run ruff check hexagents

fmt:
	cd $(BACKEND) && poetry run ruff format --check hexagents

test:
	cd $(BACKEND) && poetry run pytest hexagents/tests $(CLI_PKG)/tests -m 'not integration and not e2e' --tb=short

test-all:
	cd $(BACKEND) && poetry run pytest hexagents/tests $(CLI_PKG)/tests -m 'not integration and not e2e' --tb=short
	cd $(REACT_DIR) && npm run coverage
	cd $(FLUTTER_DIR) && flutter test

coverage:
	cd $(BACKEND) && poetry run pytest hexagents/tests $(CLI_PKG)/tests --cov=hexagents --cov-report=term-missing --cov-fail-under=95

guard:
	python $(HEXAGUARD) --all --root src/backend/hexagents

agent-guard:
	python $(AGENTGUARD) --root .

update-badge:
	@echo "🏷️  Updating test count badge in README.md..."
	$(PYTHON) scripts/update_test_badge.py

run-cli:
	@cd $(BACKEND) && poetry run hexa

run-chat:
	@cd $(BACKEND) && poetry run hexa chat

cli-check:
	cd $(BACKEND) && poetry run ruff check $(CLI_PKG)
	cd $(BACKEND) && poetry run mypy $(CLI_PKG)

cli-test:
	cd $(BACKEND) && poetry run pytest $(CLI_PKG)/tests --cov=hexagents.infrastructure.presenters.cli --cov-report=term-missing --cov-fail-under=95 -q

web-dev:
	@cd $(REACT_DIR) && npm run dev

web-check:
	cd $(REACT_DIR) && npm run typecheck
	cd $(REACT_DIR) && npm run lint

web-test:
	cd $(REACT_DIR) && npm run coverage

web:
	cd $(FLUTTER_DIR) && flutter run -d chrome

flutter-check:
	cd $(FLUTTER_DIR) && flutter analyze

flutter-test:
	cd $(FLUTTER_DIR) && flutter test

rust-build:
	cd $(RUST_DIR) && VIRTUAL_ENV=$(CURDIR)/$(BACKEND)/.venv $(CURDIR)/$(BACKEND)/.venv/bin/maturin develop --release

rust-check:
	cd $(RUST_DIR) && cargo fmt --check
	cd $(RUST_DIR) && cargo clippy --workspace --all-targets -- -D warnings

rust-test:
	cd $(RUST_DIR) && cargo test --workspace

all: check test guard agent-guard cli-check cli-test web-check web-test rust-check rust-test
	@echo "All gates green."
