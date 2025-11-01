.PHONY: run stop logs clean test-api

run:
	docker rm -f r4test 2>/dev/null || true
	printf "API_KEY=demo\nRNG_BIN=/app/core/bin/re4_dump\n" > .env.ci
	# 1) Зібрати community-стадію (в ній покладено stub-бінарник)
	docker build --target community -t r4-ci-stub:latest .
	# 2) Запустити
	docker run -d --name r4test -p 18080:8080 --entrypoint "" --env-file ./.env.ci \
	  r4-ci-stub:latest \
	  sh -lc 'exec python -m uvicorn api.main:app --host 0.0.0.0 --port 8080'

test-api:
	curl -s http://127.0.0.1:18080/version && echo
	curl -s "http://127.0.0.1:18080/random?n=16&fmt=hex&key=demo" && echo

stop:
	docker rm -f r4test 2>/dev/null || true

logs:
	docker logs --tail=200 -f r4test || true

clean: stop
	rm -f .env.ci
