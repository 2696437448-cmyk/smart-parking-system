#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/apps/frontend"
PYTHON_BIN="${PYTHON_BIN:-python3}"
STRICT_RUNTIME=1
FAILURES=()
WARNINGS=()

if [[ "${1:-}" == "--static" ]]; then
  STRICT_RUNTIME=0
fi

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

add_failure() {
  FAILURES+=("$1")
}

add_warning() {
  WARNINGS+=("$1")
}

check_file() {
  local path="$1"
  local label="$2"
  if [[ ! -f "$path" ]]; then
    add_failure "$label missing: $path"
  fi
}

check_dir() {
  local path="$1"
  local label="$2"
  if [[ ! -d "$path" ]]; then
    add_failure "$label missing: $path"
  fi
}

env_value() {
  local file="$1"
  local key="$2"
  awk -F= -v target="$key" '$1 == target {print substr($0, index($0, "=") + 1)}' "$file" | tail -n 1
}

if ! has_cmd docker; then
  add_failure "docker command not found"
elif [[ "$STRICT_RUNTIME" -eq 1 ]] && ! docker info >/dev/null 2>&1; then
  add_failure "docker is installed but Docker Desktop/daemon is not ready"
elif [[ "$STRICT_RUNTIME" -eq 0 ]] && ! docker info >/dev/null 2>&1; then
  add_warning "docker daemon not ready; strict preflight would fail"
fi

if ! has_cmd "$PYTHON_BIN"; then
  add_failure "python runtime not found: $PYTHON_BIN"
fi

if ! has_cmd node; then
  add_failure "node command not found"
fi

if ! has_cmd npm; then
  add_failure "npm command not found"
fi

if ! has_cmd make; then
  add_warning "make command not found; use scripts directly instead"
fi

check_file "$ROOT_DIR/.env.example" "root env template"
check_file "$ROOT_DIR/README.md" "README"
check_file "$ROOT_DIR/scripts/defense_demo.sh" "demo script"
check_file "$ROOT_DIR/openapi/smart-parking.yaml" "OpenAPI spec"
check_file "$FRONTEND_DIR/.env.example" "frontend env template"
check_file "$ROOT_DIR/Makefile" "Makefile"
check_dir "$ROOT_DIR/infra" "infra directory"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  add_warning "root .env not found; compose will use defaults from docker-compose/.env.example"
else
  for key in MYSQL_ROOT_PASSWORD MYSQL_PASSWORD RABBIT_PASS RABBITMQ_DEFAULT_PASS GF_ADMIN_PASSWORD; do
    value="$(env_value "$ROOT_DIR/.env" "$key")"
    case "$value" in
      root|sp_pass|guest|admin)
        add_warning "root .env retains demo default for $key; rotate before non-demo usage"
        ;;
    esac
  done
fi

if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  add_warning "frontend node_modules missing; run 'cd apps/frontend && npm install'"
fi

if [[ ! -f "$FRONTEND_DIR/.env.local" ]]; then
  add_warning "apps/frontend/.env.local not found; Vite will fall back to built-in localhost defaults"
fi

echo "[preflight] root=$ROOT_DIR"
echo "[preflight] python=$PYTHON_BIN"
echo "[preflight] mode=$([[ "$STRICT_RUNTIME" -eq 1 ]] && echo strict || echo static)"

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
  echo "[preflight] warnings:"
  for item in "${WARNINGS[@]}"; do
    echo "  - $item"
  done
fi

if [[ ${#FAILURES[@]} -gt 0 ]]; then
  echo "[preflight] failures:"
  for item in "${FAILURES[@]}"; do
    echo "  - $item"
  done
  echo "STEP32_PREFLIGHT_FAIL"
  exit 1
fi

echo "STEP32_PREFLIGHT_PASS"
