#!/usr/bin/env python3
"""
Простой скрипт для запуска API Code Explainer
"""

import sys
import os
import subprocess

# Настройка кодировки консоли Windows
if sys.platform == 'win32':
    try:
        # Попытка установить кодировку UTF-8 для консоли Windows
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        # Резервный вариант для старых версий Python или при ошибке reconfigure
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    print("Запуск API Code Explainer...")
    print("=" * 50)
    
    # Определяем корневую директорию проекта (где находится этот скрипт)
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Добавляем корень проекта в PYTHONPATH, чтобы backend импортировался как пакет
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        # Запускаем из корня проекта, используя backend.app:app в качестве модуля приложения
        cmd = [sys.executable, '-m', 'uvicorn', 'backend.app:app', '--reload', '--host', '0.0.0.0', '--port', '8000']
        print(f"Команда запуска: {' '.join(cmd)}")
        print("\nAPI будет доступно по адресу: http://localhost:8000")
        print("Документация API: http://localhost:8000/docs")
        print("Веб-интерфейс: http://localhost:8000/static/index.html")
        print("Страница истории: http://localhost:8000/static/history.html")
        print("\n" + "=" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\nОстановка API Code Explainer...")
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")
        print("\nУбедитесь, что установлены все зависимости:")
        print("   pip install -r backend/requirements.txt")

if __name__ == "__main__":
    main()