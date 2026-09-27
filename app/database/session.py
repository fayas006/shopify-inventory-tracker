from sqlalchemy.orm import sessionmaker

from app.database.models import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
