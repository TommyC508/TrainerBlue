#!/usr/bin/env bash
set -euo pipefail

# Installs deps + builds the official Pokémon Showdown submodule.
# This is required for the CLI tools (including simulate-battle) and for running a local server.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PS_DIR="$ROOT_DIR/external/pokemon-showdown"

if [[ ! -d "$PS_DIR" ]]; then
  echo "ERROR: Pokémon Showdown submodule not found at: $PS_DIR" >&2
  echo "Did you run: git submodule update --init --recursive" >&2
  exit 1
fi

cd "$PS_DIR"

echo "[setup_showdown] Installing dependencies (omit optional native deps)..."
npm ci --omit=optional

echo "[setup_showdown] Building Pokémon Showdown..."
npm run build

echo "[setup_showdown] Done. You can now run: scripts/run_showdown_server.sh"
