from app.db.base import Base
from app.db.database import engine

# Импортируем все модели
import app.models

# Создаем таблицы
Base.metadata.create_all(bind=engine)

print("✅ Database initialized successfully!")