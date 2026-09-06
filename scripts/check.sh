#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# Locate repository root
# ============================================================

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
DEMO_DIR="$PROJECT_ROOT/demo"
ARTIFACTS_DIR="$PROJECT_ROOT/.artifacts"

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
# Prepare artefact directory
# ============================================================

section "Preparing artefact directory"

rm -rf "$ARTIFACTS_DIR"

mkdir -p "$ARTIFACTS_DIR"


# ============================================================
# Cleanup artefacts on failure
# ============================================================

SUCCESS=false

cleanup() {

    if [[ "$SUCCESS" != true ]]; then
        rm -rf "$ARTIFACTS_DIR"
    fi

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
    > "$ARTIFACTS_DIR/ruff-report.sarif"

echo "Ruff SARIF report generated."


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
    > "$ARTIFACTS_DIR/bandit-report.html"

echo "Bandit HTML report generated."


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
    > "$ARTIFACTS_DIR/pip-audit-report.md"

echo "pip-audit Markdown report generated."


# ============================================================
# OpenAPI schema validation
# ============================================================

section "Generating and validating OpenAPI schema"

cd "$DEMO_DIR"

uv run python manage.py spectacular \
    --file "$ARTIFACTS_DIR/schema.yml" \
    --validate \
    > "$ARTIFACTS_DIR/drf-spectacular-report.txt" 2>&1

echo "OpenAPI schema generated."
echo "drf-spectacular report generated."


# ============================================================
# Check committed schema is current
# ============================================================

section "Checking OpenAPI schema is current"

if ! diff -q schema.yml "$ARTIFACTS_DIR/schema.yml" > /dev/null; then

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
    --directory "$ARTIFACTS_DIR/coverage"

echo "HTML coverage report generated."


# ============================================================
# Verify generated artefacts
# ============================================================

section "Verifying generated artefacts"

REQUIRED_FILES=(
    "$ARTIFACTS_DIR/ruff-report.sarif"
    "$ARTIFACTS_DIR/bandit-report.html"
    "$ARTIFACTS_DIR/pip-audit-report.md"
    "$ARTIFACTS_DIR/schema.yml"
    "$ARTIFACTS_DIR/drf-spectacular-report.txt"
)

for FILE in "${REQUIRED_FILES[@]}"; do

    if [[ ! -f "$FILE" ]]; then

        echo
        echo "ERROR: Expected artefact was not generated:"
        echo
        echo "  $FILE"
        echo

        exit 1

    fi

done


if [[ ! -d "$ARTIFACTS_DIR/coverage" ]]; then

    echo
    echo "ERROR: Coverage report directory was not generated:"
    echo
    echo "  $ARTIFACTS_DIR/coverage"
    echo

    exit 1

fi

echo "All expected artefacts were generated successfully."


# ============================================================
# Success
# ============================================================

SUCCESS=true

echo
echo "============================================================"
echo "ALL CHECKS PASSED"
echo "============================================================"

echo
echo "Artefacts staged in:"
echo
echo "  $ARTIFACTS_DIR"
echo