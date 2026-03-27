SHELL := /bin/bash

.PHONY: help preflight preflight-static ci-smoke security-scan release-bundle release-acceptance start stop baseline faults acceptance acceptance-enhanced acceptance-step30 acceptance-step24 acceptance-legacy typecheck build step30

help:
	@echo "Smart Parking common commands"
	@echo "  make preflight          # check local prerequisites and env templates"
	@echo "  make preflight-static   # validate repo/env templates without requiring Docker daemon"
	@echo "  make ci-smoke           # run static preflight + OpenAPI + Step33 CI smoke gate"
	@echo "  make security-scan      # run Step35 security scan and config hardening gate"
	@echo "  make release-bundle     # generate a versioned release bundle under deliverables/bundles"
	@echo "  make release-acceptance # run Step36 release acceptance"
	@echo "  make start              # start services + frontend business preview"
	@echo "  make stop               # stop services + preview"
	@echo "  make baseline           # run baseline gates"
	@echo "  make faults             # run fault injection sequence"
	@echo "  make acceptance         # run default Step36 release acceptance"
	@echo "  make acceptance-step30  # run historical Step30 enhanced acceptance"
	@echo "  make acceptance-step24  # run historical Step24 baseline acceptance"
	@echo "  make acceptance-legacy  # run historical Step18 legacy acceptance"
	@echo "  make typecheck          # frontend typecheck"
	@echo "  make build              # frontend build"
	@echo "  make step30             # historical Step30 enhanced acceptance shortcut"

preflight:
	./scripts/preflight_check.sh

preflight-static:
	./scripts/preflight_check.sh --static

ci-smoke: preflight-static
	python3 scripts/validate_openapi.py --spec openapi/smart-parking.yaml
	python3 scripts/test_step33_ci_smoke.py

security-scan:
	python3 scripts/security_scan.py
	python3 scripts/test_step35_security_config.py

release-bundle:
	./scripts/create_release_bundle.sh

release-acceptance:
	python3 scripts/test_step36_release_acceptance.py

start:
	./scripts/defense_demo.sh start

stop:
	./scripts/defense_demo.sh stop

baseline:
	./scripts/defense_demo.sh baseline

faults:
	./scripts/defense_demo.sh faults

acceptance:
	./scripts/defense_demo.sh acceptance

acceptance-enhanced:
	./scripts/defense_demo.sh acceptance-enhanced

acceptance-step30:
	./scripts/defense_demo.sh acceptance-step30

acceptance-step24:
	./scripts/defense_demo.sh acceptance-step24

acceptance-legacy:
	./scripts/defense_demo.sh acceptance-legacy

typecheck:
	cd apps/frontend && npm run typecheck

build:
	cd apps/frontend && npm run build

step30: acceptance-step30
