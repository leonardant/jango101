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

ARCHIVE_DIR="$PROJECT_ROOT/archives"

ARCHIVE_FILE="repo-${SHORT_COMMIT}-${TIMESTAMP}.zip"

ARCHIVE_PATH="$ARCHIVE_DIR/$ARCHIVE_FILE"


# ============================================================
# Create archive directory
# ============================================================

section "Preparing archive directory"

mkdir -p "$ARCHIVE_DIR"

echo "Archive directory: $ARCHIVE_DIR"


# ============================================================
# Create Git archive
# ============================================================

section "Creating Git archive"

git archive \
    --format=zip \
    --output="$ARCHIVE_PATH" \
    HEAD


# ============================================================
# Verify archive
# ============================================================

section "Verifying archive"

if [[ ! -f "$ARCHIVE_PATH" ]]; then
    echo "ERROR: Archive was not created."
    exit 1
fi

ARCHIVE_SIZE="$(du -h "$ARCHIVE_PATH" | cut -f1)"

echo "Archive created successfully"
echo "Archive size: $ARCHIVE_SIZE"


# ============================================================
# Success
# ============================================================

echo
echo "============================================================"
echo "ARCHIVE CREATED SUCCESSFULLY"
echo "============================================================"

echo
echo "Commit:  $SHORT_COMMIT"
echo "Branch:  $BRANCH"
echo "Archive: $ARCHIVE_PATH"
echo