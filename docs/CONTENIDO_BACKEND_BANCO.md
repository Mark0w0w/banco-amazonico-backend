# Contenido del proyecto: Asistente Virtual Bancario con IA

**Curso:** Calidad aplicada a los sistemas de información, UNAMAD\
**Docente:** Jaramillo Peralta, Denys Alberto\
**Equipo:** Villasante Aracayo, Mark Anthony · Pereira Rampas, Korven Joshua · Díaz Ancco, Jorge Antonio\
**Entrega:** martes 3 de noviembre de 2026\
**Nombre de trabajo del banco:** Banco Amazónico (el de las pantallas de Stitch)

---

## Índice

1. [De qué se trata el proyecto](#1-de-qué-se-trata-el-proyecto)
2. [Qué es cada archivo de referencia (y cuál NO es el proyecto)](#2-qué-es-cada-archivo-de-referencia-y-cuál-no-es-el-proyecto)
3. [Los 5 RNF que hay que cumplir](#3-los-5-rnf-que-hay-que-cumplir)
4. [Cómo funciona el chatbot, paso a paso](#4-cómo-funciona-el-chatbot-paso-a-paso)
5. [Cómo se cumple y cómo se demuestra cada RNF](#5-cómo-se-cumple-y-cómo-se-demuestra-cada-rnf)
6. [Tecnologías](#6-tecnologías)
7. [Arquitectura general](#7-arquitectura-general)
8. [Modelo de datos](#8-modelo-de-datos)
9. [Endpoints de la API](#9-endpoints-de-la-api)
10. [Estructura de carpetas](#10-estructura-de-carpetas)
11. [Reparto de tareas](#11-reparto-de-tareas)
12. [Cronograma día a día](#12-cronograma-día-a-día)
13. [Proceso de calidad (tomado de la monografía como guía)](#13-proceso-de-calidad-tomado-de-la-monografía-como-guía)
14. [Qué instalar en cada computadora](#14-qué-instalar-en-cada-computadora)
15. [Riesgos conocidos y cómo los atacamos](#15-riesgos-conocidos-y-cómo-los-atacamos)
16. [Decisiones pendientes](#16-decisiones-pendientes)

---

## 1. De qué se trata el proyecto

En la exposición del curso analizamos el caso **"Asistente Virtual Bancario con IA"**: identificamos
5 requisitos no funcionales (RNF) con la norma **ISO/IEC 25010**, analizamos un conflicto entre dos de
ellos (*trade-off*) y propusimos una arquitectura técnica para cada uno.

El docente nos pidió **construir ese caso de verdad**: una app de banco emulado (inspirada en la banca
móvil del BCP Perú) cuyo asistente con IA **cumpla los 5 RNF de la diapositiva**, implementando lo que
propusimos.

En una frase:

> Un banco emulado (clientes, cuentas, movimientos y tarjetas con datos de prueba) cuyo
> protagonista es un **asistente con IA real**. El asistente responde en ≤ 1,5 s, nunca le pasa datos
> personales al modelo, solo atiende con sesión verificada, permite cambiar de modelo sin cortar
> conversaciones y acierta ≥ 98 % en las operaciones críticas.

**La regla de diseño más importante:** **la IA no toca el dinero.** La IA solo *entiende* qué pidió
el cliente y *redacta* la respuesta. Consultar el saldo, transferir o bloquear una tarjeta lo hace el
backend con código normal contra PostgreSQL, y siempre pide confirmación (biometría o TOTP) antes de
ejecutar algo que cambia datos.

---

## 2. Qué es cada archivo de referencia (y cuál NO es el proyecto)

| Archivo | Qué es | Cómo lo usamos |
|---|---|---|
| `Presentacion_Casos_RNF_corregida (1).pptx` | Nuestra exposición: 5 RNF, trade-off y propuesta técnica | **Es la especificación del proyecto.** Lo que dice ahí es lo que hay que cumplir |
| `teoria_backend.md` | Guía paso a paso de un proyecto anterior (ComparaLO / contador) hecho con FastAPI + PostgreSQL + Supabase | **Es el orden de trabajo del backend.** Seguimos sus pasos con algunos ajustes (ver 13.1) |
| `stitch_asistente_virtual_bancario_ia.zip` | 4 pantallas HTML/Tailwind generadas con Stitch + `DESIGN.md` (colores, tipografías) | **Es la referencia visual y funcional del frontend.** No se copia al 100 %: lo hacemos "a nuestra manera" en React |
| `Monografia plan de calidad .docx` | Monografía de **otra tarea** sobre un banco ficticio ("FinBank Mobile") | **Solo es un ejemplo y una guía** de cómo se escribe un plan de calidad: plantillas de casos de prueba y defectos, matriz de trazabilidad, GitFlow, nomenclatura, puertas de calidad. **Sus RNF, sus números (99.999 %, 5,000 TPS), su stack (Java, Kubernetes, Kafka) y su nombre de banco NO son de este proyecto** |

### Las 4 pantallas de Stitch y lo que le piden al backend

| Pantalla | Funcionalidad |
|---|---|
| **Login seguro + 2FA** | Ingreso con DNI, C.E. o RUC + N.° de tarjeta + clave de 6 dígitos con teclado numérico aleatorio. Segundo factor: token TOTP (estilo Google Authenticator) o biometría. Sesión JWT corta |
| **Posición consolidada** | Cuentas en S/ y US$, CCI, saldo disponible, ocultar saldos, últimos movimientos, accesos rápidos (transferir, pagar, bloquear tarjeta), acceso al asistente IA |
| **Confirmación biométrica** | La IA prepara la operación (monto, destino, titular validado, saldo después del cargo) y el cliente la **autoriza con huella o TOTP**. El core transaccional es el que ejecuta |
| **Chatbot IA** | Consulta de saldo y movimientos, bloqueo de tarjeta con confirmación, preguntas sobre productos (tasas) respondidas con documentos oficiales (RAG), derivación a un asesor humano si la confianza es < 80 %, enmascarado de datos personales visible, respuesta en streaming |

> **Ojo con la numeración:** las etiquetas RF/RNF que aparecen escritas dentro del HTML de Stitch
> (por ejemplo "RNF-03" en el login) **no siempre coinciden** con la numeración de nuestro PPT. La
> numeración oficial es **la del PPT** (sección 3). Al pasar las pantallas a React se corrigen las
> etiquetas.

---

## 3. Los 5 RNF que hay que cumplir

Tal cual están en la diapositiva 2 de nuestra exposición:

| ID | Característica ISO 25010 | Subcaracterística | Requisito y métrica verificable |
|---|---|---|---|
| **RNF-01** | Eficiencia de desempeño | Comportamiento temporal | Respuesta completa en **≤ 1,5 s en el 95 % de las consultas (p95)** |
| **RNF-02** | Seguridad | Confidencialidad | **0 %** de datos personales (cuenta, DNI, tarjeta) enviados al modelo en texto plano. **TLS 1.3** y **AES-256** |
| **RNF-03** | Seguridad | Autenticidad | **100 %** de consultas sobre cuentas con sesión verificada (biometría o MFA); **expira tras 5 min de inactividad** |
| **RNF-04** | Mantenibilidad | Modificabilidad | Actualizar el modelo de IA con **0 conversaciones interrumpidas** |
| **RNF-05** | Adecuación funcional | Corrección funcional | **≥ 98 %** de acierto en intenciones críticas (saldo, transferencia, bloqueo) sobre **1,000 consultas de prueba** |

### Trade-off (diapositiva 3)

**RNF-01 (rapidez) frente a RNF-02 (confidencialidad).** Los modelos más potentes están en la nube de
terceros, y usarlos saca los datos del cliente fuera del banco. Un modelo propio protege los datos,
pero con menos hardware responde más lento. Además, cada control (enmascarar, verificar la sesión,
cifrar) agrega un paso antes de responder.

**Decisión: se prioriza RNF-02.** La velocidad se recupera con un modelo pequeño propio (SLM), caché
de preguntas frecuentes y respuesta en streaming. El enmascarado se hace en dos capas (celular y
servidor), porque el servidor nunca confía en la app.

### Propuesta técnica (diapositiva 4)

| RNF | Propuesta |
|---|---|
| RNF-01 | SLM cuantizado en GPU + caché semántica (Redis) + streaming |
| RNF-02 | Enmascaramiento en cliente y servidor (Microsoft Presidio) + modelo on-premise |
| RNF-03 | OAuth 2.0 con tokens JWT + biometría / MFA |
| RNF-04 | Despliegue Blue-Green del modelo |
| RNF-05 | RAG sobre documentos oficiales + derivación a asesor humano si la confianza es < 80 % |

**Todo lo de esta tabla se implementa.** Eso es lo que el docente va a revisar.

---

## 4. Cómo funciona el chatbot, paso a paso

```
 APP (APK Android)                     BACKEND (FastAPI)                           OLLAMA (Llama local, GPU)
 ──────────────────                    ─────────────────                           ─────────────────────────
 1. El cliente escribe:
    "bloquea mi tarjeta 4557 8912 3456 7890"

 2. CAPA 1 de enmascarado (JS)
    "bloquea mi tarjeta [TARJETA_1]"
    y guarda en el celular
    [TARJETA_1] = ****7890
                        ── HTTPS (TLS 1.3) ──→
                                       3. Verifica el JWT y la inactividad    (RNF-03)
                                          sin sesión, vencida o inactiva > 5 min → 401

                                       4. CAPA 2: Presidio                     (RNF-02)
                                          por si la capa 1 dejó pasar algo
                                          (DNI, CCI, tarjeta, correo, teléfono)

                                       5. ¿Pregunta frecuente en la caché?     (RNF-01)
                                          sí → responde directo, sin IA

                                       6. Clasifica la intención               (RNF-05)
                                          reglas + LLM con salida JSON  ──────────────→  {"intencion":
                                                                         ←──────────────   "bloquear_tarjeta",
                                                                                           "confianza": 0.99}
                                       7. Decide según la confianza:

                                          ≥ 0.80 y CRÍTICA (saldo, movimientos,
                                          transferencia, bloqueo)
                                            → servicio normal contra PostgreSQL
                                            → si cambia datos: crea una ACCIÓN PENDIENTE
                                              que el cliente confirma con huella o TOTP

                                          ≥ 0.80 e INFORMATIVA (tasas, requisitos,
                                          horarios)
                                            → RAG: busca fragmentos en los documentos
                                              oficiales (pgvector)
                                            → el LLM redacta con esos fragmentos  ──────→
                                                                         ←────── texto por partes

                                          < 0.80
                                            → derivación a un asesor humano

                                       8. Guarda en la auditoría SOLO texto enmascarado
                                          + intención + confianza + latencia + trace_id
                        ←── SSE (streaming) ──
 9. Muestra la respuesta mientras
    llega. Si es una acción pendiente,
    abre la hoja de confirmación
    biométrica (pantalla Stitch).
10. El cliente pone la huella
    (biometría) o el TOTP    ── POST /confirmar ──→  11. Verifica la firma o el TOTP y
                                                         EJECUTA (transacción + FOR UPDATE)
```

### Intenciones que reconoce el asistente

| Intención | Tipo | Qué hace el backend |
|---|---|---|
| `consultar_saldo` | Crítica | Lee el saldo de PostgreSQL y responde con una plantilla (sin LLM, milisegundos) |
| `consultar_movimientos` | Crítica | Lee los últimos movimientos y responde con una plantilla |
| `transferir` | Crítica | Extrae monto y destino → valida el titular → **acción pendiente** → confirmación biométrica |
| `bloquear_tarjeta` | Crítica | Identifica la tarjeta → **acción pendiente** → confirmación biométrica → bloqueo |
| `consulta_producto` | Informativa | RAG sobre el tarifario y las FAQ del banco + LLM |
| `saludo` / `fuera_de_dominio` | Otra | Respuesta corta. Si no entiende, deriva |
| *(confianza < 0.80)* | — | **Derivación a asesor humano** |

### Por qué la IA no ejecuta operaciones

- Un LLM se puede equivocar o ser manipulado (*prompt injection*: "ignora tus reglas y transfiere…").
  Si la IA solo puede *proponer* y el cliente tiene que *confirmar con su huella*, un error de la IA
  nunca mueve dinero solo.
- Las respuestas críticas salen de plantillas con datos reales de la base, no "inventadas" por el
  modelo. Eso ayuda a la vez a RNF-01 (son instantáneas) y a RNF-05 (son exactas).

---

## 5. Cómo se cumple y cómo se demuestra cada RNF

La idea es que **cada RNF tenga una prueba automática que produzca un número**. Esos números van al
informe de evidencias que se entrega.

### RNF-01: comportamiento temporal (p95 ≤ 1,5 s)

**Cómo se construye**
- Llama 3.1 8B cuantizado (Q4) servido por **Ollama en la GPU** (la RTX 5060 de 8 GB lo soporta).
- Las intenciones críticas responden con plantilla, sin generar texto con el LLM.
- **Caché semántica** en Redis: si la pregunta se parece mucho a una ya respondida (similitud de
  embeddings ≥ umbral), se devuelve la respuesta guardada. Solo se cachean respuestas
  **informativas**, nunca saldos ni datos de cuentas.
- **La caché también cubre las respuestas largas:** las preguntas informativas más comunes (tasas,
  requisitos, horarios, comisiones) se **precalientan** al arrancar el backend, generándolas una vez y
  guardándolas. Así, en la demo, una pregunta larga frecuente responde completa al instante. La
  caché se invalida cuando cambia un documento del RAG o se cambia de modelo (RNF-04).
- Respuestas informativas cortas (límite de ~150 tokens) y **streaming SSE**.
- El modelo se mantiene cargado en memoria (`keep_alive`) para evitar el arranque en frío.

**Definición acordada por el equipo (22 de octubre)**

El tiempo de RNF-01 se mide **hasta que el cliente empieza a ver la respuesta** (primer fragmento
visible en pantalla). En la exposición se muestran dos tipos de respuesta:

| Tipo | Ejemplo | Qué pasa | Meta |
|---|---|---|---|
| **Corta** (intenciones críticas) | "¿Cuánto tengo?" | Sale de PostgreSQL con plantilla, sin LLM. La respuesta **completa** llega en ~0,3 s | Completa ≤ 1,5 s ✅ |
| **Larga** (preguntas específicas, RAG) | "¿Qué tasa tiene el plazo fijo y qué requisitos pide?" | El LLM escribe palabra por palabra. **Empieza a verse rápido** y termina un poco después | Primer fragmento ≤ 1,5 s ✅; el tiempo total se reporta aparte |
| **Larga repetida** (está en la caché) | La misma pregunta, u otra muy parecida, de nuevo | Se devuelve la respuesta guardada, sin pasar por el LLM | Completa ≤ 1,5 s ✅ |

Mensaje para la exposición: *"Las consultas cortas cumplen RNF-01 completas. Las preguntas más
específicas empiezan a mostrarse dentro de 1,5 s y terminan de escribirse un poco después; si ya se
preguntaron antes, la caché las devuelve completas al instante."*

**Cómo se mide**
- Cada mensaje registra **dos tiempos**: `ttft_ms` (hasta el primer fragmento, *time to first token*)
  y `latencia_total_ms` (hasta el evento `done`). Además se registra si vino de plantilla, de caché
  o del LLM.
- **k6** lanza la mezcla real de consultas (críticas + informativas nuevas + informativas repetidas) y
  reporta:
  - **p95 de `ttft_ms` ≤ 1500 ms** → criterio de cumplimiento de RNF-01.
  - p95 de `latencia_total_ms` **por tipo** (corta, larga, caché) → para mostrar la diferencia.
  - Porcentaje de aciertos de la caché.
- **Evidencia:** reporte de k6 + tabla por tipo de respuesta.

> Como la diapositiva dice "respuesta completa", en el informe y en la exposición se aclara
> explícitamente la definición usada (primer fragmento visible) y se muestran también los tiempos
> totales. Así nadie puede decir que se cambió la métrica a escondidas.

### RNF-02: confidencialidad (0 % de datos personales al modelo, TLS 1.3, AES-256)

**Cómo se construye**
- **Capa 1 (frontend):** expresiones regulares que reemplazan DNI, CCI, N.° de tarjeta, correo y
  teléfono por marcadores (`[DNI_1]`, `[TARJETA_1]`) antes de enviar.
- **Capa 2 (backend):** **Microsoft Presidio** con modelo de spaCy en español y **reconocedores
  propios para Perú**:
  - DNI: 8 dígitos (con contexto "dni", "documento").
  - CCI: 20 dígitos.
  - Tarjeta: 13 a 19 dígitos que pasan el **algoritmo de Luhn**.
  - Número de cuenta con el formato del banco (`193-XXXXXXXX-X-XX`).
- El LLM corre **en local** (Ollama): ningún texto sale de la máquina.
- **AES-256 en reposo:** los campos sensibles (N.° de documento, secreto TOTP) se cifran con
  **AES-256-GCM** (librería `cryptography`) antes de guardarse. Además, Supabase cifra el disco.
- Las tarjetas se guardan solo como los últimos 4 dígitos + hash, nunca el número completo.
- **TLS 1.3:** un proxy **Caddy** delante del backend, configurado para aceptar solo TLS 1.3.
- Los logs nunca contienen datos personales: un filtro de logging enmascara antes de escribir.

**Cómo se mide**
- `tests/rnf/test_rnf02_pii.py`: **200 mensajes llenos de datos personales**. Se intercepta lo que le
  llega al cliente de Ollama y se verifica que no aparezca ningún dato original. **Un solo dato filtrado
  = la prueba falla.**
- Una prueba que confirma que los campos cifrados en la base no son legibles.
- `openssl s_client -tls1_2` contra el servidor **debe fallar**, y con `-tls1_3` debe conectar.
- **Evidencia:** reporte de pytest + captura de las pruebas de TLS.

### RNF-03: autenticidad (100 % con sesión verificada, expira a los 5 min inactivo)

**Cómo se construye**
- Login: documento + N.° de tarjeta + clave de 6 dígitos (hash **Argon2**). Teclado aleatorio
  generado por el servidor.
- **MFA obligatorio:** TOTP con `pyotp` (compatible con Google Authenticator) **o** biometría con
  **huella nativa de Android** (plugin de Capacitor + clave del dispositivo que firma un desafío con
  HMAC-SHA256; ver 6.4).
- Flujo OAuth 2.0 *password + MFA* que entrega un **JWT de vida corta** firmado (HS256 o RS256).
- **Inactividad:** cada petición renueva una clave en Redis con TTL de 300 s. Si la clave no existe,
  la sesión murió aunque el JWT siga vigente → 401.
- **Step-up:** las acciones críticas del chat (transferir, bloquear) piden **otra vez** huella o TOTP.
- Bloqueo tras 3 intentos fallidos + *rate limiting* en el login (`slowapi`).
- **Todos** los endpoints de cuentas y del chat dependen de `usuario_actual`.

**Cómo se mide**
- `tests/rnf/test_rnf03_auth.py`: sin token, con token vencido, con token manipulado, con 5 min de
  inactividad simulada, sin MFA completado → **todos 401**.
- Una prueba que recorre **todas las rutas** de la app y verifica que ninguna ruta de datos responde
  sin token (100 %).
- **Evidencia:** reporte de pytest.

### RNF-04: modificabilidad (cambiar el modelo con 0 conversaciones interrumpidas)

**Cómo se construye: Blue-Green del modelo**
- Tabla `modelo_ia` con dos registros: **azul** (versión actual) y **verde** (versión nueva). Uno está
  marcado como `activo`.
- Cada conversación **guarda con qué versión empezó** (`id_modelo`).
  - Las conversaciones **nuevas** usan el modelo activo.
  - Las que estaban **en curso terminan con el modelo con el que empezaron** (drenado).
- Endpoint de administración `POST /api/v1/admin/modelo/activar`: se prueba el verde y se cambia el
  tráfico. Si algo falla, se vuelve al azul con el mismo endpoint (**reversión inmediata**).
- Antes de activar el verde se corre una **prueba de humo** automática (un set corto de consultas).

**Cómo se mide**
- Un script (k6 o Python) mantiene **50 conversaciones con streaming abiertas** y, a mitad de camino,
  hace el cambio azul → verde.
- Criterio: las 50 terminan con su evento `done` y sin errores = **0 interrumpidas**. Las nuevas
  conversaciones arrancan con el verde.
- **Evidencia:** log del script + reporte.

> ⚠️ Riesgo de VRAM: dos modelos 8B no entran juntos en 8 GB. Opciones: (a) que la "versión nueva" sea
> el mismo modelo base con un Modelfile mejorado (prompt de sistema y parámetros), (b) usar modelos de
> 3B para la demostración del cambio. Se prueba el **26 de octubre**.

### RNF-05: corrección funcional (≥ 98 % de acierto en intenciones críticas)

**Cómo se construye**
- **Clasificador híbrido:**
  1. Reglas para lo inequívoco ("bloquea" + "tarjeta", "cuánto tengo", "transferir S/ 100 a…").
  2. Si las reglas no deciden, el LLM con **salida JSON estructurada** `{intencion, confianza,
     entidades}` y temperatura 0.
- **Confianza < 0.80 → derivación a un asesor humano** (tabla `derivacion` + panel mínimo de asesor).
- **RAG** para las preguntas informativas: documentos oficiales del banco ficticio (tarifario de tasas,
  FAQ, condiciones de las cuentas) divididos en fragmentos, con embeddings **bge-m3** (multilingüe,
  vía Ollama) y búsqueda con **pgvector** dentro de Supabase. La respuesta cita la fuente.

**Cómo se mide**
- **Dataset `qa/dataset/consultas_1000.jsonl`**: 1,000 consultas etiquetadas. Distribución propuesta:
  300 de saldo y movimientos, 250 de transferencias, 250 de bloqueo y 200 informativas o fuera de
  dominio. Con variaciones reales: faltas de ortografía, jerga peruana ("cuánta plata tengo", "se me
  perdió la tarjeta"), mensajes largos y cortos.
- **Separación para no hacer trampa:** 300 consultas de *desarrollo* (para ajustar reglas y prompt) y
  **700 de *prueba*** que nadie mira mientras ajusta. **El 98 % se reporta sobre las 700.**
- El script `qa/evaluar_intenciones.py` calcula el acierto global, la precisión y el recall por
  intención, la **matriz de confusión** y cuántas consultas se derivaron.
- **Evidencia:** reporte del script con acierto ≥ 98 % en intenciones críticas.

**Definición acordada por el equipo (22 de octubre): la derivación a un humano cuenta como acierto**

Cuando el asistente no está seguro (confianza < 0.80) y deriva al asesor, **resolvió bien la
situación**: no adivinó con el dinero del cliente. Por eso:

| Resultado de una consulta | ¿Cuenta como acierto? |
|---|---|
| Reconoció la intención correcta (confianza ≥ 0.80) | ✅ Sí |
| No estaba seguro y derivó a un asesor humano (confianza < 0.80) | ✅ Sí |
| Se equivocó de intención con confianza ≥ 0.80 (por ejemplo, tomó un bloqueo como consulta de saldo) | ❌ No: **este es el único error** |

```
acierto RNF-05 = (correctas + derivadas) / total de consultas críticas del set de prueba  ≥ 98 %
```

**Control para que el número sea honesto:** con esta regla, un bot que derivara *todo* tendría 100 %.
Por eso el informe muestra también:
- **% de derivación**, con una meta de **≤ 5 %**. Un asistente que deriva demasiado no sirve.
- El acierto **sin** contar derivaciones, como dato informativo.

Ejemplo de cómo se ve en el informe (700 consultas de prueba):

| Correctas | Derivadas | Errores | Acierto RNF-05 | % derivación | Acierto sin derivaciones |
|---|---|---|---|---|---|
| 680 | 12 | 8 | **98,9 %** ✅ | 1,7 % ✅ | 97,1 % |

---

## 6. Tecnologías

### 6.1 La base: FastAPI + PostgreSQL + Supabase ✅ (se mantiene)

Es una buena elección para este proyecto y es la que explica `teoria_backend.md`:

- **FastAPI:** asíncrono (aguanta el streaming del chat), valida con Pydantic y genera `/docs` solo.
  Con eso el frontend integra sin manual.
- **PostgreSQL:** transacciones ACID y `SELECT … FOR UPDATE` para que el dinero nunca quede
  inconsistente.
- **Supabase:** nos da el PostgreSQL en la nube, compartido por los 3, **y además trae `pgvector`**
  para el RAG. No hace falta otra base de datos de vectores.

**Cómo usamos Supabase:** igual que en el proyecto anterior, **solo como hosting de PostgreSQL**
(cadena de conexión). **No usamos Supabase Auth.** La autenticación (RNF-03) la construimos y la
probamos nosotros; si la hiciera Supabase, no podríamos demostrar el RNF.

### 6.2 Lo que hay que agregar (y por qué)

| Necesidad | Tecnología | Para qué RNF |
|---|---|---|
| Servir el LLM local | **Ollama** + `llama3.1:8b` (cuantizado Q4) | RNF-01, RNF-02 |
| Embeddings para el RAG | **bge-m3** vía Ollama (buen español) | RNF-05 |
| Búsqueda de vectores | **pgvector** (extensión de Supabase) + paquete `pgvector` para SQLAlchemy | RNF-05 |
| Enmascarar datos personales | **Microsoft Presidio** (analyzer + anonymizer) + spaCy `es_core_news_md` | RNF-02 |
| Caché semántica, inactividad de sesión, idempotencia | **Redis** | RNF-01, RNF-03 |
| Streaming del chat | **SSE** (`sse-starlette`) | RNF-01 |
| Hash de claves | **Argon2** (`pwdlib[argon2]`) | RNF-03 |
| JWT | **PyJWT** | RNF-03 |
| TOTP | **pyotp** (+ `qrcode` para enrolar el token) | RNF-03 |
| Biometría | Plugin de **biometría nativa de Capacitor** + desafío firmado con HMAC-SHA256 (ver 6.4) | RNF-03 |
| Límite de intentos | **slowapi** | RNF-03 |
| Cifrado AES-256 de campos | **cryptography** (AES-256-GCM) | RNF-02 |
| Proxy HTTPS solo TLS 1.3 | **Caddy** | RNF-02 |
| Exponer la demo con HTTPS a los celulares | **Cloudflare Tunnel** (`cloudflared`) | RNF-02 (Android bloquea HTTP sin cifrar en el APK) |
| Contenedores | **Docker Desktop** + `docker compose` (Redis, Caddy, backend) | Todos |
| Logs con trace_id y sin PII | **structlog** | RNF-02, trazabilidad |
| Métricas de latencia | `prometheus-fastapi-instrumentator` (opcional) | RNF-01 |

### 6.3 Calidad y pruebas

| Herramienta | Uso |
|---|---|
| **pytest** + `pytest-asyncio` + **httpx** | Pruebas unitarias y de integración |
| **pytest-cov** | Cobertura (meta ≥ 80 % en el backend) |
| **schemathesis** | Pruebas automáticas contra el OpenAPI de `/docs` (casos raros que nadie pensó) |
| **ruff** | Estilo y errores comunes (linter + formateador) |
| **radon** | Complejidad ciclomática (V(G) ≤ 10 por función, como en la monografía) |
| **bandit** + **pip-audit** | Análisis estático de seguridad y dependencias vulnerables |
| **SonarQube Cloud** (opcional) | Panel de calidad del código para mostrar en la exposición |
| **k6** | Carga y latencia (RNF-01) y conversaciones durante el cambio de modelo (RNF-04) |
| **Playwright** + **@axe-core/playwright** | Pruebas de punta a punta del frontend + accesibilidad WCAG |
| **Vitest** | Pruebas unitarias del frontend (por ejemplo, el enmascarado de la capa 1) |
| **GitHub Actions** | CI: en cada pull request corre ruff, pytest, cobertura, bandit y el build del frontend |
| **pre-commit** | Corre ruff antes de cada commit, en local |

### 6.4 Frontend (decidido)

**React + Vite + TypeScript + Tailwind, empaquetado como APK de Android con Capacitor**:

- Se desarrolla como web normal (Vite, en el navegador, con recarga rápida) **todo el proyecto**.
- **Capacitor** (de Ionic) envuelve esa misma app web en una **app nativa de Android (APK)**. No se
  reescribe nada: `npm run build` → `npx cap sync android` → se compila el APK.
- El APK se instala en el celular como cualquier app, con su ícono, y se usa en la exposición
  duplicando la pantalla con **scrcpy** (ver sección 6.5).
- **Huella:** dentro de un APK, WebAuthn no funciona bien (el WebView de Android no lo soporta). Se
  usa en su lugar un **plugin de biometría nativa de Capacitor** que abre el diálogo de huella real de
  Android (BiometricPrompt). Para que el backend no "confíe en la palabra" de la app:
  1. Al registrar el dispositivo, el backend le entrega una **clave del dispositivo** que la app guarda
     protegida por la huella (almacenamiento seguro de Android).
  2. Al autorizar una operación, el backend manda un **desafío** (número aleatorio de un solo uso).
  3. El cliente pone la huella → la app desbloquea la clave y firma el desafío con **HMAC-SHA256**.
  4. El backend verifica la firma. Sin huella no hay clave, y sin clave no hay firma válida.
  (El plugin exacto se elige en la tarea F-02; tiene que permitir proteger un secreto con la huella.)
- **TOTP** (Google Authenticator) queda siempre como alternativa a la huella.
- Durante el desarrollo en el navegador, la "huella" se simula con un botón (solo en modo
  desarrollo) y el TOTP funciona igual.

- Las pantallas de Stitch ya están en Tailwind: se pasan casi directo a componentes. Los colores y
  tipografías del `DESIGN.md` van al `tailwind.config`.
- **React Router** para la navegación, **TanStack Query** para las llamadas a la API y **Zod** para
  validar formularios.
- El streaming se lee con `fetch` + `ReadableStream`. `EventSource` no sirve porque no permite mandar
  el header `Authorization`.
- La URL del backend va en una variable (`VITE_API_URL`). En el APK apunta a la dirección HTTPS del
  Cloudflare Tunnel, porque Android bloquea las conexiones HTTP sin cifrar.
- CORS del backend: además de `http://localhost:5173` (Vite), se permite el origen del WebView de
  Capacitor (`https://localhost`; se confirma al configurar Capacitor).

### 6.5 La demo en la exposición (decidido)

Igual que lo hizo un compañero en otro curso:

1. El **APK está instalado** en un celular **Android** y la app ya está abierta con la sesión lista.
2. El celular se conecta por **cable USB-C** a la laptop.
3. **scrcpy** (gratis, sin instalar nada en el celular) duplica la pantalla del celular en la laptop,
   y la laptop va al proyector. Todo el salón ve lo que se hace en el celular, incluido el diálogo de
   la huella.
4. La laptop con la RTX 5060 corre el backend, Ollama, Redis y el tunnel al mismo tiempo.

**Preparación (una sola vez):** en el celular, activar *Opciones de desarrollador* (tocar 7 veces
"Número de compilación" en *Ajustes → Acerca del teléfono*) y luego activar *Depuración USB*. Al
conectar el cable, aceptar el aviso "¿Permitir depuración USB?".

**Plan B:** si falla el cable o el celular, la misma app corre en el navegador de la laptop con el
modo celular de Chrome (F12 → ícono de celular). La huella se reemplaza por TOTP.

> El APK solo funciona en **Android**. Si el celular de la demo es un iPhone, hay que usar el de otro
> integrante.

### 6.6 ¿Hace falta algo "más avanzado" que FastAPI + PostgreSQL + Supabase?

**No para la base.** Lo "avanzado" del proyecto está en las piezas de la sección 6.2 (Ollama, Presidio,
pgvector, Redis, biometría), no en cambiar el framework. Cosas que **no** recomendamos para 12 días:

- **Kubernetes, Kafka, microservicios:** son de la monografía de ejemplo y no se pueden montar ni
  probar bien en este plazo.
- **LangChain / LlamaIndex:** agregan una capa grande para algo que son ~100 líneas propias (llamar a
  Ollama, buscar en pgvector, armar el prompt). Además, el código propio es más fácil de probar y de
  explicar en la exposición.
- **Modelos en la nube (OpenAI, etc.):** violan directamente RNF-02 y el trade-off que defendimos.

**Opcional:** `uv` en vez de `pip` para instalar dependencias más rápido y con archivo de bloqueo.
La guía usa `pip` + `venv` y eso funciona bien; solo cambiar si el equipo lo prefiere.

---

## 7. Arquitectura general

```
   Celular Android (APK: React + Capacitor)
              │  HTTPS, TLS 1.3
              ▼
   ┌──────────────────────┐
   │  Cloudflare Tunnel   │  ← solo para la demo (URL pública con HTTPS)
   └──────────┬───────────┘
              ▼
   ┌──────────────────────┐
   │  Caddy (proxy)       │  ← termina TLS 1.3, sirve el frontend compilado y pasa /api al backend
   └──────────┬───────────┘
              ▼
   ┌──────────────────────────────────────────────┐
   │  Backend FastAPI                             │
   │   routers/  → auth, cuentas, tarjetas,       │
   │               transferencias, chat, asesor,  │
   │               admin                          │
   │   services/ → lógica bancaria                │
   │   services/ia/ → enmascarado, clasificador,  │
   │                  rag, llm, cache, orquestador│
   └────┬──────────────┬────────────────┬─────────┘
        │              │                │
        ▼              ▼                ▼
   ┌─────────┐   ┌──────────┐   ┌────────────────────────┐
   │  Redis  │   │  Ollama  │   │  Supabase (PostgreSQL) │
   │ caché,  │   │ llama3.1 │   │  datos del banco,      │
   │ sesión, │   │ bge-m3   │   │  auditoría, pgvector   │
   │ idemp.  │   │ (GPU)    │   │                        │
   └─────────┘   └──────────┘   └────────────────────────┘
```

**Dónde corre cada cosa durante el desarrollo:**

- **Ollama solo corre bien en la laptop con la RTX 5060.** El otro integrante de backend tiene tres
  opciones:
  1. Apuntar `OLLAMA_URL` a la laptop con GPU por la red local o por Tailscale.
  2. Usar `llama3.2:3b` en su propia máquina para desarrollar.
  3. Usar el **LLM falso** de las pruebas (ver abajo).
- **Las pruebas de pytest nunca llaman al LLM real:** usan un `LLMFalso` que devuelve respuestas fijas.
  Así el CI de GitHub corre sin GPU. Las evaluaciones con el LLM real (RNF-05 y la latencia de RNF-01)
  se corren en la laptop con GPU.

---

## 8. Modelo de datos

Siguiendo la convención de la monografía (como guía): **tablas en singular**, clave primaria
`id_<tabla>` y campos de auditoría en todas las tablas: `created_at`, `updated_at`, `created_by`,
`is_active`. **Dinero siempre `NUMERIC(14,2)`, nunca `float`.** Fechas siempre `TIMESTAMPTZ`.

| Tabla | Campos principales | Notas |
|---|---|---|
| `cliente` | id_cliente, tipo_documento (DNI/CE/RUC), documento_cifrado, documento_hash, nombres, apellidos, email, telefono | El documento va cifrado con AES-256 y se busca por su hash |
| `credencial` | id_credencial, id_cliente, tarjeta_hash, clave_hash (Argon2), totp_secreto_cifrado, intentos_fallidos, bloqueado_hasta | Bloqueo tras 3 intentos |
| `dispositivo` | id_dispositivo, id_cliente, nombre, clave_dispositivo_cifrada, ultimo_uso | Celular registrado para la huella (la clave va cifrada con AES-256) |
| `desafio_biometrico` | id_desafio, id_dispositivo, valor, usado, expira_en | Número de un solo uso que la app firma tras la huella |
| `sesion` | id_sesion, id_cliente, jti, metodo_mfa, ultimo_uso, expira_en, revocada | Auditoría de sesiones; la inactividad se controla en Redis |
| `cuenta` | id_cuenta, id_cliente, tipo, moneda (PEN/USD), numero, cci, saldo `CHECK (saldo >= 0)` | |
| `tarjeta` | id_tarjeta, id_cuenta, ultimos4, pan_hash, estado (activa/bloqueo_temporal/bloqueada) | Nunca se guarda el número completo |
| `movimiento` | id_movimiento, id_cuenta, tipo (cargo/abono), monto, descripcion, canal, saldo_resultante | |
| `transferencia` | id_transferencia, id_cuenta_origen, cuenta_destino o cci_destino, titular_destino, monto, moneda, estado, clave_idempotencia `UNIQUE` | Débito y crédito en **una** transacción con `FOR UPDATE` |
| `accion_pendiente` | id_accion, id_conversacion, tipo (transferir/bloquear), datos_json, estado, expira_en | Lo que la IA propone y el cliente confirma |
| `modelo_ia` | id_modelo, nombre, version, color (azul/verde), activo | Blue-Green (RNF-04) |
| `conversacion` | id_conversacion, id_cliente, id_modelo, estado (activa/derivada/cerrada) | Guarda con qué modelo empezó |
| `mensaje` | id_mensaje, id_conversacion, rol, contenido_enmascarado, intencion, confianza, latencia_ms, trace_id | **Solo texto enmascarado** |
| `asesor` | id_asesor, nombres, especialidad | Para la derivación |
| `derivacion` | id_derivacion, id_conversacion, id_asesor, motivo, estado | Confianza < 0.80 (RNF-05) |
| `documento_rag` | id_documento, titulo, fuente, version | Tarifario, FAQ, condiciones |
| `fragmento_rag` | id_fragmento, id_documento, contenido, embedding `vector(1024)` | pgvector, índice HNSW |
| `bitacora_auditoria` | id_bitacora, id_cliente, accion, detalle_json (sin PII), trace_id, ip_hash | Registro de cada operación |

Los datos de prueba se cargan con un script de semilla: clientes de ejemplo como "Carlos", con sus
cuentas en S/ y US$, tarjetas y unos 50 movimientos cada uno.

---

## 9. Endpoints de la API

Todo va bajo `/api/v1`. Sustantivos en plural y códigos HTTP correctos: 200, 201, 400, 401, 403, 404,
409 (idempotencia duplicada), 422 y 429 (demasiados intentos).

**Autenticación (RNF-03)**
```
GET    /api/v1/auth/teclado                         → orden aleatorio del teclado numérico
POST   /api/v1/auth/login                           → documento + tarjeta + clave → token temporal "mfa_pendiente"
POST   /api/v1/auth/mfa/totp                        → verifica TOTP → JWT de sesión
POST   /api/v1/auth/mfa/totp/enrolar                → genera el secreto + QR
POST   /api/v1/auth/dispositivos                    → registra el celular y entrega su clave (requiere TOTP)
POST   /api/v1/auth/biometria/desafio               → número aleatorio de un solo uso
POST   /api/v1/auth/biometria/verificar             → firma HMAC del desafío → JWT de sesión / step-up
POST   /api/v1/auth/logout
```

**Banco**
```
GET    /api/v1/cuentas                              → posición consolidada
GET    /api/v1/cuentas/{id_cuenta}/movimientos?limite=&desde=
GET    /api/v1/tarjetas
POST   /api/v1/tarjetas/{id_tarjeta}/bloqueo        → requiere step-up (huella/TOTP)
GET    /api/v1/transferencias/titular?cci=          → nombre del titular destino
POST   /api/v1/transferencias                       → header X-Idempotency-Key, requiere step-up
```

**Asistente IA**
```
POST   /api/v1/chat/conversaciones                  → crea una conversación (con el modelo activo)
POST   /api/v1/chat/conversaciones/{id}/mensajes    → responde en STREAMING (SSE)
POST   /api/v1/chat/acciones/{id_accion}/confirmar  → huella o TOTP → ejecuta la acción
GET    /api/v1/chat/conversaciones/{id}             → historial (enmascarado)
```

**Asesor y administración**
```
GET    /api/v1/asesor/derivaciones                  → bandeja del asesor humano
POST   /api/v1/asesor/derivaciones/{id}/mensajes
GET    /api/v1/admin/modelos
POST   /api/v1/admin/modelos/{id_modelo}/activar    → cambio Blue-Green (RNF-04)
GET    /health                                      → {"ok": true}
```

**Formato del streaming** (eventos SSE):
```
event: meta     data: {"intencion":"consultar_saldo","confianza":0.99,"trace_id":"..."}
event: token    data: {"texto":"Tu Cuenta Simple"}
event: token    data: {"texto":" en Soles tiene..."}
event: accion   data: {"id_accion":"...","tipo":"bloquear_tarjeta","resumen":{...}}
event: derivar  data: {"asesor":"Martín Alvarado"}
event: done     data: {"latencia_ms":820}
```

---

## 10. Estructura de carpetas

Un **solo repositorio (monorepo)** para los 3. A diferencia del proyecto anterior (que separó
frontend y backend), así el CI, los documentos y las evidencias quedan en un solo lugar, y un PR puede
tocar las dos partes cuando cambia el contrato de la API.

```
banco-asistente-ia/
├── backend/
│   ├── app/
│   │   ├── main.py              ← crea la app, CORS, middlewares, routers
│   │   ├── config.py            ← variables de entorno (pydantic-settings)
│   │   ├── database.py          ← motor async + get_db
│   │   ├── seguridad/           ← jwt, argon2, totp, biometría (desafíos), cifrado AES, inactividad
│   │   ├── models/              ← una tabla por archivo (SQLAlchemy)
│   │   ├── schemas/             ← Pydantic: *Crear / *Salida
│   │   ├── routers/             ← auth, cuentas, tarjetas, transferencias, chat, asesor, admin
│   │   ├── services/            ← lógica bancaria
│   │   │   └── ia/
│   │   │       ├── enmascarado.py   ← Presidio + reconocedores peruanos (RNF-02)
│   │   │       ├── clasificador.py  ← reglas + LLM JSON (RNF-05)
│   │   │       ├── rag.py           ← pgvector + bge-m3 (RNF-05)
│   │   │       ├── llm.py           ← cliente Ollama + LLMFalso para pruebas
│   │   │       ├── cache.py         ← caché semántica Redis (RNF-01)
│   │   │       ├── modelos.py       ← registro Blue-Green (RNF-04)
│   │   │       └── orquestador.py   ← junta todo el flujo de la sección 4
│   │   └── middleware/          ← trace_id, latencia, logging sin PII
│   ├── alembic/                 ← migraciones (incluye CREATE EXTENSION vector)
│   ├── scripts/semilla.py       ← datos de prueba del banco
│   ├── docs_rag/                ← tarifario, FAQ, condiciones (Markdown)
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── rnf/                 ← test_rnf02_pii.py, test_rnf03_auth.py, ...
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/                    ← React + Vite + TS + Tailwind + Capacitor (APK)
│   ├── src/
│   └── tests/                   ← Playwright + Vitest
├── qa/
│   ├── dataset/consultas_1000.jsonl
│   ├── evaluar_intenciones.py   ← RNF-05
│   └── k6/                      ← rnf01_latencia.js, rnf04_bluegreen.js
├── infra/
│   ├── docker-compose.yml       ← redis, caddy, backend
│   └── Caddyfile                ← solo TLS 1.3
├── docs/
│   ├── CONTENIDO_BACKEND_BANCO.md
│   ├── matriz_trazabilidad.md
│   └── evidencias/              ← reportes de cada RNF para la entrega
├── .github/
│   ├── workflows/ci.yml
│   ├── ISSUE_TEMPLATE/defecto.md
│   └── pull_request_template.md
├── .gitignore
└── README.md
```

---

## 11. Reparto de tareas

### El día 1 se trabaja junto: el contrato

Antes de separarse, los 3 acuerdan **el modelo de datos (sección 8) y los endpoints (sección 9)**, y
Backend 1 publica **endpoints falsos (mocks)** que devuelven datos inventados (Parte 4 de
`teoria_backend.md`). Así el frontend empieza a trabajar de inmediato sin esperar al backend real.

También se fija la **interfaz interna** entre los dos backends, para que el asistente (Backend 2) use
la lógica bancaria (Backend 1) sin pisarse:

```python
# services/cuentas.py      (lo hace Backend 1, lo usa Backend 2)
async def obtener_cuentas(db, id_cliente) -> list[CuentaSalida]: ...
async def obtener_movimientos(db, id_cuenta, limite) -> list[MovimientoSalida]: ...


# services/acciones.py
async def crear_accion_pendiente(db, id_conversacion, tipo, datos) -> AccionPendiente: ...
async def ejecutar_accion(db, id_accion, prueba_mfa) -> ResultadoAccion: ...


# services/ia/modelos.py
async def modelo_para_conversacion(db, id_conversacion) -> ModeloIA: ...
```

### Backend 1: core bancario, seguridad e infraestructura

**Dueño de: RNF-03 (autenticidad) y RNF-04 (Blue-Green).** También es responsable de AES-256 y TLS 1.3
dentro de RNF-02.

| # | Tarea |
|---|---|
| B1-01 | Repositorio, ramas protegidas, `.gitignore`, `.env.example`, `requirements.txt`, estructura de carpetas |
| B1-02 | Proyecto Supabase, `config.py`, `database.py`, Alembic (incluida la extensión `vector`) |
| B1-03 | Modelos SQLAlchemy de las tablas del banco + migración inicial + script de semilla |
| B1-04 | Endpoints mock para el frontend (día 1) |
| B1-05 | Login: Argon2, teclado aleatorio, bloqueo tras 3 intentos, `slowapi` |
| B1-06 | MFA TOTP (`pyotp`) + enrolamiento con QR |
| B1-07 | JWT + dependencia `usuario_actual` + inactividad de 5 min en Redis |
| B1-08 | Biometría del dispositivo: registro de la clave del dispositivo, desafío y verificación HMAC-SHA256 (login + step-up) |
| B1-09 | Cuentas, movimientos, tarjetas, bloqueo |
| B1-10 | Transferencias: validación del titular, `X-Idempotency-Key`, transacción única con `FOR UPDATE` |
| B1-11 | Acciones pendientes + confirmación con step-up (las que crea el chat) |
| B1-12 | Cifrado AES-256-GCM de campos sensibles + bitácora de auditoría |
| B1-13 | Registro de modelos Blue-Green + endpoint de activación + drenado (RNF-04) |
| B1-14 | Docker Compose (Redis, Caddy, backend) + Caddyfile con solo TLS 1.3 + Cloudflare Tunnel |
| B1-15 | CI en GitHub Actions (ruff, pytest, cobertura, bandit, pip-audit) |
| B1-16 | Pruebas: `test_rnf03_auth.py`, prueba de cifrado y de TLS, prueba de transferencias concurrentes |

### Backend 2: asistente con IA

**Dueño de: RNF-01 (latencia), RNF-02 (enmascarado en el servidor) y RNF-05 (corrección).**

| # | Tarea |
|---|---|
| B2-01 | Instalar Ollama, descargar `llama3.1:8b` y `bge-m3`, **medir la latencia real** (día 2–3) |
| B2-02 | `llm.py`: cliente de Ollama con streaming + `LLMFalso` para las pruebas |
| B2-03 | `enmascarado.py`: Presidio + spaCy en español + reconocedores de DNI, CCI, tarjeta (Luhn) y cuenta |
| B2-04 | `test_rnf02_pii.py` con 200 mensajes con datos personales |
| B2-05 | `clasificador.py`: reglas + LLM con salida JSON + umbral 0.80 |
| B2-06 | **Dataset de 1,000 consultas** etiquetadas (separado en desarrollo y prueba) |
| B2-07 | `qa/evaluar_intenciones.py`: acierto, matriz de confusión y reporte |
| B2-08 | Documentos del banco para el RAG (tarifario, FAQ, condiciones) + carga en `fragmento_rag` |
| B2-09 | `rag.py`: búsqueda con pgvector + prompt que obliga a citar la fuente |
| B2-10 | `cache.py`: caché semántica en Redis (solo respuestas informativas) |
| B2-11 | `orquestador.py` + endpoint del chat con SSE (todo el flujo de la sección 4) |
| B2-12 | Derivación a asesor humano + endpoints del asesor |
| B2-13 | Middleware de latencia + ajuste hasta cumplir p95 ≤ 1,5 s |
| B2-14 | Ajustar el clasificador hasta ≥ 98 % (sin mirar el set de prueba) |

### Frontend: React + APK + pruebas de interfaz y carga

**Dueño de: la capa 1 de RNF-02, la interfaz de RNF-03 y la medición con k6 de RNF-01 y RNF-04.**

| # | Tarea |
|---|---|
| F-01 | Proyecto Vite + React + TS + Tailwind con los colores y tipografías del `DESIGN.md` de Stitch |
| F-02 | Pantalla de login + teclado aleatorio + MFA (TOTP + elegir y probar el plugin de huella de Capacitor) |
| F-03 | Pantalla de posición consolidada + movimientos + ocultar saldos |
| F-04 | Pantalla del chat: lectura del streaming, burbujas, chips de enmascarado, derivación |
| F-05 | Hoja de confirmación biométrica (acciones pendientes del chat) |
| F-06 | **Capa 1 de enmascarado** en JS + pruebas con Vitest |
| F-07 | Cierre de sesión por inactividad (aviso y salida a los 5 min) |
| F-08 | Panel mínimo del asesor humano |
| F-09 | Capacitor: proyecto Android, ícono, APK firmado, prueba en el celular real + ensayo con scrcpy |
| F-10 | Pruebas Playwright de los flujos principales + accesibilidad con axe |
| F-11 | Scripts k6: `rnf01_latencia.js` y `rnf04_bluegreen.js` |

> **Equilibrio de carga:** Backend 2 tiene la parte más incierta (la IA). Si se atrasa, Backend 1 toma
> B2-10 (caché) y B2-12 (derivación), que no dependen del modelo.

---

## 12. Cronograma día a día

Hoy es jueves 22 de octubre. La entrega es el martes 3 de noviembre: **12 días**.

| Fecha | Backend 1 | Backend 2 | Frontend |
|---|---|---|---|
| **Jue 22** | **Los 3 juntos:** leer este documento, acordar el modelo de datos y los endpoints, instalar todo (sección 14) | ← | ← |
| **Vie 23** | B1-01, B1-02, B1-04 (mocks) | B2-01 (Ollama + medir latencia), B2-02 | F-01, empezar F-02 con los mocks |
| **Sáb 24** | B1-03 (modelos + semilla), B1-05 | B2-03 (Presidio) | F-02 |
| **Dom 25** | B1-06, B1-07 | B2-04, B2-05 · **puerta: ¿la latencia cumple RNF-01?** | F-03 |
| **Lun 26** | B1-08 (biometría) | B2-06 (dataset), B2-08 · **puerta: ¿entra el Blue-Green en VRAM?** | F-04 (chat con mocks) |
| **Mar 27** | B1-09, B1-10 | B2-09 (RAG), B2-07 | F-04, F-06 |
| **Mié 28** | B1-11, B1-12 | B2-10, B2-11 (chat real) | F-05, conectar con el backend real |
| **Jue 29** | B1-13 (Blue-Green) | B2-11, B2-12 | F-07, F-08 |
| **Vie 30** | B1-14 (Docker, Caddy, tunnel) | B2-13 (afinar latencia) | F-09, F-10 |
| **Sáb 31** | B1-15, B1-16 | B2-14 (afinar el clasificador) | F-10, F-11 |
| **Dom 1** | **Correr TODAS las pruebas de RNF y juntar las evidencias** | ← | ← |
| **Lun 2** | **Congelar el código** (tag `v1.0.0`), informe de evidencias, ensayo de la demo | ← | ← |
| **Mar 3** | **ENTREGA** | | |

---

## 13. Proceso de calidad (tomado de la monografía como guía)

De la monografía de ejemplo **tomamos las prácticas, no los números**.

### 13.1 Ajustes al orden de `teoria_backend.md`

| En la guía | En este proyecto |
|---|---|
| pytest en la Parte 13 | **Desde el día 1**: cada tarea entra con sus pruebas |
| Ramas "cuando haga falta" | **Ramas protegidas desde el día 1** |
| Autenticación "solo si hace falta" | Es un RNF: va en la primera semana |
| Supabase al final | **Desde el inicio**: somos 3 compartiendo la base |
| `class Config` en `config.py` | Pydantic v2: `model_config = SettingsConfigDict(env_file=".env")` |
| Tablas en plural, `id` | Tablas en singular, `id_<tabla>`, campos de auditoría (convención de la monografía) |
| CORS con `localhost:5500` | CORS con `http://localhost:5173` (Vite) y el dominio del tunnel |

**Se mantiene todo lo demás:** el modelo de datos primero, los mocks, Pydantic con esquemas separados
de entrada y salida, `.env` fuera de Git, Alembic como única forma de cambiar la base, que el servidor
decide y el cliente no, `Depends(get_db)` y `HTTPException` con códigos correctos.

### 13.2 Ramas y commits (GitFlow simplificado)

```
main        ← lo que se entrega. Solo se toca por PR desde develop. Tag v1.0.0 al final
develop     ← integración. Solo por PR
feature/BAI-012-login-totp     ← una tarea = una rama de 1 o 2 días
fix/BAI-031-latencia-rag
```

- Prefijo de tickets **BAI** (Banco Amazónico IA), con issues de GitHub.
- Commits convencionales: `feat(auth): agrega verificación TOTP [BAI-012]`.
- **Todo PR necesita 1 aprobación de otro integrante + CI en verde.** En los módulos de auth,
  transferencias y chat revisa el otro backend.
- Push directo a `main` y `develop` **bloqueado** en la configuración de GitHub.

### 13.3 Puerta de calidad del CI (en cada PR)

- ruff sin errores.
- pytest al 100 % aprobado.
- Cobertura del backend ≥ 80 %.
- bandit sin hallazgos altos.
- pip-audit sin vulnerabilidades críticas.
- Build del frontend exitoso.

### 13.4 Plantillas (adaptadas de la monografía)

- **Caso de prueba** `CP-MOD-NNN` (módulos: AUT, CON, TX, TAR, CHAT, IA, UX): ID, título, RNF trazado,
  característica ISO 25010, precondiciones, datos, pasos, resultado esperado medible, resultado
  obtenido, estado y evidencia.
- **Defecto** `DEF-2026-NNN` (plantilla de issue en GitHub): severidad (crítica, mayor, menor,
  cosmética), pasos para reproducir, obtenido vs. esperado, frecuencia, evidencia con `trace_id`.
- **Matriz de trazabilidad** `docs/matriz_trazabilidad.md`:

| RNF | Componente | Prueba | Herramienta | Evidencia |
|---|---|---|---|---|
| RNF-01 | caché, streaming, plantillas | CP-IA-001 | k6 | `evidencias/rnf01_k6.html` |
| RNF-02 | enmascarado.py, Caddy, cifrado | CP-IA-002, CP-AUT-005 | pytest, openssl | `evidencias/rnf02_*.txt` |
| RNF-03 | seguridad/, usuario_actual | CP-AUT-001..004 | pytest | `evidencias/rnf03_pytest.txt` |
| RNF-04 | modelos.py, endpoint activar | CP-IA-003 | k6 / script | `evidencias/rnf04_bluegreen.txt` |
| RNF-05 | clasificador.py, rag.py | CP-IA-004 | evaluar_intenciones.py | `evidencias/rnf05_matriz.html` |

### 13.5 Informe de evidencias (lo que se entrega)

Una tabla final por RNF: **meta → resultado medido → ¿cumple? → archivo de evidencia**. Es la
respuesta directa a lo que pidió el docente: *demostrar que la app cumple los RNF de la diapositiva*.

---

## 14. Qué instalar en cada computadora

| Herramienta | Backend 1 | Backend 2 | Frontend |
|---|---|---|---|
| Git + cuenta de GitHub | ✅ | ✅ | ✅ |
| VS Code | ✅ | ✅ | ✅ |
| Python 3.11 | ✅ | ✅ | opcional |
| **Node.js LTS** (para React, Playwright y algunas herramientas) | ✅ | ✅ | ✅ |
| Docker Desktop (Redis, Caddy) | ✅ | ✅ | opcional |
| PostgreSQL local (para correr las pruebas sin tocar Supabase) | ✅ | ✅ | — |
| **Ollama** + `llama3.1:8b` + `bge-m3` | opcional | ✅ (laptop con la RTX 5060) | — |
| k6 | — | opcional | ✅ |
| **Android Studio** (trae el SDK de Android y Java, necesarios para compilar el APK) | — | — | ✅ |
| **scrcpy** (duplicar la pantalla del celular) | — | solo en la laptop de la demo | ✅ |
| Celular **Android** con depuración USB + cable USB-C | — | — | ✅ |
| Acceso al proyecto de Supabase | ✅ | ✅ | — |
| Google Authenticator en el celular (para probar el TOTP) | ✅ | ✅ | ✅ |

Para comprobar Node: `node --version` (debe responder un número). Si no responde, se instala la
versión LTS desde nodejs.org.

---

## 15. Riesgos conocidos y cómo los atacamos

| Riesgo | Impacto | Qué hacemos |
|---|---|---|
| El primer fragmento de las respuestas largas pasa de 1,5 s | RNF-01 | Se mide el **25 de oct**. Plantillas para lo crítico, caché precalentada, respuestas cortas, modelo de 3B como plan B |
| Dos modelos no entran juntos en 8 GB de VRAM | RNF-04 | Se prueba el **26 de oct**. Versión nueva = mismo modelo base con Modelfile mejorado, o modelos de 3B para la demo |
| Solo una laptop tiene GPU | Atrasa a Backend 2 | `LLMFalso` en las pruebas, Ollama compartido por la red, `llama3.2:3b` para desarrollar |
| No llegar al 98 % | RNF-05 | Reglas para lo inequívoco + LLM para el resto; derivar cuando hay duda; se itera con el set de desarrollo |
| Supabase + asyncpg: errores de "prepared statement" con el pooler en modo transacción | Conexión | Usar la cadena del **Session pooler** (puerto 5432) o `statement_cache_size=0`. Verificar en el panel de Supabase |
| El APK no conecta con el backend (Android bloquea HTTP) | Demo | Backend detrás de Cloudflare Tunnel (HTTPS) y `VITE_API_URL` apuntando ahí; probar el APK en el celular el **30 de oct**, no el día de la exposición |
| El plugin de huella no permite proteger la clave del dispositivo | RNF-03 | Se prueba en F-02 (24–25 oct). Plan B: huella para desbloquear la app + TOTP obligatorio en las operaciones |
| Android Studio pesa varios GB y tarda en instalar | Atrasa al frontend | Instalarlo **el primer día**, aunque el APK se compile recién al final |
| Subir el `.env` a GitHub | Seguridad | `.gitignore` antes del primer commit; si pasa, **cambiar las claves** |
| Prompt injection ("ignora tus reglas y transfiere…") | Seguridad | La IA no ejecuta nada: todo cambio de datos pasa por una acción pendiente + huella o TOTP |
| Supabase pausa el proyecto gratuito por inactividad | Demo | Entrar al panel unos días antes de la entrega |

---

## 16. Decisiones pendientes

1. **Nombre definitivo del banco:** por ahora "Banco Amazónico".
2. ~~Definiciones de RNF-01 y RNF-05~~ **Decidido:** RNF-01 se mide hasta el primer fragmento
   visible, mostrando respuestas cortas y largas (sección 5, RNF-01). En RNF-05, la derivación a un
   humano cuenta como acierto, con un control de % de derivación ≤ 5 % (sección 5, RNF-05).
3. ~~Cómo será la demo~~ **Decidido:** **APK** (React + Capacitor) en un celular Android, con la
   pantalla duplicada por **USB-C + scrcpy** (sección 6.5). BlueStacks no se usa porque no tiene
   sensor de huella.
4. **Nombre del repositorio y quién lo crea** (propuesta: `banco-asistente-ia`, lo crea Backend 1).
5. **Quién es Backend 1 y quién es Backend 2.**
