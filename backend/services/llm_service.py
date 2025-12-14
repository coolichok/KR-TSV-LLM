import requests
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime

class LLMService:
    def __init__(self):
        # Используем Hugging Face Inference API для CodeLlama
        self.api_url = "https://api-inference.huggingface.co/models/codellama/CodeLlama-70b-Instruct-hf"
        self.headers = {
            "Content-Type": "application/json",
        }
        # В демонстрационном режиме используем мок-сервис, если API HF недоступно
        self.use_mock = os.getenv("USE_MOCK_LLM", "true").lower() == "true"
    
    def explain_code(self, code_snippet: str, language: str, complexity_level: str = "intermediate", 
                     code_summary: Dict[str, Any] = None, validation_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Генерирует объяснение кода с помощью LLM
        """
        if self.use_mock:
            return self._mock_explanation(code_snippet, language, complexity_level, code_summary, validation_info)
        
        try:
            prompt = self._create_prompt(code_snippet, language, complexity_level)
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.1,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url, 
                headers=self.headers, 
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                explanation = result[0].get("generated_text", "")
                return {
                    "success": True,
                    "explanation": self._format_explanation(explanation),
                    "complexity_level": complexity_level,
                    "language": language
                }
            else:
                # При ошибке API переключаемся на мок-режим
                return self._mock_explanation(code_snippet, language, complexity_level, code_summary, validation_info)
                
        except Exception as e:
            print(f"Ошибка обращения к LLM API: {e}")
            return self._mock_explanation(code_snippet, language, complexity_level, code_summary, validation_info)
    
    def _create_prompt(self, code_snippet: str, language: str, complexity_level: str) -> str:
        """
        Создаёт структурированный промпт для объяснения кода
        """
        complexity_guidelines = {
            "beginner": "Объясняй простыми словами, подходящими новичкам. Разбирай сложные понятия по шагам.",
            "intermediate": "Давай подробные объяснения с лучшими практиками и обоснованием.",
            "advanced": "Добавляй советы по оптимизации, альтернативные подходы и продвинутые концепции."
        }
        
        prompt = f"""<s>[INST] <<SYS>>
Ты опытный преподаватель программирования. Объясни следующий {language} код понятным и обучающим языком.

Рекомендации:
- Целевая аудитория: уровень {complexity_level}
- {complexity_guidelines.get(complexity_level, complexity_guidelines["intermediate"])}
- При необходимости давай построчные комментарии
- Отмечай лучшие практики и возможные улучшения
- Раскрывай логику и обоснование выбранных решений
- Используй корректное форматирование в markdown

Код для объяснения:
```{language}
{code_snippet}
```

Дай развёрнутое объяснение.[/INST]
"""
        
        return prompt
    
    def _format_explanation(self, explanation: str) -> str:
        """
        Форматирует ответ LLM для удобного чтения
        """
        # Очищаем ответ и следим за корректным форматированием
        explanation = explanation.strip()
        
        # Гарантируем корректные блоки кода в markdown
        if "```" not in explanation:
            explanation = explanation.replace("`", "\\`")
        
        return explanation
    
    def _mock_explanation(self, code_snippet: str, language: str, complexity_level: str, 
                         code_summary: Dict[str, Any] = None, validation_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Мок-объяснение для разработки и тестирования.
        Использует результаты анализа кода, чтобы сформировать персонализированный ответ.
        """
        # Формируем шаблон с учётом языка
        # Отображаем названия языков для вывода
        lang_display_names = {
            "cpp": "C++",
            "csharp": "C#",
            "javascript": "JavaScript",
            "typescript": "TypeScript"
        }
        lang_name = lang_display_names.get(language, language.capitalize())
        code_block_lang = language
        
        # Используем собранный анализ кода, если он есть
        if code_summary is None:
            code_summary = {"purpose": "Неизвестная функциональность", "complexity": "Простая", "key_functions": []}
        
        # Извлекаем ключевую информацию из анализа
        purpose = code_summary.get("purpose", "Неизвестная функциональность")
        functions = code_summary.get("key_functions", [])
        control_structures = code_summary.get("control_structures", [])
        variables = code_summary.get("key_variables", [])
        operations = code_summary.get("operations", [])
        patterns = code_summary.get("patterns", [])
        complexity_detected = code_summary.get("complexity", "Простая")
        level_display = {
            "beginner": "начальный",
            "intermediate": "средний",
            "advanced": "продвинутый"
        }.get(complexity_level, complexity_level)
        
        # Формируем текст со списком функций
        if functions:
            if len(functions) == 1:
                functions_text = f"`{functions[0]}`"
            elif len(functions) <= 3:
                functions_text = ", ".join([f"`{f}`" for f in functions])
            else:
                functions_text = ", ".join([f"`{f}`" for f in functions[:3]]) + f", и ещё {len(functions) - 3}"
        else:
            functions_text = "Функции не обнаружены"
        
        # Формируем описание управляющих конструкций
        control_text = ", ".join(control_structures) if control_structures else "Прямолинейное последовательное выполнение"
        
        # Формируем описание операций
        operations_text = ", ".join(operations) if operations else "Базовые операции"
        
        # Получаем превью кода для примера
        first_line = code_snippet.split('\n')[0][:80] if code_snippet else "code_example"
        preview = code_snippet[:200] + "..." if len(code_snippet) > 200 else code_snippet
        
        base_explanation = f"""## Объяснение кода на {lang_name} (уровень {level_display})

### Общее описание
Этот пример на {lang_name} предназначен для задачи **{purpose.lower()}**. Анализ показал, что уровень сложности — {complexity_detected.lower()}.

### Что делает код
Код решает задачу «{purpose.lower()}».{" Он включает следующие функции: " + functions_text + "." if functions else " Операции выполняются без явных определений функций."}

### Ключевые элементы
{"**Функции:** " + functions_text if functions else ""}
{"**Управление потоком:** " + control_text if control_structures else ""}
{"**Операции:** " + operations_text if operations else ""}
{"**Ключевые переменные:** " + ", ".join([f"`{v}`" for v in variables[:5]]) if variables else ""}
{chr(10).join("- " + p for p in patterns) if patterns else ""}

### Фрагмент кода
```{code_block_lang}
{preview}
```

### Технические детали
- **Назначение:** {purpose}
- **Обнаруженная сложность:** {complexity_detected}
- **Язык:** {lang_name}
{"- **Функции:** " + functions_text if functions else ""}

### Лучшие практики
- Код следует соглашениям {lang_name}
- {"Используются соответствующие управляющие конструкции" if control_structures else "Выполнение идёт последовательно без ветвлений"}
- {"Основные операции: " + operations_text if operations else "Задействованы базовые операции"}

Объяснение адаптировано под {level_display} уровень и построено на анализе переданного кода."""
        
        if complexity_level == "intermediate":
            # Формируем подробный список компонент
            components = []
            if functions:
                components.append(f"**Функции:** {functions_text}")
            if control_structures:
                components.append(f"**Управление потоком:** {control_text}")
            if operations:
                components.append(f"**Операции:** {operations_text}")
            if variables:
                components.append(f"**Ключевые переменные:** {', '.join([f'`{v}`' for v in variables[:5]])}")
            components_text = chr(10).join(f"- {c}" for c in components) if components else "- Базовая структура кода"
            
            base_explanation = f"""## Анализ кода на {lang_name} (уровень {level_display})

### Сводка
Этот код на {lang_name} реализует **{purpose.lower()}**. Анализ показал **{complexity_detected.lower()}** уровень сложности, {"обнаружено " + str(len(functions)) + " функци(й/и)" if functions else "функции не задействованы"}.

### Логика работы
Главная цель — {purpose.lower()}. {"Для этого используются функции: " + functions_text + "." if functions else "Логика реализована напрямую в теле кода."}

#### Ключевые компоненты
{components_text}

#### Технические детали
```{code_block_lang}
{preview}
```

#### Разбор анализа
- **Назначение:** {purpose}
- **Сложность кода:** {complexity_detected}
- **Управление потоком:** {control_text}
{"- **Операции:** " + operations_text if operations else ""}
{chr(10).join("- " + p for p in patterns) if patterns else ""}

#### Замечания по производительности
{"Код выполняет " + operations_text + ", что может повлиять на производительность." if operations else "Производительность соответствует базовому сценарию."} {"Наличие " + str(len(functions)) + " функци(й/и) повышает модульность." if functions else ""}

#### Продемонстрированные практики
- {"Ясное разделение логики по функциям" if functions else "Последовательная реализация без вспомогательных функций"}
- {"Корректное использование " + control_text.lower() if control_structures else "Линейное исполнение без ветвлений"}
- Соблюдаются соглашения {lang_name}

Этот разбор даёт представление среднего уровня и основан на структуре вашего кода."""
        
        elif complexity_level == "advanced":
            # Расширенный анализ с дополнительными выводами
            memory_ops = [op for op in operations if 'memory' in op or 'allocation' in op or 'deallocation' in op]
            memory_text = ", ".join(memory_ops) if memory_ops else "Стандартное управление памятью"
            
            base_explanation = f"""## Продвинутый анализ и оптимизация кода на {lang_name}

### Архитектура решения
Код реализует **{purpose.lower()}**, уровень сложности — {complexity_detected.lower()}. {"В коде определено " + str(len(functions)) + " функци(й/и): " + functions_text + "." if functions else "Реализация выполнена без выделенных функций."}

#### Детальный разбор

**1. Структура функций**
{"Код использует следующие функции: " + functions_text + "." if functions else "Функции не обнаружены — логика реализована процедурно."}
{"Количество функций указывает на " + ("модульный подход" if len(functions) > 1 else "сфокусированный дизайн под одну задачу") if functions else ""}

**2. Управление потоком**
Задействованы конструкции: {control_text.lower()}. {"Это говорит о " + ("сложной логике принятия решений" if len(control_structures) > 2 else "умеренной ветвистости") if control_structures else "Исполнение идёт последовательно."}

**3. Операции и паттерны**
{"Определены операции: " + operations_text + "." if operations else "Выполняются базовые операции."}
{chr(10).join("- " + p for p in patterns) if patterns else ""}

#### Продвинутые аспекты

**Управление памятью**
{memory_text}. {"Код явно управляет памятью" if memory_ops else f"Память контролируется рантаймом {lang_name}."}

**Алгоритмическая сложность**
{"Наличие " + str(len(functions)) + " функци(й/и) намекает на " + ("возможность оптимизации через рефакторинг" if len(functions) > 3 else "хорошую модульность") + "." if functions else "Стоит рассмотреть вынос частей логики в функции для переиспользования."}
По управляющим конструкциям: {"сложная логика ветвлений" if len(control_structures) > 2 else "умеренная сложность"}.

**Производительность**
{"Код выполняет " + operations_text + ", что влияет на характеристики производительности." if operations else "Производительность определяется базовой последовательной обработкой."}

#### Структура кода
```{code_block_lang}
{first_line}
...
```

#### Возможности оптимизации
{"Рассмотрите рефакторинг на более мелкие функции, если сложность превышает комфортный уровень." if complexity_detected == "Сложная" else "Структура кода сбалансирована для текущей задачи."}
{"Наличие операций (" + operations_text + ") требует внимания к производительности." if operations else ""}
{"Множественные управляющие конструкции (" + str(len(control_structures)) + ") можно упростить для повышения читабельности." if len(control_structures) > 3 else ""}

#### Рекомендации для продакшена
- {"Модульный дизайн с " + str(len(functions)) + " функци(ями/ями) упрощает тестирование и поддержку." if functions else "Рассмотрите выделение функций для упрощения тестирования."}
- {control_text + " требует внимательного учета крайних случаев." if control_structures else "Прямолинейный поток снижает риск ошибок."}
- {"Операции (" + operations_text + ") стоит мониторить в продуктивной среде." if operations else ""}

Этот анализ основан на фактическом содержимом кода и предназначен для продвинутых разработчиков, работающих с {lang_name}."""
        
        return {
            "success": True,
            "explanation": base_explanation,
            "complexity_level": complexity_level,
            "language": language,
            "mock": True
        }