# Re4ctoR public entropy API container

FROM python:3.10-slim

WORKDIR /app

# Залежності для API
COPY api/requirements.txt /app/api/requirements.txt
RUN pip install --no-cache-dir -r /app/api/requirements.txt

# Код API
COPY api /app/api

# Всередині контейнера сервіс слухає порт 8081
EXPOSE 8081

# Запускаємо uvicorn
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8081"]
