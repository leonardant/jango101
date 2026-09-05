#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# Locate repository root
# ============================================================

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

DEMO_DIR="$PROJECT_ROOT/demo"

cd "$DEMO_DIR"


# ============================================================
# Helper
# ============================================================

section() {
    echo
    echo "============================================================"
    echo "$1"
    echo "============================================================"
}


# ============================================================
# Django system checks
# ============================================================

section "Django system checks"

uv run python manage.py check


# ============================================================
# Check for missing migrations
# ============================================================

section "Checking for missing migrations"

uv run python manage.py makemigrations --check --dry-run


# ============================================================
# Ruff linting
# ============================================================

section "Ruff lint checks"

cd "$PROJECT_ROOT"

uv run ruff check .


# ============================================================
# Ruff formatting
# ============================================================

section "Ruff formatting checks"

uv run ruff format --check .


# ============================================================
# Bandit security scan
# ============================================================

section "Bandit security scan"

cd "$DEMO_DIR"

uv run bandit -r api my1stapp


# ============================================================
# Dependency vulnerability scan
# ============================================================

section "pip-audit dependency scan"

cd "$PROJECT_ROOT"

uv run pip-audit


# ============================================================
# OpenAPI schema validation
# ============================================================

section "OpenAPI schema validation"

cd "$DEMO_DIR"

TEMP_SCHEMA="$(mktemp)"

trap 'rm -f "$TEMP_SCHEMA"' EXIT

uv run python manage.py spectacular \
    --file "$TEMP_SCHEMA" \
    --validate


# ============================================================
# Check committed schema is current
# ============================================================

section "Checking OpenAPI schema is current"

if ! diff -q schema.yml "$TEMP_SCHEMA" > /dev/null; then

    echo
    echo "ERROR: schema.yml is out of date."
    echo
    echo "Run:"
    echo
    echo "    cd demo"
    echo "    uv run python manage.py spectacular --file schema.yml --validate"
    echo
    exit 1

fi


# ============================================================
# Tests with branch coverage
# ============================================================

section "Running tests with branch coverage"

uv run coverage run \
    --branch \
    --source=api,my1stapp \
    manage.py test


# ============================================================
# Coverage report
# ============================================================

section "Coverage report"

uv run coverage report -m


# ============================================================
# Success
# ============================================================

echo
echo "============================================================"
echo "ALL CHECKS PASSED"
echo "============================================================"