#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# Locate repository root
# ============================================================

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
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
# Check for uncommitted changes
# ============================================================

section "Checking working tree"

if [[ -n "$(git status --porcelain)" ]]; then

    echo
    echo "ERROR: The working tree contains uncommitted changes."
    echo
    echo "Please commit or stash your changes before creating an archive."
    echo
    echo "Current changes:"
    echo

    git status --short

    exit 1

fi

echo "Working tree is clean: OK"


# ============================================================
# Get Git information
# ============================================================

section "Reading commit information"

BRANCH="$(git branch --show-current)"
SHORT_COMMIT="$(git rev-parse --short HEAD)"
FULL_COMMIT="$(git rev-parse HEAD)"
COMMIT_MESSAGE="$(git log -1 --pretty=%s)"

echo "Branch:         $BRANCH"
echo "Short commit:   $SHORT_COMMIT"
echo "Full commit:    $FULL_COMMIT"
echo "Commit message: $COMMIT_MESSAGE"


# ============================================================
# Find latest successful check folder for this commit
# ============================================================

section "Finding successful check artefacts"

if [[ ! -d "$ARCHIVES_DIR" ]]; then
    echo "ERROR: No archives directory exists."
    echo
    echo "Run ./scripts/check.sh successfully before creating an archive."
    exit 1
fi


RUN_DIR="$(
    find "$ARCHIVES_DIR" \
        -maxdepth 1 \
        -type d \
        -name "*-${SHORT_COMMIT}" \
        -printf "%f\n" \
        | sort \
        | tail -n 1
)"


if [[ -z "$RUN_DIR" ]]; then

    echo
    echo "ERROR: No successful check archive was found for commit:"
    echo
    echo "  $SHORT_COMMIT"
    echo
    echo "Run:"
    echo
    echo "  ./scripts/check.sh"
    echo
    echo "successfully before running:"
    echo
    echo "  ./scripts/archive.sh"
    echo

    exit 1

fi


RUN_DIR="$ARCHIVES_DIR/$RUN_DIR"

echo "Using check archive folder:"
echo "  $RUN_DIR"


# ============================================================
# Verify expected check artefacts exist
# ============================================================

section "Verifying successful check artefacts"

REQUIRED_FILES=(
    "$RUN_DIR/ruff-report.sarif"
    "$RUN_DIR/bandit-report.html"
    "$RUN_DIR/pip-audit-report.md"
    "$RUN_DIR/schema.yml"
)


for FILE in "${REQUIRED_FILES[@]}"; do

    if [[ ! -f "$FILE" ]]; then

        echo "ERROR: Required check artefact is missing:"
        echo
        echo "  $FILE"
        echo

        exit 1

    fi

done


if [[ ! -d "$RUN_DIR/coverage" ]]; then

    echo "ERROR: Coverage report directory is missing:"
    echo
    echo "  $RUN_DIR/coverage"
    echo

    exit 1

fi


echo "All required check artefacts are present."


# ============================================================
# Create Git archive
# ============================================================

section "Creating Git archive"

ARCHIVE_FILE="$RUN_DIR/repo.zip"

git archive \
    --format=zip \
    --output="$ARCHIVE_FILE" \
    HEAD


# ============================================================
# Verify archive
# ============================================================

section "Verifying archive"

if [[ ! -f "$ARCHIVE_FILE" ]]; then

    echo "ERROR: Archive was not created."

    exit 1

fi


ARCHIVE_SIZE="$(du -h "$ARCHIVE_FILE" | cut -f1)"

echo "Archive created successfully."
echo "Archive size: $ARCHIVE_SIZE"


# ============================================================
# Create metadata file
# ============================================================

section "Creating archive metadata"

cat > "$RUN_DIR/metadata.txt" << EOF
Archive created: $(date '+%Y-%m-%d %H:%M:%S')
Branch: $BRANCH
Short commit: $SHORT_COMMIT
Full commit: $FULL_COMMIT
Commit message: $COMMIT_MESSAGE
EOF


echo "Metadata created:"
echo "  $RUN_DIR/metadata.txt"


# ============================================================
# Success
# ============================================================

echo
echo "============================================================"
echo "ARCHIVE CREATED SUCCESSFULLY"
echo "============================================================"

echo
echo "Complete release artefacts:"
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
echo "  coverage/"
echo