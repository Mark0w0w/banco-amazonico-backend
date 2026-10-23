"""Modelos SQLAlchemy. Una tabla por archivo; todos se importan aquí para que Alembic los vea.

Convención (ver docs/CONTENIDO_BACKEND_BANCO.md, sección 8):
- tablas en singular, clave primaria id_<tabla>
- campos de auditoría vía AuditoriaMixin
- dinero en Numeric(14, 2), nunca float; fechas con zona horaria
"""

from app.models.base import AuditoriaMixin, Base

__all__ = ["AuditoriaMixin", "Base"]
