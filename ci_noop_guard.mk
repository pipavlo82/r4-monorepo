# --- CI NOOP guard ---
ifeq ($(CI),true)
override .DEFAULT_GOAL := ci-noop

.PHONY: ci-noop r4cat all dev-up dev-down build client

ci-noop:
	@echo "[ci] NOOP (CI)"
	@:

# Якщо викличуть будь-яку з цих цілей — теж NOOP
r4cat all dev-up dev-down build client:
	@$(MAKE) ci-noop
endif
# --- end CI NOOP guard ---
