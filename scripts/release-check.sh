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
# Django deployment checks
# ============================================================

section "Django deployment checks"

uv run python manage.py check --deploy


# ============================================================
# Compile translations
# ============================================================

section "Compiling translations"

uv run python manage.py compilemessages


# ============================================================
# Validate OpenAPI schema
# ============================================================

section "Validating OpenAPI schema"

uv run python manage.py spectacular \
    --file schema.yml \
    --validate


# ============================================================
# Collect static files
# ============================================================

section "Collecting static files"

uv run python manage.py collectstatic --noinput


# ============================================================
# Success
# ============================================================

echo
echo "============================================================"
echo "RELEASE CHECKS PASSED"
echo "============================================================"