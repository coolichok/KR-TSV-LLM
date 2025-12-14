from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class CodeExplanationRequest(BaseModel):
    code_snippet: str = Field(..., description="Фрагмент кода, который нужно объяснить", min_length=1)
    language: Optional[str] = Field(None, description="Язык программирования (null/пусто для автоопределения)")
    complexity_level: str = Field(default="intermediate", description="Целевой уровень сложности объяснения")
    
    @validator('language')
    def validate_language(cls, v):
        if v is None:
            return None
        allowed_languages = ['python', 'javascript', 'java', 'cpp', 'csharp', 'php', 'ruby', 'go', 'rust', 'typescript', 'html', 'css', 'sql', 'bash', 'auto', 'auto-detect']
        v_lower = v.lower() if v else None
        if v_lower and v_lower not in allowed_languages:
            raise ValueError(f'Язык должен быть одним из: {", ".join(allowed_languages)}')
        return v_lower if v_lower else None
    
    @validator('complexity_level')
    def validate_complexity(cls, v):
        allowed_levels = ['beginner', 'intermediate', 'advanced']
        if v.lower() not in allowed_levels:
            raise ValueError(f'Уровень сложности должен быть одним из: {", ".join(allowed_levels)}')
        return v.lower()

class CodeExplanationResponse(BaseModel):
    success: bool
    explanation: str
    language: str
    complexity_level: str
    code_summary: Optional[Dict[str, Any]] = None
    validation_info: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None

class HistoryItem(BaseModel):
    id: int
    code_snippet: str
    language: str
    explanation: str
    complexity_level: str
    created_at: datetime
    is_favorite: bool = False
    tags: Optional[str] = None
    
    class Config:
        from_attributes = True

class HistoryResponse(BaseModel):
    success: bool
    explanations: List[HistoryItem]
    total_count: int
    page: int
    per_page: int
    total_pages: int

class HistoryFilter(BaseModel):
    language: Optional[str] = None
    complexity_level: Optional[str] = None
    is_favorite: Optional[bool] = None
    search_term: Optional[str] = None
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)

class FavoriteRequest(BaseModel):
    explanation_id: int
    is_favorite: bool

class APIHealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    llm_service_status: str
    database_status: str