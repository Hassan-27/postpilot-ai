from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.core.config import get_settings

settings = get_settings()

# Engine = the connection pool. Create once, reuse for the app's lifetime.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,       # prints every SQL query when DEBUG=True
    pool_size=10,              # persistent connections kept open
    max_overflow=20,           # extra connections allowed under burst load
    pool_pre_ping=True,        # test connections before using (handles DB restarts)
)

# SessionLocal is a factory — calling it produces a new session object
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,    # critical for async — explained below
    autocommit=False,
    autoflush=False,
)