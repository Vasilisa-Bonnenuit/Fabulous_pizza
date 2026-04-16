from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# строка подключения к бд
DATABASE_URL = "sqlite:///./users.db"

# создаём движок
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# фабрика сессий, через неё мы будем работать с БД (добавлять, читать, удалять)
SessionLocal = sessionmaker(
    autocommit=False,   # чтобы изменения не применялись автоматически
    autoflush=False,    # чтобы не было лишних автоматических сохранений
    bind=engine
)

# базовый класс для всех моделей
Base = declarative_base()