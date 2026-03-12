#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/infra/docker-compose.yml"
PYTHON_BIN_DEFAULT="/Users/yanchen/PycharmProjects/quant-value-regression/.venv/bin/python"
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

start_stack() {
  echo "[defense-demo] starting services..."
  compose up -d gateway-service parking-service model-service realtime-service rabbitmq prometheus grafana

  wait_http "http://localhost:8080/actuator/health"
  wait_http "http://localhost:15672/api/overview" 120 1 || true
  wait_http "http://localhost:9090/-/ready"

  # Warm up gateway-to-parking connections to reduce cold-start jitter.
  local i
  for i in $(seq 1 10); do
    curl -fsS "http://localhost:8080/api/v1/admin/realtime/status" >/dev/null 2>&1 || true
    sleep 0.2
  done
  echo "[defense-demo] stack is ready"
}

stop_stack() {
  echo "[defense-demo] stopping services..."
  compose down
  echo "[defense-demo] stack stopped"
}

run_baseline() {
  echo "[defense-demo] running baseline checks..."
  "$PYTHON_BIN" "$ROOT_DIR/scripts/validate_openapi.py" --spec "$ROOT_DIR/openapi/smart-parking.yaml"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step4_consistency.py"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/test_step5_model_core.py"
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

run_full() {
  start_stack
  run_baseline
  run_faults
  stop_stack
  echo "[defense-demo] full demo run passed"
}

usage() {
  cat <<USAGE
Usage: ./scripts/defense_demo.sh <command>

Commands:
  start      Start demo stack and warm up routes
  baseline   Run contract + Step4 + Step5 baseline checks
  faults     Run Step6/7/8/9 fault-injection sequence
  full       Run start + baseline + faults + stop
  stop       Stop and clean stack
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
    full)
      run_full
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
