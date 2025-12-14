# Code Explainer — инструкция по настройке

## Предварительные требования

- Python 3.8 или новее
- pip (пакетный менеджер Python)
- Git (для клонирования репозитория)

## Установка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd code-explainer
```

### 2. Настройка окружения Python

Рекомендуется использовать виртуальное окружение:

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 4. Запуск приложения

```bash
# Запуск сервера FastAPI
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

API будет доступно по адресу `http://localhost:8000`.

## Структура проекта

```
code-explainer/
├── backend/
│   ├── app.py              # Основное приложение FastAPI
│   ├── models.py           # Модели Pydantic
│   ├── database.py         # Настройка базы данных
│   ├── api/
│   │   ├── code.py         # Эндпойнты объяснения кода
│   │   └── history.py      # Эндпойнты истории объяснений
│   ├── services/
│   │   ├── llm_service.py  # Интеграция с LLM
│   │   └── code_analyzer.py # Утилиты анализа кода
│   └── requirements.txt    # Зависимости Python
├── frontend/
│   ├── index.html          # Основной интерфейс
│   ├── history.html        # Страница истории
│   ├── main.js             # JavaScript-файлы фронтенда
│   └── resources/          # Статические ресурсы
├── docs/
│   ├── API.md              # Документация по API
│   └── setup.md            # Этот файл
└── tests/
    └── test_api.py         # Тесты API
```

## Конфигурация

### Переменные окружения

Приложение можно настраивать через переменные окружения:

```bash
# Использовать мок-сервис LLM в режиме разработки (по умолчанию: true)
export USE_MOCK_LLM=true

# Путь к базе данных (по умолчанию: backend/code_explainer.db)
export DATABASE_PATH=/path/to/database.db
```

### База данных

По умолчанию используется SQLite. Файл базы данных создаётся автоматически при первом запуске приложения.

Расположение базы: `backend/code_explainer.db`.

## Использование

### 1. Запуск бэкенда

```bash
cd backend
uvicorn app:app --reload
```

### 2. Доступ к веб-интерфейсу

Откройте браузер и перейдите по адресам:
- Основной интерфейс: `http://localhost:8000/static/index.html`
- Страница истории: `http://localhost:8000/static/history.html`
- Документация API: `http://localhost:8000/docs`

### 3. Работа с приложением

1. **Объяснение кода:**
   - Вставьте код в редактор.
   - Выберите язык программирования (или используйте автоопределение).
   - Укажите уровень сложности.
   - Нажмите «Explain Code».

2. **Просмотр истории:**
   - Перейдите на страницу истории.
   - Отфильтруйте по языку, сложности или строке поиска.
   - Просматривайте, добавляйте в избранное или удаляйте объяснения.

## Тестирование API

### Через Swagger UI

Перейдите на `http://localhost:8000/docs`, чтобы открыть интерактивную документацию.

### Через curl

```bash
# Запрос объяснения кода
curl -X POST "http://localhost:8000/code/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "code_snippet": "print(\'Hello, World!\')",
    "language": "python",
    "complexity_level": "beginner"
  }'

# Получение истории
curl "http://localhost:8000/history/explanations"
```

## Разработка

### Добавление новых функций

1. **Бэкенд:**
   - Добавляйте эндпойнты в директории `api/`.
   - Обновляйте модели в `models.py`.
   - Размещайте бизнес-логику в `services/`.

2. **Фронтенд:**
   - Изменяйте HTML в `frontend/`.
   - Добавляйте JS-функциональность в `main.js`.

### Тестирование

Запуск набора тестов:

```bash
cd backend
pytest ../tests/
```

## Устранение неполадок

### Типовые проблемы

1. **Порт уже занят:**
   ```bash
   # Сменить порт
   uvicorn app:app --reload --port 8001
   ```

2. **Ошибки CORS:**
   - Проверьте настройки CORS в `app.py`.
   - Убедитесь, что фронтенд обращается по корректному URL.

3. **Ошибки базы данных:**
   - Удалите файл базы и перезапустите приложение.
   - Проверьте права доступа к каталогу базы.

4. **Ошибки LLM-сервиса:**
   - По умолчанию используется мок-сервис LLM.
   - Установите `USE_MOCK_LLM=false`, чтобы подключить реальную модель (требуется API-ключ).

### Режим отладки

Включение расширенного логирования:

```python
# В app.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Продуктивный деплой

### Использование Docker

Создайте `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Сборка и запуск:

```bash
docker build -t code-explainer .
docker run -p 8000:8000 code-explainer
```

### Использование Gunicorn

Развёртывание с несколькими рабочими процессами:

```bash
pip install gunicorn
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Безопасность

1. **Аутентификация API:** в продакшене добавьте проверку API-ключей.
2. **Ограничение частоты:** настройте rate limiting для защиты от злоупотреблений.
3. **Валидация данных:** все входные данные валидируются через модели Pydantic.
4. **SQL-инъекции:** использование SQLAlchemy предотвращает инъекции.
5. **CORS:** настройте корректные CORS-политики для продакшена.

## Поддержка

По вопросам и проблемам:

1. Проверьте раздел устранения неполадок выше.
2. Ознакомьтесь с документацией API на `/docs`.
3. Изучите логи приложения.
4. Создайте issue в репозитории.

## Лицензия

Проект является open source. Подробности в файле LICENSE.

