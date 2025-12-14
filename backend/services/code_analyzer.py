import re
from typing import Dict, Optional, List, Any

class CodeAnalyzer:
    """
    Утилитный класс для анализа и валидации фрагментов кода
    """
    
    # Шаблоны для определения языка
    LANGUAGE_PATTERNS = {
        'python': [
            r'^\s*def\s+\w+\s*\(',  # Определение функции
            r'^\s*import\s+\w+',     # Оператор import
            r'^\s*from\s+\w+\s+import',  # Оператор from ... import
            r'^\s*#.*$',              # Комментарий Python
            r'print\s*\(',            # Вызов print
            r'^\s*if\s+__name__\s*==\s*["\']__main__["\']\s*:',  # Страж main
        ],
        'javascript': [
            r'^\s*function\s+\w+\s*\(',  # Объявление функции
            r'^\s*const\s+\w+\s*=',      # Объявление const
            r'^\s*let\s+\w+\s*=',        # Объявление let
            r'^\s*var\s+\w+\s*=',        # Объявление var
            r'console\.log\s*\(',         # Вызов console.log
            r'^\s*//.*$',                 # Комментарий JavaScript
            r'^\s*/\*.*\*/\s*$',         # Многострочный комментарий
        ],
        'java': [
            r'^\s*public\s+class\s+\w+',  # Объявление публичного класса
            r'^\s*public\s+static\s+void\s+main',  # Метод main
            r'^\s*import\s+java\.',       # Импорт Java
            r'^\s*System\.out\.println',  # Вызов System.out.println
            r'^\s*//.*$',                  # Однострочный комментарий
            r'^\s*/\*.*\*/\s*$',          # Многострочный комментарий
        ],
        'cpp': [
            r'^\s*#include\s+<',           # Директива include
            r'^\s*int\s+main\s*\(',        # Функция main
            r'^\s*std::cout\s*<<',         # Использование std::cout
            r'^\s*using\s+namespace\s+std', # Использование пространства имён std
            r'^\s*\w+\*+\s*\w+',          # Типы указателей
            r'^\s*\w+\s*\w+\*+&',         # Ссылка на указатель
            r'^\s*\w+\*+&\s*\w+',         # Параметр со ссылкой на указатель
            r'nullptr',                    # Ключевое слово nullptr
            r'^\s*void\s+\w+\s*\(',       # Функция с типом void
            r'^\s*\w+::\w+',               # Использование пространства имён
            r'new\s+\w+\s*\(',            # Оператор new
            r'delete\s+\w+',               # Оператор delete
            r'^\s*//.*$',                  # Комментарий C++
        ]
    }
    
    # Соответствие расширений файлов языкам
    EXTENSION_MAPPING = {
        'py': 'python',
        'js': 'javascript',
        'java': 'java',
        'cpp': 'cpp',
        'c++': 'cpp',
        'c': 'c',
        'cs': 'csharp',
        'php': 'php',
        'rb': 'ruby',
        'go': 'go',
        'rs': 'rust',
        'ts': 'typescript',
        'html': 'html',
        'css': 'css',
        'sql': 'sql',
        'sh': 'bash',
        'bash': 'bash'
    }
    
    @staticmethod
    def detect_language(code_snippet: str, suggested_language: str = None) -> str:
        """
        Определяет язык программирования на основе фрагмента кода
        """
        code_snippet = code_snippet.strip()
        
        # Обрабатываем режим автоопределения или пустое значение
        if not suggested_language or suggested_language.lower() in ('auto', 'auto-detect', ''):
            suggested_language = None
        
        # Если пользователь указал язык явно, проверяем и используем его
        if suggested_language and suggested_language.lower() in CodeAnalyzer.EXTENSION_MAPPING.values():
            return suggested_language.lower()
        
        # Пытаемся определить язык по расширению, указанному в комментарии
        extension_match = re.search(r'//\s*(\w+)\s*$', code_snippet.split('\n')[0])
        if extension_match:
            ext = extension_match.group(1).lower()
            if ext in CodeAnalyzer.EXTENSION_MAPPING:
                return CodeAnalyzer.EXTENSION_MAPPING[ext]
        
        # Оценка по набранным очкам — надёжнее, чем первое совпадение
        language_scores = {}
        
        # Подсчитываем очки для каждого языка на основе совпадений
        for language, patterns in CodeAnalyzer.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, code_snippet, re.MULTILINE)
                # Более специфичные шаблоны получают больший вес
                # Шаблоны, характерные для меньшего числа языков, надёжнее
                if matches:
                    # Вес зависит от специфичности шаблона (чем специфичнее, тем выше)
                    # Шаблоны с ::, * или # — более показательные
                    weight = 2 if ('::' in pattern or '*' in pattern or '#' in pattern) else 1
                    score += len(matches) * weight
            if score > 0:
                language_scores[language] = score
        
        # Возвращаем язык с максимальным количеством баллов, иначе python
        if language_scores:
            detected = max(language_scores.items(), key=lambda x: x[1])[0]
            return detected
        
        # По умолчанию считаем язык python
        return "python"
    
    @staticmethod
    def validate_code(code_snippet: str, language: str) -> Dict[str, any]:
        """
        Базовая валидация фрагмента кода
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "stats": {}
        }
        
        if not code_snippet or not code_snippet.strip():
            validation_result["is_valid"] = False
            validation_result["errors"].append("Фрагмент кода не может быть пустым")
            return validation_result
        
        code_snippet = code_snippet.strip()
        lines = code_snippet.split('\n')
        
        # Базовая статистика
        validation_result["stats"] = {
            "lines": len(lines),
            "characters": len(code_snippet),
            "non_empty_lines": len([line for line in lines if line.strip()]),
            "comment_lines": len([line for line in lines if line.strip().startswith(('#', '//', '/*', '*'))])
        }
        
        # Языковые проверки
        if language == "python":
            validation_result.update(CodeAnalyzer._validate_python(code_snippet))
        elif language == "javascript":
            validation_result.update(CodeAnalyzer._validate_javascript(code_snippet))
        elif language == "java":
            validation_result.update(CodeAnalyzer._validate_java(code_snippet))
        
        # Общие предупреждения
        if validation_result["stats"]["lines"] > 100:
            validation_result["warnings"].append("Большой фрагмент кода может обрабатываться дольше")
        
        if validation_result["stats"]["comment_lines"] == 0:
            validation_result["warnings"].append("Рекомендуется добавить комментарии к коду")
        
        return validation_result
    
    @staticmethod
    def _validate_python(code_snippet: str) -> Dict[str, any]:
        """Проверки, характерные для Python"""
        result = {"errors": [], "warnings": []}
        
        # Проверяем наличие базового синтаксиса Python
        if not re.search(r'\w+', code_snippet):
            result["errors"].append("Не обнаружен корректный Python-код")
        
        # Ищем пропущенные двоеточия в управляющих конструкциях
        control_structures = ['if\s+.+:', 'for\s+.+:', 'while\s+.+:', 'def\s+\w+\s*\(.*\):', 'class\s+\w+\s*:']
        for pattern in control_structures:
            matches = re.findall(pattern, code_snippet)
            for match in matches:
                if not match.strip().endswith(':'):
                    result["warnings"].append(f"Возможно, отсутствует двоеточие: {match}")
        
        return result
    
    @staticmethod
    def _validate_javascript(code_snippet: str) -> Dict[str, any]:
        """Проверки, характерные для JavaScript"""
        result = {"errors": [], "warnings": []}
        
        # Проверяем наличие базовых элементов JavaScript
        if not re.search(r'(function|=>|const|let|var)\s+\w*', code_snippet):
            result["warnings"].append("Не обнаружены функции или объявления переменных")
        
        # Ищем пропущенные точки с запятой (частая проблема в JS)
        lines = code_snippet.split('\n')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped and 
                not stripped.endswith((';', '{', '}', ')', '(', '[', ']', ',')) and
                not stripped.startswith(('//', '/*', '*')) and
                '=>' not in stripped):
                result["warnings"].append(f"Строка {i+1}: рекомендуется добавить точку с запятой")
        
        return result
    
    @staticmethod
    def _validate_java(code_snippet: str) -> Dict[str, any]:
        """Проверки, характерные для Java"""
        result = {"errors": [], "warnings": []}
        
        # Проверяем наличие объявления класса
        if not re.search(r'class\s+\w+', code_snippet):
            result["warnings"].append("Не найдено объявление класса")
        
        # Проверяем наличие объявлений методов
        if not re.search(r'(public|private|protected)?\s*\w+\s+\w+\s*\(', code_snippet):
            result["warnings"].append("Не найдено объявление методов")
        
        return result
    
    @staticmethod
    def extract_code_summary(code_snippet: str, language: str) -> Dict[str, Any]:
        """
        Формирует подробное описание того, что делает код
        """
        summary = {
            "purpose": "Неизвестная функциональность",
            "complexity": "Простая",
            "key_functions": [],
            "control_structures": [],
            "key_variables": [],
            "operations": [],
            "patterns": []
        }
        
        lines = code_snippet.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith(('//', '/*', '#', '*'))]
        
        # Извлекаем имена функций в зависимости от языка
        if language == "python":
            functions = re.findall(r'def\s+(\w+)\s*\(', code_snippet)
            classes = re.findall(r'class\s+(\w+)', code_snippet)
            summary["key_functions"] = functions[:5]
            if classes:
                summary["patterns"].append(f"Определяет {len(classes)} класс(ов): {', '.join(classes)}")
        elif language == "javascript":
            functions = re.findall(r'function\s+(\w+)\s*\(', code_snippet)
            arrow_functions = re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*[^(]*=>', code_snippet)
            classes = re.findall(r'class\s+(\w+)', code_snippet)
            summary["key_functions"] = (functions + arrow_functions)[:5]
            if classes:
                summary["patterns"].append(f"Определяет {len(classes)} класс(ов): {', '.join(classes)}")
        elif language == "java":
            classes = re.findall(r'class\s+(\w+)', code_snippet)
            methods = re.findall(r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(', code_snippet)
            summary["key_functions"] = methods[:5]
            if classes:
                summary["patterns"].append(f"Определяет {len(classes)} класс(ов): {', '.join(classes)}")
        elif language == "cpp":
            functions = re.findall(r'(?:void|int|bool|string|char|float|double|\w+)\s+(\w+)\s*\(', code_snippet)
            classes = re.findall(r'class\s+(\w+)', code_snippet)
            summary["key_functions"] = functions[:5]
            if classes:
                summary["patterns"].append(f"Определяет {len(classes)} класс(ов): {', '.join(classes)}")
        
        # Определяем используемые управляющие конструкции
        control_patterns = {
            'if': r'\bif\s*\(',
            'for': r'\bfor\s*\(',
            'while': r'\bwhile\s*\(',
            'switch': r'\bswitch\s*\(',
            'try': r'\btry\s*\{'
        }
        for struct_name, pattern in control_patterns.items():
            matches = re.findall(pattern, code_snippet, re.IGNORECASE)
            if matches:
                summary["control_structures"].append(f"{len(matches)} конструкций {struct_name}")
        
        # Извлекаем ключевые переменные (объявления)
        var_patterns = {
            'python': r'(?:self\.)?(\w+)\s*=',
            'javascript': r'(?:const|let|var)\s+(\w+)',
            'java': r'(?:int|String|boolean|float|double)\s+(\w+)',
            'cpp': r'(?:int|string|bool|float|double|char)\s+(\w+)'
        }
        pattern = var_patterns.get(language)
        if pattern:
            variables = re.findall(pattern, code_snippet)
            # Убираем ключевые слова и имена функций
            keywords = {'if', 'for', 'while', 'return', 'def', 'class', 'import', 'from'}
            key_vars = [v for v in variables if v not in keywords and len(v) > 2][:8]
            summary["key_variables"] = key_vars
        
        # Определяем используемые операции
        operations = []
        if re.search(r'\+\+|\-\-|[\+\-\*/%=]', code_snippet):
            operations.append("арифметические операции")
        if re.search(r'(?:==|!=|<=|>=|<|>|&&|\|\|)', code_snippet):
            operations.append("операции сравнения")
        if re.search(r'(?:\.(?:add|remove|push|pop|insert|delete|find|get|set))', code_snippet, re.IGNORECASE):
            operations.append("операции с структурами данных")
        if re.search(r'(?:new\s+\w+|malloc|calloc)', code_snippet):
            operations.append("выделение памяти")
        if re.search(r'(?:delete|free|delete\[\])', code_snippet):
            operations.append("освобождение памяти")
        summary["operations"] = operations
        
        # Определяем уровень сложности
        line_count = len(lines)
        function_count = len(summary["key_functions"])
        control_count = len(summary["control_structures"])
        
        if line_count > 100 or function_count > 5:
            summary["complexity"] = "Сложная"
        elif line_count > 30 or function_count > 2 or control_count > 3:
            summary["complexity"] = "Средняя"
        else:
            summary["complexity"] = "Простая"
        
        # Дополнительное определение назначения кода
        code_lower = code_snippet.lower()
        
        # Управление памятью
        if any(word in code_lower for word in ['delete', 'free', 'clear', 'release', 'nullptr']):
            summary["purpose"] = "Управление памятью и очистка"
        elif any(word in code_lower for word in ['new', 'malloc', 'allocate']):
            summary["purpose"] = "Выделение памяти"
        
        # Структуры данных
        elif any(word in code_lower for word in ['sort', 'order', 'arrange', 'sorted']):
            summary["purpose"] = "Сортировка или упорядочивание данных"
        elif any(word in code_lower for word in ['search', 'find', 'lookup', 'contains']):
            summary["purpose"] = "Поиск элементов"
        elif any(word in code_lower for word in ['insert', 'add', 'push', 'append']):
            summary["purpose"] = "Добавление элементов в структуры данных"
        elif any(word in code_lower for word in ['remove', 'delete', 'pop']):
            summary["purpose"] = "Удаление элементов из структур данных"
        
        # Алгоритмы
        elif any(word in code_lower for word in ['calculate', 'compute', 'sum', 'count', 'total']):
            summary["purpose"] = "Математические вычисления"
        elif any(word in code_lower for word in ['fibonacci', 'factorial', 'recursive']):
            summary["purpose"] = "Реализация рекурсивного алгоритма"
        
        # Ввод/вывод
        elif any(word in code_lower for word in ['input', 'output', 'read', 'write', 'print', 'cout', 'cin']):
            summary["purpose"] = "Операции ввода-вывода"
        
        # Итерации
        elif re.search(r'\bfor\s*\(|\bwhile\s*\(', code_snippet):
            if len([m for m in re.finditer(r'\bfor\s*\(|\bwhile\s*\(', code_snippet)]) > 1:
                summary["purpose"] = "Итерационная обработка с циклами"
        
        # Если цель всё ещё неизвестна, пробуем определить по именам функций
        if summary["purpose"] == "Неизвестная функциональность" and summary["key_functions"]:
            func_names = ' '.join(summary["key_functions"]).lower()
            if any(word in func_names for word in ['get', 'fetch', 'retrieve']):
                summary["purpose"] = "Получение данных"
            elif any(word in func_names for word in ['set', 'update', 'modify']):
                summary["purpose"] = "Изменение данных"
            elif any(word in func_names for word in ['clear', 'clean', 'reset']):
                summary["purpose"] = "Сброс или очистка данных"
        
        return summary