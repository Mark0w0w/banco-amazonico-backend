FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Dependencias primero: Docker las guarda en caché y no reinstala si solo cambia el código.
# INSTALAR_DEV=true (docker-compose) agrega pytest, ruff, etc. para correr las pruebas adentro.
ARG INSTALAR_DEV=false
COPY requirements.txt requirements-dev.txt ./
RUN if [ "$INSTALAR_DEV" = "true" ]; then pip install -r requirements-dev.txt; \
    else pip install -r requirements.txt; fi

COPY . .

# Nunca correr como root dentro del contenedor.
RUN useradd --create-home --uid 1000 banco && chown -R banco:banco /app
USER banco

EXPOSE 8000

# Primero migra la base, después levanta el servidor (en ese orden).
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
