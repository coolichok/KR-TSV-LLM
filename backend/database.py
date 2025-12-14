from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Создаём каталог для базы данных, если его нет
db_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(db_dir, 'code_explainer.db')

# Настройка базы данных
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CodeExplanation(Base):
    __tablename__ = "code_explanations"
    
    id = Column(Integer, primary_key=True, index=True)
    code_snippet = Column(Text, nullable=False)
    language = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=False)
    complexity_level = Column(String(20), default="intermediate")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_favorite = Column(Boolean, default=False)
    tags = Column(String(500), default="")
    
    def to_dict(self):
        return {
            "id": self.id,
            "code_snippet": self.code_snippet,
            "language": self.language,
            "explanation": self.explanation,
            "complexity_level": self.complexity_level,
            "created_at": self.created_at.isoformat(),
            "is_favorite": self.is_favorite,
            "tags": self.tags
        }

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()