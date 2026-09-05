#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# Locate repository root
# ============================================================

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
ARTIFACTS_DIR="$PROJECT_ROOT/.artifacts"
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
# Check Git repository
# ============================================================

section "Checking Git repository"

if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "ERROR: This script must be run inside a Git repository."
    exit 1
fi

echo "Git repository: OK"


# ============================================================
# Check staged artefacts exist
# ============================================================

section "Checking staged artefacts"

if [[ ! -d "$ARTIFACTS_DIR" ]]; then

    echo
    echo "ERROR: No staged artefacts found."
    echo
    echo "Run ./scripts/check.sh successfully first."
    echo

    exit 1

fi

echo "Staged artefacts found."


# ============================================================
# Get Git information
# ============================================================

section "Reading commit information"

BRANCH="$(git branch --show-current)"
SHORT_COMMIT="$(git rev-parse --short HEAD)"
FULL_COMMIT="$(git rev-parse HEAD)"
COMMIT_MESSAGE="$(git log -1 --pretty=%s)"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

RUN_DIR="$ARCHIVES_DIR/${TIMESTAMP}-${SHORT_COMMIT}"

echo "Branch:         $BRANCH"
echo "Short commit:   $SHORT_COMMIT"
echo "Full commit:    $FULL_COMMIT"
echo "Commit message: $COMMIT_MESSAGE"


# ============================================================
# Create archive directory
# ============================================================

section "Creating archive directory"

mkdir -p "$RUN_DIR"


# ============================================================
# Copy staged artefacts
# ============================================================

section "Copying check artefacts"

cp -R "$ARTIFACTS_DIR/." "$RUN_DIR/"

echo "Check artefacts copied."


# ============================================================
# Create Git source archive
# ============================================================

section "Creating Git source archive"

git archive \
    --format=zip \
    --output="$RUN_DIR/repo.zip" \
    HEAD

echo "Source archive created."


# ============================================================
# Create metadata
# ============================================================

section "Creating archive metadata"

cat > "$RUN_DIR/metadata.txt" << EOF
Archive created: $(date '+%Y-%m-%d %H:%M:%S')
Branch: $BRANCH
Short commit: $SHORT_COMMIT
Full commit: $FULL_COMMIT
Commit message: $COMMIT_MESSAGE
EOF

echo "Metadata created."


# ============================================================
# Verify archive
# ============================================================

section "Verifying archive artefacts"

REQUIRED_FILES=(
    "$RUN_DIR/ruff-report.sarif"
    "$RUN_DIR/bandit-report.html"
    "$RUN_DIR/pip-audit-report.md"
    "$RUN_DIR/schema.yml"
    "$RUN_DIR/drf-spectacular-report.txt"
    "$RUN_DIR/repo.zip"
    "$RUN_DIR/metadata.txt"
)

for FILE in "${REQUIRED_FILES[@]}"; do

    if [[ ! -f "$FILE" ]]; then

        echo
        echo "ERROR: Required archive artefact is missing:"
        echo
        echo "  $FILE"
        echo

        exit 1

    fi

done


if [[ ! -d "$RUN_DIR/coverage" ]]; then

    echo
    echo "ERROR: Coverage directory is missing:"
    echo

    exit 1

fi


echo "All archive artefacts verified."


# ============================================================
# Success
# ============================================================

echo
echo "============================================================"
echo "ARCHIVE CREATED SUCCESSFULLY"
echo "============================================================"

echo
echo "Archive location:"
echo
echo "  $RUN_DIR"
echo

echo "Contents:"
echo "  repo.zip"
echo "  metadata.txt"
echo "  ruff-report.sarif"
echo "  bandit-report.html"
echo "  pip-audit-report.md"
echo "  schema.yml"
echo "  drf-spectacular-report.txt"
echo "  coverage/index.html"
echo