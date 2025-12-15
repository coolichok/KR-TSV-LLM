# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    USE_MOCK_LLM=true

# Копируем файл зависимостей
COPY backend/requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Создаем директорию для базы данных
RUN mkdir -p /app/backend/data

# Открываем порт 8000
EXPOSE 8000

# Команда запуска приложения
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]

