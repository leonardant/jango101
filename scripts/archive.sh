#!/usr/bin/env bash

set -euo pipefail


# ============================================================
# Locate repository root
# ============================================================

PROJECT_ROOT="$(git rev-parse --show-toplevel)"

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
# Create archive information
# ============================================================

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

ARCHIVES_DIR="$PROJECT_ROOT/archives"

RUN_DIR="$ARCHIVES_DIR/${TIMESTAMP}-${SHORT_COMMIT}"

ARCHIVE_FILE="$RUN_DIR/repo.zip"


# ============================================================
# Create archive directory
# ============================================================

section "Preparing archive directory"

mkdir -p "$RUN_DIR"

echo "Archive directory:"
echo "  $RUN_DIR"


# ============================================================
# Create Git archive
# ============================================================

section "Creating Git archive"

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
echo "Archive folder:"
echo "  $RUN_DIR"
echo

echo "Contents:"
echo "  repo.zip"
echo "  metadata.txt"
echo