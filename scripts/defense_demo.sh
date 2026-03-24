#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/infra/docker-compose.yml"
FRONTEND_DIR="$ROOT_DIR/apps/frontend"
FRONTEND_PID_FILE="/tmp/smart_parking_frontend_preview.pid"
if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
  PYTHON_BIN_DEFAULT="$ROOT_DIR/.venv/bin/python"
else
  PYTHON_BIN_DEFAULT="python3"
fi
PYTHON_BIN="${PYTHON_BIN:-$PYTHON_BIN_DEFAULT}"

compose() {
  docker compose -f "$COMPOSE_FILE" "$@"
}

wait_http() {
  local url="$1"
  local retries="${2:-120}"
  local sleep_s="${3:-1}"
  local i
  for i in $(seq 1 "$retries"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$sleep_s"
  done
  echo "[defense-demo] timeout waiting for $url" >&2
  return 1
}

stop_frontend_preview() {
  if [[ -f "$FRONTEND_PID_FILE" ]]; then
    local pid
    pid="$(cat "$FRONTEND_PID_FILE" || true)"
    if [[ -n "$pid" ]] && kill -0 "$pid" >/dev/null 2>&1; then
      kill "$pid" >/dev/null 2>&1 || true
      wait "$pid" 2>/dev/null || true
    fi
    rm -f "$FRONTEND_PID_FILE"
  fi
}

start_frontend_preview() {
  if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    echo "[defense-demo] frontend dependencies missing: cd apps/frontend && npm install" >&2
    return 1
  fi

  stop_frontend_preview

  echo "[defense-demo] building frontend business UI..."
  (
    cd "$FRONTEND_DIR"
    npm run build >/tmp/smart_parking_frontend_build.log 2>&1
  )

  echo "[defense-demo] starting frontend preview..."
  (
    cd "$FRONTEND_DIR"
    nohup npm run preview >/tmp/smart_parking_frontend_preview.log 2>&1 &
    echo $! > "$FRONTEND_PID_FILE"
  )

  wait_http "http://localhost:4173" 120 1
}

start_stack() {
  echo "[defense-demo] starting services..."
  compose up -d gateway-service parking-service model-service realtime-service rabbitmq prometheus grafana mysql redis

  wait_http "http://localhost:8080/actuator/health"
  wait_http "http://localhost:9090/-/ready"
  wait_http "http://localhost:15672" 120 1 || true

  local i
  for i in $(seq 1 10); do
    curl -fsS "http://localhost:8080/api/v1/admin/realtime/status" >/dev/null 2>&1 || true
    sleep 0.2
  done

  start_frontend_preview

  echo "[defense-demo] stack is ready"
  echo "[defense-demo] Owner UI: http://localhost:4173/owner/dashboard"
  echo "[defense-demo] Admin UI: http://localhost:4173/admin/monitor"
  echo "[defense-demo] Gateway health: http://localhost:8080/actuator/health"
  echo "[defense-demo] RabbitMQ UI (ops): http://localhost:15672 (guest/guest)"
  echo "[defense-demo] Grafana UI (ops): http://localhost:13000 (admin/admin)"
}

stop_stack() {
  echo "[defense-demo] stopping frontend preview..."
  stop_frontend_preview
  echo "[defense-demo] stopping services..."
  compose down
  echo "[defense-demo] stack stopped"
}

run_baseline() {
  echo "[defense-demo] running baseline checks..."
  "$PYTHON_BIN" "$ROOT_DIR/scripts/validate_openapi.py" --spec "$ROOT_DIR/openapi/smart-parking.yaml"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step4_consistency.py"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step5_model_core.py"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step19b_hungarian.py"
  echo "[defense-demo] baseline checks passed"
}

run_faults() {
  echo "[defense-demo] Step6 fallback fault injection..."
  compose stop model-service
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step6_resilience.py"
  compose up -d model-service
  sleep 2

  echo "[defense-demo] Step7 MQ retry + DLQ fault injection..."
  "$PYTHON_BIN" "$ROOT_DIR/scripts/setup_rabbitmq.py"
  "$PYTHON_BIN" "$ROOT_DIR/services/dispatch_worker.py" \
    --api http://localhost:15672/api \
    --user guest \
    --password guest \
    --max-retry 2 \
    --max-cycles 100 &
  local worker_pid=$!
  sleep 2
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step7_mq_reliability.py"
  wait "$worker_pid" || true

  echo "[defense-demo] Step8 realtime fallback fault injection..."
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step8_realtime_channel.py" --mode realtime
  compose stop realtime-service
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step8_realtime_channel.py" --mode fallback
  compose up -d realtime-service

  echo "[defense-demo] Step9 observability fault transition..."
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step9_observability.py" --mode baseline
  compose stop model-service
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step9_observability.py" --mode fault
  compose up -d model-service

  echo "[defense-demo] fault-injection sequence passed"
}

run_acceptance() {
  echo "[defense-demo] running Step30 enhanced acceptance..."
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step30_enhanced_acceptance.py"
  echo "[defense-demo] enhanced acceptance passed"
}

run_acceptance_enhanced() {
  run_acceptance
}

run_acceptance_step24() {
  echo "[defense-demo] running Step24 baseline acceptance..."
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step24_full_acceptance.py"
  echo "[defense-demo] Step24 baseline acceptance passed"
}

run_acceptance_legacy() {
  echo "[defense-demo] running Step18 legacy acceptance..."
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step18_full_acceptance.py"
  echo "[defense-demo] legacy acceptance passed"
}

run_full() {
  start_stack
  run_baseline
  run_faults
  run_acceptance
  stop_stack
  echo "[defense-demo] full demo run passed"
}

run_full_enhanced() {
  start_stack
  run_baseline
  run_faults
  run_acceptance
  run_acceptance_enhanced
  stop_stack
  echo "[defense-demo] full enhanced demo run passed"
}

usage() {
  cat <<USAGE
Usage: ./scripts/defense_demo.sh <command>

Commands:
  start               Start backend stack + frontend business preview
  baseline            Run contract + Step4 + Step5 + Step19B baseline checks
  faults              Run Step6/7/8/9 fault-injection sequence
  acceptance          Run default Step30 enhanced acceptance gates
  acceptance-enhanced Run Step30 enhanced acceptance gates (alias)
  acceptance-step24   Run historical Step24 full acceptance gates
  acceptance-legacy   Run Step18 legacy acceptance gates
  full                Run start + baseline + faults + acceptance + stop
  full-enhanced       Run start + baseline + faults + acceptance + stop (alias)
  stop                Stop and clean stack
USAGE
}

main() {
  if [[ "$#" -lt 1 ]]; then
    usage
    exit 1
  fi

  case "$1" in
    start)
      start_stack
      ;;
    baseline)
      run_baseline
      ;;
    faults)
      run_faults
      ;;
    acceptance)
      run_acceptance
      ;;
    acceptance-enhanced)
      run_acceptance_enhanced
      ;;
    acceptance-step24)
      run_acceptance_step24
      ;;
    acceptance-legacy)
      run_acceptance_legacy
      ;;
    full)
      run_full
      ;;
    full-enhanced)
      run_full_enhanced
      ;;
    stop)
      stop_stack
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
