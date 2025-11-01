# ---- Makefile (CI-safe) ----
.PHONY: r4cat

# Якщо йдемо в CI — нічого не будуємо і повертаємо успіх (exit 0)
r4cat:
	@echo "r4cat: nothing to build in CI (noop)"
	@:
# Локальний підйом сервісів
dev-up:
ifndef CI
	docker compose up -d
else
	@echo "CI detected => skip docker compose (dev-up)"
	@true
endif

# Локальне вимкнення сервісів
dev-down:
ifndef CI
	docker compose down
else
	@echo "CI detected => skip docker compose (dev-down)"
	@true
endif

# Явний "успішний" таргет (може знадобитись у workflow)
ci-ok:
	@echo "CI OK"
	@true
# ---- end ----
