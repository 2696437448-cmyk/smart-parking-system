#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${RELEASE_OUTPUT_DIR:-$ROOT_DIR/deliverables/bundles}"
BUNDLE_LABEL="${1:-step40}"
STAMP="$(date '+%Y%m%d-%H%M%S')"
ARCHIVE_NAME="smart-parking-${BUNDLE_LABEL}-release-${STAMP}.tar.gz"
TMP_DIR="$(mktemp -d)"
PACKAGE_ROOT="$TMP_DIR/smart-parking-release"
MANIFEST_FILE="$PACKAGE_ROOT/manifest.txt"
MANIFEST_COPY="$OUTPUT_DIR/${ARCHIVE_NAME%.tar.gz}.manifest.txt"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

copy_into() {
  local rel="$1"
  mkdir -p "$PACKAGE_ROOT/$(dirname "$rel")"
  cp "$ROOT_DIR/$rel" "$PACKAGE_ROOT/$rel"
}

mkdir -p "$OUTPUT_DIR"
mkdir -p "$PACKAGE_ROOT"

FILES=(
  ".env.example"
  ".env.secure.example"
  "Makefile"
  "README.md"
  "requirements-dev.txt"
  "docs/defense_demo_runbook.md"
  "docs/security_hardening.md"
  "openapi/smart-parking.yaml"
  "scripts/defense_demo.sh"
  "scripts/preflight_check.sh"
  "scripts/security_scan.py"
  "scripts/test_step33_ci_smoke.py"
  "scripts/test_step35_security_config.py"
  "scripts/test_step36_release_acceptance.py"
  "scripts/test_step37_prompt_frontend_modernization.py"
  "scripts/test_step38_dashboard_contract_and_viewmodels.py"
  "scripts/test_step39_dashboard_hardening.py"
  "scripts/test_step40_release_acceptance.py"
  ".github/workflows/ci.yml"
  "apps/frontend/.env.example"
  "memory-bank/implementation-plan.md"
  "memory-bank/acceptance.md"
  "memory-bank/architecture.md"
  "memory-bank/gap-matrix.md"
  "memory-bank/progress.md"
  "memory-bank/project-prompt-library.md"
  "memory-bank/prompt-templates.md"
  "reports/step30_technical_acceptance.md"
  "reports/step30_gate_results.json"
  "reports/step31_execution.md"
  "reports/step32_execution.md"
  "reports/step33_execution.md"
  "reports/step34_execution.md"
  "reports/step35_execution.md"
  "reports/step37_execution.md"
  "reports/step38_execution.md"
  "reports/step39_execution.md"
  "reports/step40_technical_acceptance.md"
  "deliverables/README.md"
)

OPTIONAL_FILES=(
  "reports/step33_ci_smoke.json"
  "reports/step35_security_scan.json"
  "reports/step35_gate_results.json"
  "reports/step36_technical_acceptance.md"
  "reports/step36_gate_results.json"
  "reports/step38_gate_results.json"
  "reports/step39_gate_results.json"
  "reports/step40_gate_results.json"
)

for rel in "${FILES[@]}"; do
  copy_into "$rel"
done

for rel in "${OPTIONAL_FILES[@]}"; do
  if [[ -f "$ROOT_DIR/$rel" ]]; then
    copy_into "$rel"
  fi
done

{
  echo "bundle_label=$BUNDLE_LABEL"
  echo "generated_at=$(date '+%Y-%m-%d %H:%M:%S %Z')"
  echo "source_branch=$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
  echo "source_commit=$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
  echo "archive_name=$ARCHIVE_NAME"
  echo "included_files:"
  (
    cd "$PACKAGE_ROOT"
    find . -type f | sed 's#^\./##' | sort
  )
} > "$MANIFEST_FILE"

tar -czf "$OUTPUT_DIR/$ARCHIVE_NAME" -C "$TMP_DIR" smart-parking-release
cp "$MANIFEST_FILE" "$MANIFEST_COPY"

echo "STEP34_BUNDLE_PASS bundle=$OUTPUT_DIR/$ARCHIVE_NAME manifest=$MANIFEST_COPY"
