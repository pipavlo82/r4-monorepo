# ===== base image & deps (ваш існуючий докерфайл зверху залишається) =====
# ... ваші шари до етапу копіювання re4_dump ...

# --- Sealed core binary (stub by default) ---
RUN mkdir -p /app/core/bin
# 1) завжди кладемо stub, щоб CI/ком’юніті-збірки будувались
COPY docker/stubs/re4_dump /app/core/bin/re4_dump

# 2) якщо передали build-arg з шляхом до реального core у контексті — перетремо stub
ARG R4_CORE_BIN=""
COPY ${R4_CORE_BIN} /app/core/bin/re4_dump 2>/dev/null || true

# 3) права
RUN chmod +x /app/core/bin/re4_dump

# ===== решта вашого Dockerfile нижче (COPY коду, запуск тощо) =====
# EXPOSE 8080 8081
# CMD ["python", "-m", "uvicorn", ...]
