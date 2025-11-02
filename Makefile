.PHONY: dev-up dev-down dual-json vrf-test

dev-up:
	docker compose up -d
	@for i in $$(seq 1 20); do curl -fsS http://127.0.0.1:18080/health && echo && break || sleep 0.2; done
	@for i in $$(seq 1 20); do curl -fsS http://127.0.0.1:18084/health && echo && break || sleep 0.2; done

dev-down:
	docker compose down

dual-json:
	curl -s -H "X-API-Key: demo" "http://127.0.0.1:18084/random_dual?sig=ecdsa&n=32&fmt=json" > examples/out_dual_ecdsa.json
	jq -r 'keys[]' examples/out_dual_ecdsa.json >/dev/null

vrf-test: dual-json
	cd examples/vrf-hardhat && npm ci && npx hardhat test
.PHONY: run test-api dev-up dev-down

# локальний раннер (community)
run:
	docker rm -f r4test 2>/dev/null || true
	printf "API_KEY=demo\nRNG_BIN=/app/core/bin/re4_dump\n" > .env.ci
	docker build --target community -t r4-ci-stub:latest .
	docker run -d --name r4test -p 18080:8080 --entrypoint "" --env-file ./.env.ci \
	  r4-ci-stub:latest \
	  sh -lc 'exec python -m uvicorn api.main:app --host 0.0.0.0 --port 8080'

test-api:
	@for i in $$(seq 1 20); do curl -fsS http://127.0.0.1:18080/health && echo && break || sleep 0.2; done
	curl -s "http://127.0.0.1:18080/version" && echo
	curl -s "http://127.0.0.1:18080/random?n=16&fmt=hex&key=demo" && echo
	curl -s -H "X-API-Key: demo" "http://127.0.0.1:18080/random?n=16&fmt=hex" && echo

# локальний docker compose (СКИП у CI)
dev-up:
	@if [ -n "$$CI" ]; then \
	  echo "CI detected → skip docker compose"; \
	else \
	  docker compose up -d; \
	  for i in $$(seq 1 20); do curl -fsS http://127.0.0.1:18080/health && echo && break || sleep 0.2; done; \
	  for i in $$(seq 1 20); do curl -fsS http://127.0.0.1:18084/health && echo && break || sleep 0.2; done; \
	fi

dev-down:
	@if [ -n "$$CI" ]; then echo "CI detected → skip"; else docker compose down; fi

# --- CI override: r4cat завжди noop і exit 0 ---
.PHONY: r4cat
r4cat:
	@echo "CI detected -> r4cat noop (skip docker compose)"; exit 0

# --- CI override: r4cat is NOOP (always success) ---
ifeq ($(CI),true)
.PHONY: r4cat
r4cat:
	@echo "CI detected -> r4cat noop (skip docker compose)"; true
endif

# --- CI-safe override ---
.PHONY: r4cat
r4cat:
	@echo "== r4cat =="
	@if [ -n "$$CI" ]; then \
		echo "CI detected → skip docker compose (noop)"; \
		true; \
	else \
		echo "Local build → docker compose up"; \
		docker compose up -d; \
	fi

# --- CI override: r4cat must be noop-success in CI ---
ifeq ($(CI),true)
.PHONY: r4cat
r4cat:
	@echo "CI detected -> skip docker compose (noop success)"
	@:
endif
