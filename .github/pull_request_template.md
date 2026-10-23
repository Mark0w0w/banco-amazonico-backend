## Qué cambia

<!-- Una o dos frases. -->

**Tarea:** BAI-___  · **RNF relacionado:** RNF-__

## Cómo se probó

- [ ] Agregué o actualicé pruebas (pytest)
- [ ] `ruff check .` y `pytest` pasan en mi máquina
- [ ] Si cambié la base: hay una migración de Alembic y la leí antes de aplicarla

## Lista de revisión (la marca quien revisa)

- [ ] Toda entrada se valida con Pydantic; las consultas a la base son parametrizadas
- [ ] No se registran datos personales (DNI, cuenta, tarjeta, claves, tokens) en logs
- [ ] Ninguna excepción se silencia sin registrarla
- [ ] Si toca dinero: transacción única, `FOR UPDATE` y `X-Idempotency-Key`
- [ ] Si cambia un esquema de `app/schemas`: avisé al frontend (es el contrato)
- [ ] No queda código muerto ni comentado
