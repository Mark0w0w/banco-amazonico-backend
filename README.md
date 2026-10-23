# Banco Amazónico — Backend del Asistente Virtual con IA

Backend del proyecto del curso **Calidad aplicada a los sistemas de información** (UNAMAD).
FastAPI + PostgreSQL (pgvector) + Redis + Ollama. Debe cumplir los 5 RNF de ISO/IEC 25010 de
nuestra exposición.

📄 **El plan completo está en [`docs/CONTENIDO_BACKEND_BANCO.md`](docs/CONTENIDO_BACKEND_BANCO.md).**
Léelo antes de empezar.

| RNF | Qué exige | Dueño |
|---|---|---|
| RNF-01 | p95 ≤ 1,5 s hasta la primera respuesta visible | Backend 2 |
| RNF-02 | 0 % de datos personales al modelo · TLS 1.3 · AES-256 | Backend 2 (enmascarado) + Backend 1 (cifrado, TLS) |
| RNF-03 | 100 % con sesión verificada (MFA) · expira a 5 min inactivo | Backend 1 |
| RNF-04 | Cambiar el modelo con 0 conversaciones interrumpidas | Backend 1 |
| RNF-05 | ≥ 98 % de acierto en intenciones críticas | Backend 2 |

---

## 1. Primera vez: levantar todo con Docker

**Necesitas:** Git, [Docker Desktop](https://www.docker.com/products/docker-desktop/) abierto
(la ballena en la barra de tareas) y VS Code.

```powershell
git clone https://github.com/Mark0w0w/banco-amazonico-backend.git
cd banco-amazonico-backend
git checkout develop

copy .env.example .env          # en Git Bash / Linux / Mac:  cp .env.example .env
docker compose up --build
```

La primera vez tarda unos minutos (descarga PostgreSQL, Redis y Python). Cuando veas
`Uvicorn running on http://0.0.0.0:8000`, abre:

- **http://localhost:8000/docs** → todos los endpoints con botón para probarlos
- **http://localhost:8000/health** → debe decir `{"ok": true, "db": true, "redis": true}`

Para apagar: `Ctrl + C` y luego `docker compose down`.
Para borrar también la base local y empezar de cero: `docker compose down -v`.

> Guardas un archivo `.py` en VS Code y el servidor se reinicia solo (`--reload`). No hace falta
> reconstruir. **Solo** hay que volver a hacer `docker compose up --build` cuando cambia
> `requirements.txt`.

## 2. Comandos del día a día

```powershell
docker compose up                                  # levantar (sin --build si no cambió requirements)
docker compose exec api pytest                     # correr TODAS las pruebas
docker compose exec api pytest --cov               # pruebas + cobertura (meta ≥ 80 %)
docker compose exec api ruff check .               # estilo y errores
docker compose exec api ruff format .              # formatear el código
docker compose exec api alembic revision --autogenerate -m "crea tabla cuenta"
docker compose exec api alembic upgrade head       # aplicar migraciones
docker compose exec db psql -U banco -d banco      # entrar a la base con SQL
docker compose logs -f api                         # ver los logs del backend
```

## 3. Los mocks (para el frontend)

Con `MOCKS_ACTIVOS=true` (por defecto en `.env.example`), estos endpoints devuelven datos
inventados con **la misma forma que tendrán los reales**. Los esquemas de `app/schemas/` son el
contrato con el frontend.

| Endpoint | Dato de prueba |
|---|---|
| `GET /api/v1/auth/teclado` | orden aleatorio del teclado |
| `POST /api/v1/auth/login` | cualquier clave de 6 dígitos sirve, salvo `000000` |
| `POST /api/v1/auth/mfa/totp` | el código **`123456`** siempre funciona |
| `GET /api/v1/cuentas` | 2 cuentas (S/ y US$) |
| `GET /api/v1/cuentas/{id}/movimientos` | 5 movimientos (cuentas 1 y 2) |
| `POST /api/v1/chat/conversaciones` | crea una conversación |
| `POST /api/v1/chat/conversaciones/{id}/mensajes` | **streaming SSE**: prueba "¿cuánto tengo?", "bloquear mi tarjeta", "tasa plazo fijo" o algo raro (deriva al asesor) |

Cuando un endpoint real esté listo, se borra su versión de `app/routers/mocks.py`.

## 4. IA: Ollama (solo Backend 2 / laptop con GPU)

Ollama **no** corre en Docker: se instala en Windows desde [ollama.com](https://ollama.com).

```powershell
ollama pull llama3.1:8b
ollama pull bge-m3
```

En `.env` cambia `LLM_PROVEEDOR=ollama`. El contenedor llega a Ollama por
`http://host.docker.internal:11434`. Si tu laptop no tiene GPU, deja `LLM_PROVEEDOR=falso`
(respuestas fijas) o apunta `OLLAMA_URL` a la IP de la laptop con GPU.

## 5. Cómo trabajamos (proceso de calidad)

**Ramas.** Nadie hace push directo a `main` ni a `develop` (están protegidas).

```powershell
git checkout develop
git pull                                     # SIEMPRE antes de empezar
git checkout -b feature/BAI-012-login-totp   # una rama por tarea, que dure 1 o 2 días
# ... trabajas y haces commits ...
git push -u origin feature/BAI-012-login-totp
# En GitHub: "Compare & pull request" hacia develop → el otro revisa → Merge
```

**Commits** (convencionales): `tipo(ámbito): descripción [BAI-NNN]`

```
feat(auth): agrega verificación TOTP [BAI-012]
fix(chat): corrige el evento done sin latencia [BAI-031]
test(rnf02): 200 mensajes con datos personales [BAI-040]
docs: actualiza el README
```

**Para fusionar un PR hace falta:**
1. La aprobación del otro integrante (en auth, transferencias y chat revisa el otro backend).
2. El **CI en verde**: ruff, bandit, pip-audit, migraciones desde cero y pytest con cobertura ≥ 80 %.

**Antes del primer commit**, una sola vez:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pre-commit install          # revisa estilo y secretos en cada commit
```

(El `.venv` también le da a VS Code el autocompletado.)

**Reglas que no se negocian:**
- `.env` nunca se sube. Si se sube por error: **cambiar las claves**, borrarlo no basta.
- Desde que existe Alembic, **la base nunca se cambia a mano**: cada cambio es una migración.
- Dinero en `Numeric(14, 2)`, nunca `float`. Fechas con zona horaria.
- No se registran datos personales en los logs. Ninguna excepción se silencia.
- Todo PR trae sus pruebas.

## 6. Estructura

```
app/
  main.py            crea la app, CORS, middlewares, routers
  config.py          variables de entorno (si falta una obligatoria, no arranca)
  database.py        conexión async a PostgreSQL + get_db
  redis_cliente.py   cliente Redis
  models/            tablas SQLAlchemy (base.py: Base + AuditoriaMixin)
  schemas/           Pydantic: el contrato de la API
  routers/           endpoints (salud.py, mocks.py, ...)
  services/          lógica bancaria (Backend 1)
  services/ia/       asistente IA (Backend 2)
  seguridad/         jwt, argon2, totp, biometría, cifrado (Backend 1)
  middleware/        trace_id, ...
alembic/             migraciones (0001: extensión pgvector)
tests/               pytest (correr dentro de Docker)
docker/              init de PostgreSQL
docs/                plan del proyecto y evidencias de los RNF
```
