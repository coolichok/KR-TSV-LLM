from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os
import time

from .database import create_tables
from .api import code, history
from .models import APIHealthResponse

# Создание таблиц базы данных при запуске приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

# Инициализация экземпляра FastAPI
app = FastAPI(
    title="Code Explainer API",
    description="AI-powered code explanation service for developers",
    version="1.0.0",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные источники
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров API
app.include_router(code.router)
app.include_router(history.router)

# Эндпойнт проверки состояния
@app.get("/health", response_model=APIHealthResponse)
async def health_check():
    """
    Эндпойнт проверки состояния API
    """
    from .services.llm_service import LLMService
    from .database import engine
    from sqlalchemy import text
    
    # Проверяем соединение с базой данных
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    # Проверяем доступность сервиса LLM
    try:
        llm_service = LLMService()
        # Мок-сервис всегда доступен
        llm_status = "healthy" if hasattr(llm_service, 'use_mock') else "unhealthy"
    except Exception:
        llm_status = "unhealthy"
    
    return APIHealthResponse(
        status="healthy" if db_status == "healthy" and llm_status == "healthy" else "degraded",
        timestamp=time.time(),
        version="1.0.0",
        llm_service_status=llm_status,
        database_status=db_status
    )

# Корневой эндпойнт
@app.get("/")
async def root():
    """
    Корневой эндпойнт с базовой информацией об API
    """
    return {
        "message": "Welcome to Code Explainer API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health"
    }

# Публикация статических файлов (фронтенд)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)