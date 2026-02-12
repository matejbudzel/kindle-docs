#!/usr/bin/env bash
set -euo pipefail

# Setup/maintenance helper for web-based Codex environments.
# - Installs OS dependencies used by CI conversion workflow.
# - Optionally installs/pins a Python version with uv while internet is available.
# - Verifies tool availability at the end.

PYTHON_VERSION="${PYTHON_VERSION:-3.12}"
INSTALL_PYTHON="${INSTALL_PYTHON:-1}"

log() {
  printf '[setup] %s\n' "$*"
}

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

run_root() {
  if have_cmd sudo; then
    sudo "$@"
  else
    "$@"
  fi
}

install_apt_deps() {
  if ! have_cmd apt-get; then
    log "apt-get not found; skipping OS package installation"
    return 0
  fi

  export DEBIAN_FRONTEND=noninteractive
  log "Updating apt metadata"
  run_root apt-get update

  log "Installing required OS packages (pandoc, calibre, python tooling, unzip)"
  run_root apt-get install -y --no-install-recommends \
    pandoc \
    calibre \
    python3 \
    python3-venv \
    python3-pip \
    unzip \
    ca-certificates \
    curl
}

install_uv_if_missing() {
  if have_cmd uv; then
    return 0
  fi

  if ! have_cmd curl; then
    log "curl not available; cannot install uv"
    return 1
  fi

  log "Installing uv (user-local)"
  curl -LsSf https://astral.sh/uv/install.sh | sh

  if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
  fi

  have_cmd uv
}

install_pinned_python() {
  if [ "$INSTALL_PYTHON" != "1" ]; then
    log "INSTALL_PYTHON=$INSTALL_PYTHON, skipping Python pin/install"
    return 0
  fi

  if ! install_uv_if_missing; then
    log "uv installation unavailable; keeping system Python"
    return 0
  fi

  log "Installing/pinning Python ${PYTHON_VERSION} with uv"
  uv python install "$PYTHON_VERSION"

  log "Creating/refreshing .venv using Python ${PYTHON_VERSION}"
  uv venv --python "$PYTHON_VERSION" .venv
}

verify_tools() {
  log "Verifying installed tools"

  for bin in pandoc ebook-convert python3; do
    if have_cmd "$bin"; then
      "$bin" --version | head -n 1
    else
      log "ERROR: missing required tool: $bin"
      return 1
    fi
  done

  if [ -d .venv ]; then
    log "Virtual environment detected at .venv"
  fi
}

main() {
  log "Starting environment setup"
  install_apt_deps
  install_pinned_python
  verify_tools
  log "Setup complete"
}

main "$@"
