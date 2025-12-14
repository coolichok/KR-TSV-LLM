# Документация по API Code Explainer

## Обзор

Code Explainer API — RESTful-сервис, который предоставляет AI-объяснения фрагментов кода. Для анализа используется модель CodeLlama 70B, формирующая обучающие пояснения.

## Базовый URL

```
http://localhost:8000
```

## Аутентификация

Сейчас API не требует аутентификации. В продакшн-среде рекомендуется добавить проверку API-ключей.

## Эндпойнты

### 1. Объяснение кода

#### POST /code/explain

Получить объяснение для фрагмента кода с помощью LLM.

**Тело запроса:**
```json
{
  "code_snippet": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "language": "python",
  "complexity_level": "intermediate"
}
```

**Ответ:**
```json
{
  "success": true,
  "explanation": "## Python Code Analysis...",
  "language": "python",
  "complexity_level": "intermediate",
  "code_summary": {
    "purpose": "Mathematical calculation",
    "complexity": "Moderate",
    "key_functions": ["fibonacci"]
  },
  "validation_info": {
    "is_valid": true,
    "errors": [],
    "warnings": [],
    "stats": {
      "lines": 4,
      "characters": 89,
      "non_empty_lines": 4,
      "comment_lines": 0
    }
  },
  "processing_time": 2.34
}
```

### 2. Поддерживаемые языки

#### GET /code/languages

Получить список поддерживаемых языков программирования.

**Ответ:**
```json
{
  "success": true,
  "languages": [
    {
      "name": "Python",
      "value": "python",
      "icon": "🐍"
    }
  ],
  "total_count": 14
}
```

### 3. Уровни сложности

#### GET /code/complexity-levels

Получить доступные уровни сложности объяснений.

**Ответ:**
```json
{
  "success": true,
  "complexity_levels": [
    {
      "name": "Beginner",
      "value": "beginner",
      "description": "Simple explanations suitable for new programmers",
      "icon": "🌱"
    }
  ]
}
```

### 4. Управление историей

#### GET /history/explanations

Получить постраничный список объяснений с фильтрами.

**Параметры запроса:**
- `language` (опционально): фильтр по языку программирования;
- `complexity_level` (опционально): фильтр по уровню сложности;
- `is_favorite` (опционально): фильтр по признаку избранного;
- `search_term` (опционально): поиск по коду или объяснению;
- `page` (по умолчанию: 1): номер страницы;
- `per_page` (по умолчанию: 10): количество элементов на странице.

**Ответ:**
```json
{
  "success": true,
  "explanations": [
    {
      "id": 1,
      "code_snippet": "def fibonacci(n):...",
      "language": "python",
      "explanation": "## Python Code Analysis...",
      "complexity_level": "intermediate",
      "created_at": "2024-01-15T10:30:00",
      "is_favorite": false,
      "tags": ""
    }
  ],
  "total_count": 25,
  "page": 1,
  "per_page": 10,
  "total_pages": 3
}
```

#### GET /history/explanations/{id}

Получить конкретное объяснение по ID.

**Ответ:**
```json
{
  "success": true,
  "explanation": {
    "id": 1,
    "code_snippet": "def fibonacci(n):...",
    "language": "python",
    "explanation": "## Python Code Analysis...",
    "complexity_level": "intermediate",
    "created_at": "2024-01-15T10:30:00",
    "is_favorite": false,
    "tags": ""
  }
}
```

#### POST /history/explanations/{id}/favorite

Изменить признак избранного для объяснения.

**Тело запроса:**
```json
{
  "explanation_id": 1,
  "is_favorite": true
}
```

**Ответ:**
```json
{
  "success": true,
  "message": "Explanation added to favorites",
  "explanation": { ... }
}
```

#### DELETE /history/explanations/{id}

Удалить объяснение из истории.

**Ответ:**
```json
{
  "success": true,
  "message": "Explanation deleted successfully"
}
```

### 5. Статистика

#### GET /history/stats

Получить статистику по объяснениям.

**Ответ:**
```json
{
  "success": true,
  "stats": {
    "total_explanations": 25,
    "favorite_explanations": 5,
    "language_distribution": [
      {
        "language": "python",
        "count": 15
      }
    ],
    "complexity_distribution": [
      {
        "complexity": "intermediate",
        "count": 18
      }
    ]
  }
}
```

### 6. Проверка состояния

#### GET /health

Проверка состояния сервиса.

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": 1705317600,
  "version": "1.0.0",
  "llm_service_status": "healthy",
  "database_status": "healthy"
}
```

## Ошибки

Все эндпойнты возвращают единый формат ошибки:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Типовые коды ответов:
- `200`: успех;
- `400`: некорректный запрос (невалидные входные данные);
- `404`: ресурс не найден;
- `500`: внутренняя ошибка сервера.

## Ограничение частоты запросов

Ограничения не настроены. В продакшене рекомендуется добавить rate limiting для защиты от злоупотреблений.

## Примеры использования

### Пример на Python

```python
import requests

# Объяснение кода
response = requests.post('http://localhost:8000/code/explain', json={
    'code_snippet': 'print("Hello, World!")',
    'language': 'python',
    'complexity_level': 'beginner'
})

explanation = response.json()
print(explanation['explanation'])

# История объяснений
response = requests.get('http://localhost:8000/history/explanations')
history = response.json()
for item in history['explanations']:
    print(f"ID: {item['id']}, Language: {item['language']}")
```

### Пример на JavaScript

```javascript
// Объяснение кода
const explainResponse = await fetch('http://localhost:8000/code/explain', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        code_snippet: 'console.log("Hello, World!")',
        language: 'javascript',
        complexity_level: 'beginner'
    })
});

const explanation = await explainResponse.json();
console.log(explanation.explanation);

// История объяснений
const historyResponse = await fetch('http://localhost:8000/history/explanations');
const history = await historyResponse.json();
history.explanations.forEach(item => {
    console.log(`ID: ${item.id}, Language: ${item.language}`);
});
```

## Тестирование

Используйте интерактивную документацию Swagger:

```
http://localhost:8000/docs
```

Через этот интерфейс можно изучить и протестировать все эндпойнты API.

