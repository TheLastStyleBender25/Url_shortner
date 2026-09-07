from app.db.session import DATABASE_URL
from sqlalchemy.ext.asyncio import AsyncSession,async_sessionmaker,create_async_engine

_engine = None
_session_factory = None


def get_worker_session_factory():
    global _engine
    global _session_factory
    if _engine is None:
        _engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
        _session_factory = async_sessionmaker(_engine,class_=AsyncSession,expire_on_commit=False)
    return _session_factory
