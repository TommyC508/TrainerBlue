#!/usr/bin/env bash
set -euo pipefail

# Runs a local Pokémon Showdown server (official battle engine).
# Default port is 8000.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PS_DIR="$ROOT_DIR/external/pokemon-showdown"
PORT="${1:-8000}"

if [[ ! -d "$PS_DIR" ]]; then
  echo "ERROR: Pokémon Showdown submodule not found at: $PS_DIR" >&2
  echo "Did you run: git submodule update --init --recursive" >&2
  exit 1
fi

cd "$PS_DIR"

# The start command will auto-build unless --skip-build is provided.
# We keep --skip-build to avoid surprising rebuilds in tight loops.
exec ./pokemon-showdown start --skip-build "$PORT"
