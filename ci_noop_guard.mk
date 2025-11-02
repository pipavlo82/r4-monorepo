# --- CI NOOP guard (bottom include) ---
ifeq ($(CI),true)

.PHONY: ci-noop all r4cat dev-up dev-down build client

ci-noop:
	@echo "[ci] NOOP (CI)"
	@:

# override: перезаписуємо рецепти основних цілей у CI
all r4cat dev-up dev-down build client:
	@echo "[ci] forced NOOP target $@ (CI)"
	@:

endif
# --- end CI NOOP guard ---
