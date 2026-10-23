"""/health: el hosting y el docker-compose lo usan para saber si el backend está vivo."""

import logging

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.redis_cliente import redis

router = APIRouter(tags=["salud"])
log = logging.getLogger(__name__)


@router.get("/health")
async def salud(respuesta: Response, db: AsyncSession = Depends(get_db)) -> dict:
    componentes = {"db": False, "redis": False}
    # /health informa del fallo en vez de reventar, pero nunca lo silencia: queda en el log.
    try:
        await db.execute(text("SELECT 1"))
        componentes["db"] = True
    except Exception:  # noqa: BLE001
        log.exception("health: la base de datos no responde")
    try:
        componentes["redis"] = bool(await redis.ping())
    except Exception:  # noqa: BLE001
        log.exception("health: redis no responde")

    ok = all(componentes.values())
    if not ok:
        respuesta.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {"ok": ok, **componentes}
