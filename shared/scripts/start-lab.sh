#!/usr/bin/env bash
# start-lab.sh — create a fresh, self-contained working repository for one lab.
#
# Usage:  bash shared/scripts/start-lab.sh <lab-folder> <target-folder>
# Example: bash shared/scripts/start-lab.sh chapter-19/lab-05-sast-codeql-semgrep ~/dt-labs/dt-lab-05
#
# What it does (nothing is sent to GitHub):
#   1. copies the shared sample application into <target>/app
#   2. overlays the lab's starter/ files (these may replace app files with a labelled insecure variant)
#   3. initialises a git repository on branch "main" and makes the first commit
# Works in Linux, macOS and Git Bash on Windows.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <lab-folder> <target-folder>" >&2
  exit 64
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LAB_DIR="${REPO_ROOT}/${1%/}"
TARGET="$2"

[[ -d "${LAB_DIR}/starter" ]] || { echo "No starter/ folder in ${LAB_DIR}" >&2; exit 66; }
[[ -e "${TARGET}" ]] && { echo "Target ${TARGET} already exists — choose a new folder." >&2; exit 73; }

mkdir -p "${TARGET}/app"
cp -R "${REPO_ROOT}/shared/sample-apps/dt-orders-api/." "${TARGET}/app/"
cp -R "${LAB_DIR}/starter/." "${TARGET}/"

cd "${TARGET}"
git init -q -b main
git add -A
git commit -q -m "Start $(basename "${LAB_DIR}") from Defending Tomorrow DevSecOps labs"
echo "Lab repository created at: ${TARGET}"
echo "Next: create an EMPTY public repository on GitHub, then run:"
echo "  git remote add origin https://github.com/<your-username>/$(basename "${TARGET}").git"
echo "  git push -u origin main"
