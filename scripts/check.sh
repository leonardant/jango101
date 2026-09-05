#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# Locate repository root
# ============================================================

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
DEMO_DIR="$PROJECT_ROOT/demo"

cd "$PROJECT_ROOT"


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

cd "$DEMO_DIR"

uv run python manage.py check


# ============================================================
# Check for missing migrations
# ============================================================

section "Checking for missing migrations"

uv run python manage.py makemigrations --check --dry-run


# ============================================================
# Ruff lint checks
# ============================================================

section "Ruff lint checks"

cd "$PROJECT_ROOT"

uv run ruff check .


# ============================================================
# Ruff formatting checks
# ============================================================

section "Ruff formatting checks"

uv run ruff format --check .


# ============================================================
# Bandit security scan
# ============================================================

section "Bandit security scan"

cd "$DEMO_DIR"

uv run bandit \
    -r api my1stapp \
    --exclude "api/tests,my1stapp/tests"


# ============================================================
# pip-audit dependency scan
# ============================================================

section "pip-audit dependency scan"

cd "$PROJECT_ROOT"

uv run pip-audit


# ============================================================
# OpenAPI schema validation
# ============================================================

section "Generating and validating OpenAPI schema"

cd "$DEMO_DIR"

TEMP_SCHEMA="$(mktemp)"

cleanup() {
    rm -f "$TEMP_SCHEMA"
}

trap cleanup EXIT

uv run python manage.py spectacular \
    --file "$TEMP_SCHEMA" \
    --validate


# ============================================================
# Check committed schema is current
# ============================================================

section "Checking OpenAPI schema is current"

if ! diff -q schema.yml "$TEMP_SCHEMA" > /dev/null; then

    echo
    echo "ERROR: demo/schema.yml is out of date."
    echo
    echo "Run:"
    echo
    echo "    cd demo"
    echo "    uv run python manage.py spectacular --file schema.yml --validate"
    echo

    exit 1

fi

echo "Committed schema.yml is current."


# ============================================================
# Full tests
# ============================================================

section "Running full test suite"

uv run python manage.py test


# ============================================================
# Success
# ============================================================

echo
echo "============================================================"
echo "ALL CHECKS PASSED"
echo "============================================================"
echo