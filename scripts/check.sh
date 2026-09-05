#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# Locate repository root
# ============================================================

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
DEMO_DIR="$PROJECT_ROOT/demo"
ARCHIVE_DIR="$PROJECT_ROOT/archives"

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
# Build artefact information
# ============================================================

SHORT_COMMIT="$(git rev-parse --short HEAD)"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

TEMP_DIR="$(mktemp -d)"

RUFF_TEMP_REPORT="$TEMP_DIR/ruff-report.sarif"
SCHEMA_TEMP_REPORT="$TEMP_DIR/schema.yml"
COVERAGE_TEMP_DIR="$TEMP_DIR/coverage"

RUFF_ARCHIVE_REPORT="$ARCHIVE_DIR/ruff-report-${SHORT_COMMIT}-${TIMESTAMP}.sarif"
SCHEMA_ARCHIVE_REPORT="$ARCHIVE_DIR/schema-${SHORT_COMMIT}-${TIMESTAMP}.yml"
COVERAGE_ARCHIVE_DIR="$ARCHIVE_DIR/coverage-${SHORT_COMMIT}-${TIMESTAMP}"


# ============================================================
# Cleanup
# ============================================================

cleanup() {
    rm -rf "$TEMP_DIR"
}

trap cleanup EXIT


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
# Ruff SARIF report
# ============================================================

section "Generating Ruff SARIF report"

uv run ruff check . \
    --output-format sarif \
    > "$RUFF_TEMP_REPORT"

echo "Temporary Ruff SARIF report generated."


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

section "Generating and validating OpenAPI schema"

cd "$DEMO_DIR"

uv run python manage.py spectacular \
    --file "$SCHEMA_TEMP_REPORT" \
    --validate

echo "Temporary OpenAPI schema generated."


# ============================================================
# Check committed schema is current
# ============================================================

section "Checking OpenAPI schema is current"

if ! diff -q schema.yml "$SCHEMA_TEMP_REPORT" > /dev/null; then

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
# Full tests with branch coverage
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
# Generate HTML coverage report
# ============================================================

section "Generating HTML coverage report"

uv run coverage html \
    --directory "$COVERAGE_TEMP_DIR"

echo "Temporary HTML coverage report generated."


# ============================================================
# Archive successful artefacts
# ============================================================

section "Archiving successful check artefacts"

mkdir -p "$ARCHIVE_DIR"


# ------------------------------------------------------------
# Archive Ruff SARIF report
# ------------------------------------------------------------

cp "$RUFF_TEMP_REPORT" "$RUFF_ARCHIVE_REPORT"

echo "Ruff report archived:"
echo "  $RUFF_ARCHIVE_REPORT"


# ------------------------------------------------------------
# Archive OpenAPI schema
# ------------------------------------------------------------

cp "$SCHEMA_TEMP_REPORT" "$SCHEMA_ARCHIVE_REPORT"

echo
echo "OpenAPI schema archived:"
echo "  $SCHEMA_ARCHIVE_REPORT"


# ------------------------------------------------------------
# Archive HTML coverage report
# ------------------------------------------------------------

cp -R "$COVERAGE_TEMP_DIR" "$COVERAGE_ARCHIVE_DIR"

echo
echo "HTML coverage report archived:"
echo "  $COVERAGE_ARCHIVE_DIR"


# ============================================================
# Success
# ============================================================

echo
echo "============================================================"
echo "ALL CHECKS PASSED"
echo "============================================================"

echo
echo "Successful artefacts archived:"
echo
echo "  Ruff SARIF:"
echo "    $RUFF_ARCHIVE_REPORT"
echo
echo "  OpenAPI schema:"
echo "    $SCHEMA_ARCHIVE_REPORT"
echo
echo "  HTML coverage report:"
echo "    $COVERAGE_ARCHIVE_DIR/index.html"
echo