from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List

from ..database import get_db, CodeExplanation
from ..models import HistoryResponse, HistoryFilter, FavoriteRequest

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/explanations", response_model=HistoryResponse)
async def get_explanations(
    language: Optional[str] = Query(None, description="Фильтр по языку программирования"),
    complexity_level: Optional[str] = Query(None, description="Фильтр по уровню сложности"),
    is_favorite: Optional[bool] = Query(None, description="Фильтр по признаку избранного"),
    search_term: Optional[str] = Query(None, description="Поиск по коду или объяснению"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=100, description="Количество элементов на странице"),
    db: Session = Depends(get_db)
):
    """
    Получить постраничный список объяснений кода с фильтрацией
    """
    try:
        # Формируем запрос
        query = db.query(CodeExplanation)
        
        # Применяем фильтры
        if language:
            query = query.filter(CodeExplanation.language == language.lower())
        
        if complexity_level:
            query = query.filter(CodeExplanation.complexity_level == complexity_level.lower())
        
        if is_favorite is not None:
            query = query.filter(CodeExplanation.is_favorite == is_favorite)
        
        if search_term:
            search_filter = or_(
                CodeExplanation.code_snippet.contains(search_term),
                CodeExplanation.explanation.contains(search_term),
                CodeExplanation.tags.contains(search_term)
            )
            query = query.filter(search_filter)
        
        # Получаем общее количество записей
        total_count = query.count()
        
        # Применяем пагинацию
        offset = (page - 1) * per_page
        explanations = query.order_by(CodeExplanation.created_at.desc()).offset(offset).limit(per_page).all()
        
        # Рассчитываем параметры пагинации
        total_pages = (total_count + per_page - 1) // per_page
        
        return HistoryResponse(
            success=True,
            explanations=explanations,
            total_count=total_count,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving explanations: {str(e)}"
        )

@router.get("/explanations/{explanation_id}")
async def get_explanation_by_id(
    explanation_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить конкретное объяснение по ID
    """
    try:
        explanation = db.query(CodeExplanation).filter(CodeExplanation.id == explanation_id).first()
        
        if not explanation:
            raise HTTPException(
                status_code=404,
                detail=f"Explanation with ID {explanation_id} not found"
            )
        
        return {
            "success": True,
            "explanation": explanation.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving explanation: {str(e)}"
        )

@router.post("/explanations/{explanation_id}/favorite")
async def toggle_favorite(
    explanation_id: int,
    request: FavoriteRequest,
    db: Session = Depends(get_db)
):
    """
    Переключить статус избранного для объяснения
    """
    try:
        explanation = db.query(CodeExplanation).filter(CodeExplanation.id == explanation_id).first()
        
        if not explanation:
            raise HTTPException(
                status_code=404,
                detail=f"Explanation with ID {explanation_id} not found"
            )
        
        explanation.is_favorite = request.is_favorite
        db.commit()
        
        return {
            "success": True,
            "message": f"Explanation {'added to' if request.is_favorite else 'removed from'} favorites",
            "explanation": explanation.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating favorite status: {str(e)}"
        )

@router.delete("/explanations/{explanation_id}")
async def delete_explanation(
    explanation_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить объяснение из истории
    """
    try:
        explanation = db.query(CodeExplanation).filter(CodeExplanation.id == explanation_id).first()
        
        if not explanation:
            raise HTTPException(
                status_code=404,
                detail=f"Explanation with ID {explanation_id} not found"
            )
        
        db.delete(explanation)
        db.commit()
        
        return {
            "success": True,
            "message": "Explanation deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting explanation: {str(e)}"
        )

@router.get("/stats")
async def get_history_stats(db: Session = Depends(get_db)):
    """
    Получить статистику по объяснениям кода
    """
    try:
        total_explanations = db.query(CodeExplanation).count()
        favorite_explanations = db.query(CodeExplanation).filter(CodeExplanation.is_favorite == True).count()
        
        # Распределение по языкам
        language_stats = db.query(
            CodeExplanation.language,
            db.func.count(CodeExplanation.id).label('count')
        ).group_by(CodeExplanation.language).all()
        
        # Распределение по уровням сложности
        complexity_stats = db.query(
            CodeExplanation.complexity_level,
            db.func.count(CodeExplanation.id).label('count')
        ).group_by(CodeExplanation.complexity_level).all()
        
        return {
            "success": True,
            "stats": {
                "total_explanations": total_explanations,
                "favorite_explanations": favorite_explanations,
                "language_distribution": [
                    {"language": lang, "count": count} for lang, count in language_stats
                ],
                "complexity_distribution": [
                    {"complexity": level, "count": count} for level, count in complexity_stats
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )