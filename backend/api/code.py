from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
import time

from ..database import get_db
from ..models import CodeExplanationRequest, CodeExplanationResponse
from ..services.llm_service import LLMService
from ..services.code_analyzer import CodeAnalyzer
from ..database import CodeExplanation

router = APIRouter(prefix="/code", tags=["code"])

@router.post("/explain", response_model=CodeExplanationResponse)
async def explain_code(
    request: CodeExplanationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Объяснение фрагмента кода с помощью анализа LLM
    """
    start_time = time.time()
    
    try:
        # Определяем или проверяем язык, если он указан
        detected_language = CodeAnalyzer.detect_language(request.code_snippet, request.language)
        
        # Валидируем код
        validation_info = CodeAnalyzer.validate_code(request.code_snippet, detected_language)
        
        if not validation_info["is_valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid code snippet: {', '.join(validation_info['errors'])}"
            )
        
        # Получаем краткое описание кода ДО вызова LLM (для более точного объяснения)
        code_summary = CodeAnalyzer.extract_code_summary(request.code_snippet, detected_language)
        
        # Инициализируем сервис LLM
        llm_service = LLMService()
        
        # Генерируем объяснение (передаём результаты анализа кода)
        llm_result = llm_service.explain_code(
            request.code_snippet,
            detected_language,
            request.complexity_level,
            code_summary=code_summary,
            validation_info=validation_info
        )
        
        if not llm_result["success"]:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate explanation. Please try again."
            )
        
        # Вычисляем время обработки
        processing_time = time.time() - start_time
        
        # Формируем ответ
        response = CodeExplanationResponse(
            success=True,
            explanation=llm_result["explanation"],
            language=detected_language,
            complexity_level=llm_result["complexity_level"],
            code_summary=code_summary,
            validation_info=validation_info,
            processing_time=round(processing_time, 2)
        )
        
        # Асинхронно сохраняем объяснение в базе данных
        background_tasks.add_task(
            save_explanation_to_db,
            db,
            request.code_snippet,
            detected_language,
            llm_result["explanation"],
            request.complexity_level
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@router.get("/languages")
async def get_supported_languages() -> Dict[str, Any]:
    """
    Возвращает список поддерживаемых языков программирования
    """
    languages = [
        {"name": "Python", "value": "python", "icon": "🐍"},
        {"name": "JavaScript", "value": "javascript", "icon": "🟨"},
        {"name": "Java", "value": "java", "icon": "☕"},
        {"name": "C++", "value": "cpp", "icon": "⚡"},
        {"name": "C#", "value": "csharp", "icon": "🔷"},
        {"name": "PHP", "value": "php", "icon": "🐘"},
        {"name": "Ruby", "value": "ruby", "icon": "💎"},
        {"name": "Go", "value": "go", "icon": "🐹"},
        {"name": "Rust", "value": "rust", "icon": "🦀"},
        {"name": "TypeScript", "value": "typescript", "icon": "🔷"},
        {"name": "HTML", "value": "html", "icon": "🌐"},
        {"name": "CSS", "value": "css", "icon": "🎨"},
        {"name": "SQL", "value": "sql", "icon": "🗄️"},
        {"name": "Bash", "value": "bash", "icon": "🐚"}
    ]
    
    return {
        "success": True,
        "languages": languages,
        "total_count": len(languages)
    }

@router.get("/complexity-levels")
async def get_complexity_levels() -> Dict[str, Any]:
    """
    Возвращает доступные уровни сложности объяснений
    """
    levels = [
        {
            "name": "Beginner",
            "value": "beginner",
            "description": "Simple explanations suitable for new programmers",
            "icon": "🌱"
        },
        {
            "name": "Intermediate", 
            "value": "intermediate",
            "description": "Detailed explanations with best practices",
            "icon": "🎯"
        },
        {
            "name": "Advanced",
            "value": "advanced", 
            "description": "Deep technical analysis with optimization tips",
            "icon": "🚀"
        }
    ]
    
    return {
        "success": True,
        "complexity_levels": levels
    }

def save_explanation_to_db(
    db: Session,
    code_snippet: str,
    language: str,
    explanation: str,
    complexity_level: str
):
    """
    Сохраняет объяснение в базе данных
    """
    try:
        db_explanation = CodeExplanation(
            code_snippet=code_snippet,
            language=language,
            explanation=explanation,
            complexity_level=complexity_level
        )
        db.add(db_explanation)
        db.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")
        db.rollback()