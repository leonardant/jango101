#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# Locate repository root
# ============================================================

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
DEMO_DIR="$PROJECT_ROOT/demo"
ARCHIVES_DIR="$PROJECT_ROOT/archives"

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
# Build run information
# ============================================================

SHORT_COMMIT="$(git rev-parse --short HEAD)"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

RUN_DIR="$ARCHIVES_DIR/${TIMESTAMP}-${SHORT_COMMIT}"

TEMP_DIR="$(mktemp -d)"

RUFF_TEMP_REPORT="$TEMP_DIR/ruff-report.sarif"
BANDIT_TEMP_REPORT="$TEMP_DIR/bandit-report.html"
PIP_AUDIT_TEMP_REPORT="$TEMP_DIR/pip-audit-report.md"
SCHEMA_TEMP_REPORT="$TEMP_DIR/schema.yml"
COVERAGE_TEMP_DIR="$TEMP_DIR/coverage"


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

uv run bandit \
    -r api my1stapp \
    --exclude "api/tests,my1stapp/tests"


# ============================================================
# Bandit HTML report
# ============================================================

section "Generating Bandit HTML report"

uv run bandit \
    -r api my1stapp \
    --exclude "api/tests,my1stapp/tests" \
    --format html \
    > "$BANDIT_TEMP_REPORT"

echo "Temporary Bandit HTML report generated."


# ============================================================
# pip-audit dependency scan
# ============================================================

section "pip-audit dependency scan"

cd "$PROJECT_ROOT"

uv run pip-audit


# ============================================================
# pip-audit Markdown report
# ============================================================

section "Generating pip-audit Markdown report"

uv run pip-audit \
    --format markdown \
    > "$PIP_AUDIT_TEMP_REPORT"

echo "Temporary pip-audit Markdown report generated."


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
# Verify generated artefacts
# ============================================================

section "Verifying generated artefacts"

REQUIRED_FILES=(
    "$RUFF_TEMP_REPORT"
    "$BANDIT_TEMP_REPORT"
    "$PIP_AUDIT_TEMP_REPORT"
    "$SCHEMA_TEMP_REPORT"
)


for FILE in "${REQUIRED_FILES[@]}"; do

    if [[ ! -f "$FILE" ]]; then

        echo
        echo "ERROR: Expected report was not generated:"
        echo
        echo "  $FILE"
        echo

        exit 1

    fi

done


if [[ ! -d "$COVERAGE_TEMP_DIR" ]]; then

    echo
    echo "ERROR: Coverage report directory was not generated:"
    echo
    echo "  $COVERAGE_TEMP_DIR"
    echo

    exit 1

fi


echo "All expected artefacts were generated successfully."


# ============================================================
# Archive successful artefacts
# ============================================================

section "Archiving successful check artefacts"

mkdir -p "$RUN_DIR"

cp "$RUFF_TEMP_REPORT" \
    "$RUN_DIR/ruff-report.sarif"

cp "$BANDIT_TEMP_REPORT" \
    "$RUN_DIR/bandit-report.html"

cp "$PIP_AUDIT_TEMP_REPORT" \
    "$RUN_DIR/pip-audit-report.md"

cp "$SCHEMA_TEMP_REPORT" \
    "$RUN_DIR/schema.yml"

cp -R "$COVERAGE_TEMP_DIR" \
    "$RUN_DIR/coverage"


# ============================================================
# Success
# ============================================================

echo
echo "============================================================"
echo "ALL CHECKS PASSED"
echo "============================================================"

echo
echo "Successful artefacts archived in:"
echo
echo "  $RUN_DIR"
echo

echo "Contents:"
echo "  ruff-report.sarif"
echo "  bandit-report.html"
echo "  pip-audit-report.md"
echo "  schema.yml"
echo "  coverage/index.html"
echo