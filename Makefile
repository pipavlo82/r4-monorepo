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
