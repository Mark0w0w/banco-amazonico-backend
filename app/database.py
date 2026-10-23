"""Conexión asíncrona a PostgreSQL (local en Docker o Supabase)."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    # Supabase con pooler: sin caché de sentencias preparadas evita errores de asyncpg.
    connect_args={"statement_cache_size": 0},
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependencia de FastAPI: entrega una sesión y la cierra al terminar, pase lo que pase."""
    async with SessionLocal() as sesion:
        yield sesion
