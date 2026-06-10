#!/usr/bin/env bash
set -euo pipefail
if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <git-remote-url>"
  echo "Examples: git@github.com:username/repo.git or https://github.com/username/repo.git"
  exit 2
fi
REMOTE_URL="$1"
git remote add origin "$REMOTE_URL"
git branch -M main || true
git push -u origin main
