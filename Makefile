# ---- Makefile (CI-safe) ----
.PHONY: all r4cat dev-up dev-down ci-ok

# default target: нічого не будуємо для r4cat у CI
all: r4cat

r4cat:
	@echo "r4cat: nothing to build in CI (noop)"
	@true

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
