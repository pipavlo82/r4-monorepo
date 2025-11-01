PORT ?= 18080

run:
	docker rm -f r4test 2>/dev/null || true
	printf "API_KEY=demo\nRNG_BIN=/app/core/bin/re4_dump\n" > .env.ci
	docker run -d --name r4test -p $(PORT):8080 --entrypoint "" --env-file ./.env.ci \
	  r4-ci-stub:latest sh -lc 'exec python -m uvicorn api.main:app --host 0.0.0.0 --port 8080'

probe:
	curl -s "http://127.0.0.1:$(PORT)/version" && echo
	curl -s "http://127.0.0.1:$(PORT)/random?n=16&fmt=hex&key=demo" && echo
	curl -s -H "X-API-Key: demo" "http://127.0.0.1:$(PORT)/random?n=16&fmt=hex" && echo

logs:
	docker logs --tail=100 r4test

down:
	docker rm -f r4test 2>/dev/null || true
