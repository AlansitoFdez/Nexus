# Orquestador Multi-Agente con LangGraph + Servidor MCP Propio (Nexus)

### Edición Code Review — pivote de dominio desde gestión de tickets

---

## 🧑‍🏫 Nota para la IA que lea esto

**Eres mi mentor y maestro en este proyecto. No eres un asistente que me da código para copiar y pegar.**

Tu rol es el de un senior developer con experiencia real en sistemas agénticos en producción que me está enseñando a construir esto desde cero. Eso significa que antes de escribir cualquier línea de código conmigo, me explicas el concepto que hay detrás. Me dices por qué hacemos las cosas así y no de otra manera. Me haces preguntas para asegurarte de que he entendido antes de avanzar. Si cometo un error, no me das la solución directamente: me das pistas para que yo llegue a ella. Si algo funciona pero está mal hecho, me lo dices aunque funcione.

El objetivo no es terminar el proyecto. El objetivo es que cuando termine el proyecto, yo sea capaz de explicarle a otra persona cómo funciona cada decisión técnica que tomamos, por qué usamos cada tecnología y qué alternativas existían.

**Reglas concretas para ti como mentor:**

- Antes de cada bloque de código, explícame el concepto que vamos a implementar. No el código, el concepto.
- Después de cada implementación, hazme al menos una pregunta para verificar que he entendido.
- Si detecto que estoy copiando sin entender, para y pregúntame qué hace cada línea.
- Usa analogías del mundo real cuando introduzcas conceptos nuevos. Los conceptos abstractos se entienden mejor con ejemplos concretos.
- Cuando tomemos una decisión de arquitectura, explícame siempre qué otras opciones existían y por qué elegimos esta.
- Al final de cada sesión o fase, hazme un pequeño resumen de lo que hemos aprendido en esa sesión.
- Si en algún momento me ves perdido o frustrado, da un paso atrás y replantea la explicación desde otro ángulo.
- **Ver la actualización de ritmo de trabajo más abajo** (sección de evolución de la dinámica de mentoría) — el modo por defecto ya no exige intento previo en todo código nuevo, pero la explicación detallada del concepto sigue siendo obligatoria siempre.

**Mi perfil como developer (punto de partida original del proyecto):**
- Junior con experiencia en React y Node.js/Express
- En proceso de aprender Next.js con TypeScript
- Aprendiendo Python y FastAPI
- Sin experiencia previa en sistemas agénticos, LangGraph o MCP
- Objetivo profesional: trabajar en roles de desarrollo con componente de IA
- Trabaja habitualmente en dos máquinas (PC de sobremesa y portátil), sincronizadas vía GitHub

**Estado real a fecha de este documento**: ya no soy el mismo punto de partida de arriba — construí una infraestructura FastAPI + PostgreSQL + Redis completa, un servidor MCP propio funcionando con autenticación, y un grafo LangGraph completo con 7 nodos, human-in-the-loop real vía `interrupt()`, y 22+ tests con mocks, todo aplicado al dominio de gestión de tickets. Ese conocimiento de la **mecánica** (LangGraph, MCP, testing de agentes, SQLAlchemy/Alembic) no se pierde con el pivote de dominio que viene a continuación — es la base sobre la que se reconstruye. **Actualización de 1 de agosto de 2026**: con la Fase 2 del dominio Code Review ya completa de extremo a extremo (ver Registro de progreso real), ese conocimiento de mecánica queda validado dos veces sobre dos dominios distintos — incluyendo el mecanismo más avanzado del proyecto hasta ahora, el fan-out dinámico con `Send()`. **Actualización de 2 de agosto de 2026**: con la Fase 3 también completa (servidor MCP con integraciones reales contra la API de GitHub — lectura de repos, diffs de PR y comentarios reales publicados en un PR), el proyecto tiene ya dos integraciones externas construidas desde cero y validadas de extremo a extremo (MCP como protocolo, y GitHub como API externa real con auth, rate limits y escritura real) — ya no es solo mecánica interna del propio backend.

---

## 🎯 Evolución de la dinámica de mentoría (acordado durante la Fase 2, actualizado en la Fase 3)

En un punto avanzado de la Fase 2, Alan expresó una preocupación real y legítima: sentía que no estaba desarrollando fluidez propia para programar, porque la mayoría del código ya salía escrito por la IA, y su parte se limitaba a responder preguntas de verificación. Esto llevó a un ajuste consciente de la dinámica de mentor:

- **Código genuinamente nuevo** (un nodo nuevo, una función con lógica no vista antes): el primer intento debe ser de Alan, aunque esté incompleto o mal. La IA corrige después, señalando el error concreto y por qué, sin simplemente sustituirlo por la versión correcta sin explicación.
- **Código mecánico o muy repetitivo** (tests que siguen un molde ya establecido, un cuarto nodo que repite un patrón ya visto tres veces): Alan puede pedir explícitamente que lo escriba la IA, para avanzar más rápido, siempre que el patrón de fondo ya haya sido entendido al menos una vez.
- **Docstrings**: por decisión explícita de Alan, estos los escribe siempre la IA. No es un área que Alan considere necesaria para entrenar su fluidez de programación.
- **Ejercicio de memoria al empezar sesión**: antes de avanzar a código nuevo, es recomendable pedir a Alan que reescriba de memoria (sin mirar el proyecto) una pieza pequeña ya cerrada en la sesión anterior — **matiz añadido en la Fase 3**: esto solo tiene valor si es un *concepto o decisión de diseño* ("¿por qué elegimos X en vez de Y?"), nunca sintaxis exacta o firmas de función palabra por palabra — memorizar código literal no entrena nada útil, y forzarlo generó fricción real sin beneficio.

**🔄 Actualización real de ritmo (Fase 3, julio 2026)**: Alan pidió explícitamente acelerar el ritmo general del proyecto. Desde ese punto en adelante, el modo de trabajo por defecto cambia a: **la IA da el código directamente junto con una explicación técnica detallada**, sin exigir un intento previo de Alan en cada pieza nueva — se mantiene, eso sí, la explicación del concepto de fondo, las preguntas de verificación puntuales cuando algo es genuinamente nuevo, y el resumen de fase. Esta es una decisión explícita y consciente de Alan sobre el trade-off velocidad-vs-fluidez-propia que él mismo había planteado en la Fase 2 — no una que la IA tome por su cuenta. Si en cualquier momento Alan siente que está perdiendo el hilo del entendimiento real, la prioridad es que lo diga y se vuelva al modo lento puntualmente, sin que eso se interprete como un fracaso del ritmo rápido.

Esta dinámica **no es una excepción puntual**: se mantiene como el modo de trabajo por defecto de aquí en adelante, salvo que Alan pida explícitamente lo contrario.

---

## 🔄 Pivote de dominio (decidido el 29 de julio de 2026)

### Qué cambia y por qué

Nexus nació como un sistema de gestión automática de tickets de soporte técnico. Tras completar la Fase 3 (servidor MCP con tools reales contra PostgreSQL, autenticación con API key, validación de parámetros), el proyecto **pivota de dominio**: de "gestión de tickets" a un **sistema de Code Review con múltiples agentes especialistas**.

**El nuevo caso de uso**: el usuario sube un repositorio de GitHub (o pega código directamente) y especifica qué quiere que se revise — patrones de diseño, malas prácticas, seguridad, rendimiento, etc. Un nodo **Router** interpreta esa petición en lenguaje natural y decide qué agentes especialistas activar (no todos corren siempre, solo los relevantes para lo que se pidió). Los agentes activados analizan el mismo código **en paralelo** (patrón **Ensemble**: varios expertos mirando lo mismo desde ángulos distintos, no una cadena secuencial). Un nodo **Sintetizador** combina todos los hallazgos en un informe único, priorizado. Si el usuario pide que el sistema comente directamente en el Pull Request de GitHub, esa acción — pública, visible, no trivialmente reversible — pasa por aprobación humana antes de ejecutarse.

**Por qué este pivote tiene sentido, no es solo "cambiar de idea"**: un sistema de code review multi-agente exige patrones arquitectónicos genuinamente más ricos que la gestión de tickets — específicamente, ejecución paralela dinámica (Router decide *cuántos* y *cuáles* agentes corren, no una ruta fija) y un patrón de síntesis sobre múltiples fuentes concurrentes. Esto encaja mejor con lo que un sistema multi-agente "de verdad" necesita demostrar en un portfolio, y usa el mismo stack ya validado.

### Mapa de qué se reutiliza y qué se reconstruye

Esta tabla es la referencia rápida; el detalle fase por fase está más abajo, en "Fases de desarrollo". *(Snapshot del plan al momento del pivote — el detalle de cómo se resolvió cada fila realmente está en el Registro de progreso real, más abajo.)*

| Pieza | Estado tras el pivote |
|---|---|
| Infraestructura (Docker Compose, Postgres, Redis, FastAPI base) | ✅ Reutilizable tal cual |
| Mecánica de LangGraph (`StateGraph`, `add_conditional_edges`, checkpointer Redis, `interrupt()`) | ✅ Reutilizable tal cual — el conocimiento de *cómo funciona* no depende del dominio |
| Servidor MCP como framework (`instance.py`/`tools.py`/`server.py`, auth con `StaticTokenVerifier`, testing in-memory con `Client(mcp)`) | ✅ Reutilizable tal cual |
| Dashboard Next.js + WebSocket hub (`ConnectionManager`) | ✅ Reutilizable tal cual — solo cambia el contenido de los mensajes, no el mecanismo |
| Patrón Repository + Dependency Injection + testing con base de datos real | ✅ Reutilizable tal cual, como convención de trabajo |
| Modelos `Ticket`/`KnowledgeBaseEntry`/`Approval` | 🔨 Se sustituyen por modelos del nuevo dominio (`AnalysisRequest`, `Finding`, etc.) — el patrón de diseño (relationships, `server_default`, índices) se reaplica igual |
| Nodos del grafo (`classifier_node`, `kb_searcher_node`, `diagnosis_node`, `response_node`, `escalation_node`) | 🔨 Se reconstruyen para el nuevo dominio — el patrón (structured output, manejo de errores vía `state["error"]`, mocking) se reutiliza; el contenido de cada nodo, no |
| `human_approval_node` | ✅ Mecanismo 100% reutilizable — solo cambia la condición que lo dispara |
| Las 4 tools MCP de tickets (`search_knowledge_base`, `query_tickets_db`, `create_external_ticket`, `notify_team`) | ❌ Se sustituyen por completo — el dominio ya no tiene sentido, pero el patrón de construcción (repository detrás de la tool, idempotencia, validación en la frontera) se reutiliza al 100% |
| Routing condicional simple (una rama → un destino) | 🔨 Se mantiene para casos de un-solo-destino, pero se añade un concepto **genuinamente nuevo**: fan-out dinámico a varios nodos en paralelo |

---

## 📋 Adenda de metodología (acordada tras el inicio del proyecto — sigue vigente sin cambios)

Esta sección registra reglas de trabajo concretas establecidas durante el desarrollo real de Nexus. Son convenciones de **cómo trabajamos**, no de **qué construimos** — por eso ninguna de ellas depende del dominio (tickets o code review) y todas siguen aplicando tal cual tras el pivote.

### Idioma del código

Todo el código (nombres de variables, clases, archivos, carpetas, columnas de base de datos) se escribe **siempre en inglés**, sin excepción, desde el commit `refactor(models): rename ticket fields to english`. Los mensajes de commit y las explicaciones del mentor se mantienen en español.

### Convención de commits

Commits atómicos (una tarea lógica = un commit, no un archivo = un commit ni un tipo-de-archivo = un commit), formato `tipo(scope): mensaje`, con scope en paréntesis (`feat(models):`, `fix(infra):`, `chore(config):`...). El scope se omite solo en cambios a nivel de todo el repo. Antes de cada commit, se verifica con `git status` que solo se añaden los archivos esperados (especial atención a que `venv/`, `node_modules/`, `.env` y `__pycache__/` nunca aparezcan). Archivos "vacíos de significado por sí solos" (como un `__init__.py` recién creado) se comitean junto al primer archivo real que dependa de ellos.

**Criterio real para decidir dónde cortar un commit** (clarificado explícitamente en la Fase 3, tras una confusión real de Alan sobre si separar tests/migraciones en commits propios): la pregunta correcta no es "¿son archivos de distinto tipo?" (código vs. test vs. migración), es **"¿esto fue una tarea real y distinta, en un momento real y distinto, que alguien querría poder revertir por separado?"**. Si el código y su test se escribieron y verificaron en el mismo momento, van en el mismo commit (un commit de código sin su test es deuda de testing disfrazada de "commit pequeño"). Si pasó tiempo real entre escribir el nodo y escribirle tests (como ocurrió entre las Fases 2.2–2.9 y la 2.10), sí se separan, porque fueron dos tareas reales en dos momentos reales.

**Matiz añadido el 29 de julio de 2026**, tras aplicar el criterio a un caso nuevo (schemas/repositories/endpoints del dominio Code Review): el test de fondo sigue siendo el mismo, pero conviene distinguir tres situaciones concretas:
- **Acoplamiento estructural (nunca se separan, sin importar el tiempo)**: modelo SQLAlchemy + su migración de Alembic. No existe ningún estado válido con uno sin el otro — revertir solo la migración deja un modelo apuntando a una tabla inexistente; revertir solo el modelo deja una tabla huérfana sin código que la use. El tiempo transcurrido entre escribir uno y otro no cambia esto; no es una señal válida aquí.
- **Mismo momento real (se separan solo si hubo tiempo real entre medias)**: código + su test — el caso original de arriba, sin cambios.
- **Decisiones de diseño independientes (sí se separan, por capa)**: schemas → repositories → endpoints REST construidos sobre un mismo dominio nuevo. Cada capa, sola, es un estado coherente y funcional aunque incompleto (un schema sin repository que lo use no rompe nada); se puede revertir una sin que la otra deje de tener sentido. Aquí tiene valor dividir en commits por capa — manteniendo, eso sí, cada test pegado a su capa según el criterio del punto anterior.

**Segundo matiz añadido el 1 de agosto de 2026**, tras la retirada completa del dominio de tickets (Fase 2.10): cuando una migración de Alembic borra filas existentes de forma intencionada (no accidental), el `DELETE` explícito se documenta con un comentario en el propio archivo de migración explicando por qué esos datos no se conservan — la migración es el lugar correcto para esa justificación, no el mensaje de commit, porque es lo primero que alguien revisará si algún día se pregunta "¿por qué desaparecieron estas filas?".

**Tercer matiz añadido el 2 de agosto de 2026**, tras cerrar la Fase 3 sin haber comiteado nada hasta confirmar que todo funcionaba de extremo a extremo: el criterio de "tarea real y distinta en un momento real y distinto" **presupone que hay commits intermedios reales que separar**. Cuando un conjunto de archivos se escribe y se verifica todo junto, en una sola sesión, sin comitear hasta el final, la granularidad histórica que se habría usado comiteando sobre la marcha (una tool → un commit, la siguiente tool → otro commit) deja de tener sentido real — separar por capa (config / cliente HTTP / registro de tools MCP / modelo+migración / schema+validación / nodo+estado / wiring del grafo) sigue aportando valor real de revertibilidad; separar además por sub-fase dentro de un mismo archivo que nunca existió en un estado intermedio comiteado, no. Es preferible una separación honesta por capas sobre el estado final, a fingir una historia incremental que no ocurrió.

### Ritmo de trabajo

Ver la sección de "Evolución de la dinámica de mentoría" arriba — actualizada en la Fase 3 para reflejar el ritmo acelerado que Alan pidió explícitamente.

### Testing

Se adopta **testing en paralelo**: cada pieza funcional nueva (endpoint, nodo del grafo, tool MCP, edge de routing) se testea inmediatamente después de construirse, nunca se acumula deuda de testing para el final de la fase. No se exige TDD estricto de forma dogmática.

Stack de testing: `pytest`, `pytest-asyncio`, `httpx2` (sustituye a `httpx` puro con `TestClient`, deprecado desde mediados de 2026) para backend; a definir para frontend cuando se llegue a la Fase 4.

Cada test debe **aislar una causa concreta**. Para testear un componente en aislamiento sin depender de sus colaboradores reales, se usan **fakes** (clases mínimas escritas a mano) o **mocking** con `unittest.mock` cuando el colaborador es una librería externa no determinista (un LLM) o un proceso separado (el servidor MCP por HTTP, o — desde la Fase 3 — la propia API de GitHub).

**Patrón de mocking** (aplica a cualquier nodo que llame a un LLM o a un cliente MCP):
- Regla de oro: **se parchea donde el nombre se usa, no donde se define** (`patch("app.agents.nodes.X.ChatGroq")`, nunca `patch("langchain_groq.ChatGroq")`).
- Llamadas a LLM: se mockea con una cadena de `.return_value` terminando en `AsyncMock(return_value=...)` o `AsyncMock(side_effect=Exception(...))`.
- Clientes MCP (`async with Client(...) as client:`): `MagicMock` con `__aenter__`/`__aexit__` asignados explícitamente como `AsyncMock`.
- Clientes HTTP externos (`httpx.AsyncClient`, desde la Fase 3): mismo patrón exacto que un cliente MCP — `MagicMock` con `__aenter__`/`__aexit__` como `AsyncMock`, y `.get`/`.post` como `AsyncMock(side_effect=[...])` devolviendo respuestas mockeadas en el orden en que se esperan las llamadas reales. Ningún test de Nexus habla con la red real, ni siquiera contra GitHub.
- Funciones de routing (edges): funciones puras, se testean llamándolas directamente, sin mocks.
- Nodos que usan `interrupt()`: no se pueden testear de forma aislada con mocks simples — su comportamiento solo existe con un grafo compilado y checkpointer real. **Actualización (Fase 2.12, dominio Code Review)**: sí se puede probar la lógica *alrededor* de `interrupt()` (crear/actualizar registros, construir el payload) parcheando la propia función `interrupt()` directamente en el módulo del nodo — sin necesidad de grafo compilado. El comportamiento de pausa/resume real en sí sigue exigiendo el test de integración con grafo + checkpointer reales.

**Gotcha real descubierto en la Fase 3, aplica igual a cualquier tool MCP futura**: las tools MCP no pasan por el sistema `Depends(get_db)` de FastAPI — llaman a `SessionLocal()` directamente. Esto significa que `app.dependency_overrides` (usado en los tests de endpoints REST) **no protege los tests de tools MCP** de golpear la base de datos real. La solución es parchear `SessionLocal` en el módulo `tools.py` específicamente (`patch.object(tools, "SessionLocal", TestSessionLocal)`), mismo principio de "parchear donde se usa". **Este mismo gotcha reapareció en la Fase 2.12** (dominio Code Review), esta vez en el test de integración del grafo completo: cada nodo llama a `SessionLocal()` por su cuenta, así que el test de integración necesita parchear `SessionLocal` en **cada módulo de nodo que toque base de datos**, no solo uno — de lo contrario los nodos golpean la base de dev real en silencio, en vez de `nexus_test`.

**Gotcha nuevo, Fase 2.9 (dominio Code Review)**: cuando un nodo persiste una escritura con su propia sesión (`SessionLocal()`), distinta a la sesión que el test usa para verificar el resultado, la sesión del test puede servir una copia cacheada (su *identity map*) del objeto tal como estaba antes de esa escritura externa, en vez de leer el valor real ya actualizado en la base. Solución: `db_session.expire_all()` antes de releer, para forzar una lectura fresca.

**Gotcha de infraestructura, Fase 2.12**: `langgraph-checkpoint-redis` depende de RediSearch para sus índices, y **RediSearch solo permite crear índices en la base de datos lógica 0 de Redis** (`FT.CREATE` falla con `Cannot create index on db != 0` en cualquier otro índice lógico). Esto descarta aislar tests de checkpointer usando un índice lógico de Redis distinto (patrón que sí funciona para aislar Postgres con una base de test separada) — la alternativa correcta es un `thread_id` único por ejecución (ej. `uuid.uuid4()`), no una base de Redis distinta.

**Gotcha de metodología, Fase 3.3 (dominio Code Review)**: cuando se agrega una constraint nueva sobre un campo que ya existía y ya se usaba en fixtures de tests repartidos por toda la suite (aquí, `post_to_pr`), no basta con revisar el archivo de test que motivó el cambio — hay que **grepear ese campo en toda la carpeta `tests/`**. La restricción "`post_to_pr=True` exige `source_type='github_repo'` y `pr_number`" rompió `test_graph.py` (detectado y corregido de entrada) y, en una segunda pasada, `test_human_approval_node.py` (se pasó por alto en la primera revisión y solo se detectó al correr `pytest` completo de forma local). Un cambio de validación que colisiona con un fixture existente además suele ser señal de una decisión de dominio real sin resolver, no solo un test desactualizado — en este caso, destapó que nada en el proyecto sabía todavía a qué PR pertenecía un análisis.

Para tests de integración con base de datos real, se usa una **base de datos de test separada** (`nexus_test`) dentro del mismo contenedor Postgres de desarrollo, con `Base.metadata.create_all()`/`drop_all()` por test — nótese que esto crea el esquema directo desde los modelos de SQLAlchemy, **sin pasar por Alembic**: aplicar una migración nueva contra la base de desarrollo real (`alembic upgrade head`) y que los tests pasen son dos verificaciones independientes, no una sustituye a la otra.

### Documentación en código

Docstrings de estilo Google en funciones y clases de lógica de negocio real — no en código trivial. Comentarios inline reservados para explicar el *por qué* de una decisión no obvia.

### Aplicación de SOLID

- **Single Responsibility**: cada nodo del grafo hace una sola cosa; endpoint/repositorio separados; edges de routing viven juntos en `edges.py` porque comparten la misma razón de cambio.
- **Dependency Inversion**: `Depends()` de FastAPI; inyección entre repositorios (ej. `ApprovalRepository` recibía `TicketRepository` por constructor — el principio se reaplica igual entre los repositorios nuevos que surjan del pivote; confirmado en la práctica: `ApprovalRepository` reconstruido en la Fase 2.10 recibe `AnalysisRequestRepository` por constructor exactamente con el mismo rol).
- **Open/Closed**: razón de fondo por la que los nodos del grafo llaman a tools MCP en vez de importar repositorios directamente — la lógica puede evolucionar sin tocar el nodo consumidor (validado en la práctica: `search_knowledge_base` pasó de datos fijos a full-text search real sin que `kb_searcher_node` cambiara su forma de llamarla; validado por segunda vez en la Fase 2.2, `entry_node` diseñado contra el contrato de `read_repository_files` antes de que esa tool existiera; validado una tercera vez en la Fase 3.1, donde ese mismo contrato se cumplió al construir la tool de verdad — `entry_node` no cambió una línea).
- Interface Segregation y Liskov se aplican solo si aparecen jerarquías de clases reales.

### Números mágicos y constantes de configuración

- **Configuración de infraestructura/despliegue** (nombres de modelo LLM, URLs, claves): va en `Settings` (`config.py`) como variable de entorno con default razonable.
- **Parámetros de comportamiento del algoritmo** (un umbral, un límite de resultados): va como constante a nivel de módulo, arriba del archivo que la usa. *(Ejemplo real, Fase 3.1: `MAX_FILE_SIZE_BYTES`/`MAX_TOTAL_SIZE_BYTES`/`INCLUDED_EXTENSIONS`/`EXCLUDED_DIR_PARTS` en `github_client.py` — límites de comportamiento del filtrado de archivos, no configuración de despliegue, así que no van en `Settings`.)*

### Errores de dominio vs. resultados normales

Un método de repositorio que **busca** algo devuelve `None` cuando no encuentra nada. Un método que **actúa** y no puede completar su tarea lanza una **excepción de dominio propia**, no devuelve `None`. **Inconsistencia real detectada y aún pendiente**: `TicketRepository.update()` devuelve `None` en silencio si el ID no existe, en vez de lanzar una excepción propia como sí hace `ApprovalRepository.create()` con `TicketNotFoundError`. *Nota post-pivote*: si `TicketRepository` desaparece en la reconstrucción del dominio, este pendiente concreto se cierra solo por eliminación del archivo — pero el patrón de error que representa (búsqueda silenciosa vs. acción que falla) debe verificarse igual en los repositorios nuevos (`AnalysisRequestRepository` y similares), para no reintroducir la misma inconsistencia con otro nombre.

**Cerrado el 29 de julio de 2026**: `AnalysisRequestRepository.update()`, construido en la reconstrucción de la Fase 1.3 del nuevo dominio, ya lanza `AnalysisRequestNotFoundError` en vez de devolver `None` — el pendiente queda resuelto en el repositorio que sustituye a `TicketRepository`.

**Cerrado del todo el 1 de agosto de 2026**: `TicketRepository` fue eliminado por completo en la retirada del dominio de tickets (Fase 2.10), así que la inconsistencia original ya no existe ni como archivo. `ApprovalRepository`, reconstruido en la misma fase para apuntar a `analysis_request_id`, reutiliza `AnalysisRequestNotFoundError` (la excepción ya existente de `AnalysisRequestRepository`) en vez de crear una excepción de dominio propia duplicada — mismo patrón de error, sin reintroducir la inconsistencia con otro nombre.

**Dentro de los nodos del grafo**: los nodos no lanzan excepciones hacia arriba para errores esperables — las capturan con `try/except` y escriben un mensaje en `state["error"]`, dejando que el edge condicional siguiente decida el routing. El campo `error` nunca debe convivir con datos que "aparenten éxito". El `try` debe acotarse a la mínima operación que puede fallar por causas externas reales.

**Matiz añadido en la Fase 2.5 (dominio Code Review)**: cuando varios nodos del mismo tipo corren en paralelo (los especialistas del fan-out), el fallo de **uno** de ellos no debe tratarse igual que el fallo de un nodo secuencial pre-fan-out. Se introdujo `failed_specialists` como campo separado de `error`, con su propio reducer `operator.add` — un especialista que falla nunca escribe en `state["error"]`, precisamente para no tumbar el análisis entero por un fallo parcial cuando los demás especialistas sí produjeron hallazgos reales.

**Tercer matiz añadido en la Fase 3.3 (dominio Code Review)**: la misma lógica de "no confundir un fallo parcial con el fallo del todo" reaparece una tercera vez, en una forma distinta a las dos anteriores — ya no es un fallo *entre nodos paralelos* (`failed_specialists`), es el fallo de una **acción posterior** a un resultado ya exitoso. `post_comment_node` corre después de que `synthesizer_node` ya persistió un status final correcto (`completed`/`completed_with_errors`); si publicar el comentario en GitHub falla, ese fallo nunca debe escribirse en `state["error"]`, porque enrutaría a `failure_node` y sobreescribiría un status ya correcto con `"failed"` — una mentira sobre lo que realmente pasó (la revisión sí se completó; solo falló publicarla). Se registra por log y se notifica por WebSocket, sin tocar el status persistido.

### Repaso periódico

Antes de avanzar a piezas nuevas tras acumular varias fases, se hacen pausas de repaso completo del proyecto para detectar inconsistencias o deuda técnica. Aplicado tras Fase 1.2, 1.3, 1.4/1.5 conjuntamente, y pendiente de retomar tras estabilizar la nueva Fase 2 del dominio de code review. **Actualización (1 de agosto de 2026)**: Fase 2 ya estabilizada y completa de extremo a extremo (ver Registro de progreso real) — el próximo repaso periódico natural es antes de arrancar la Fase 3 (servidor MCP con integraciones externas reales). **Actualización (2 de agosto de 2026)**: Fase 3 también completa — el próximo repaso periódico natural es antes de arrancar la Fase 4 (dashboard Next.js), una vez resuelto el pendiente heredado de conectar `build_graph()` a FastAPI vía lifespan events.

### Entorno multi-máquina

El proyecto se trabaja indistintamente desde un PC y un portátil, sincronizados vía GitHub. Lo que **no** viaja por git: `backend/venv/`, `backend/.env`, `frontend/node_modules/`, la base de datos `nexus_test`.

---

## 📋 Descripción general del proyecto (reescrita para el nuevo dominio)

### Qué vamos a construir

Un sistema backend donde varios agentes de IA especialistas colaboran para revisar código automáticamente. El usuario aporta un repositorio de GitHub (o pega código suelto) y especifica qué tipo de revisión quiere. El sistema:

1. Interpreta la petición y decide qué especialistas son relevantes (**Router**)
2. Activa esos especialistas en paralelo sobre el mismo código (**Ensemble**) — por ejemplo: seguridad, rendimiento, patrones de diseño, buenas prácticas (set de partida propuesto, ajustable cuando lleguemos ahí)
3. Combina todos los hallazgos en un informe único, priorizado (**Sintetizador**)
4. Si se pidió comentar directamente en el PR de GitHub, esa acción espera aprobación humana antes de ejecutarse

**LangGraph** sigue siendo el framework de orquestación — y aquí se le exige más que en el dominio de tickets: fan-out dinámico (número variable de especialistas activos por petición) y fan-in con reducers para combinar hallazgos concurrentes, en vez de una cadena de decisiones secuenciales.

**Servidor MCP propio** sigue exponiendo las herramientas que los agentes usan — ahora orientadas a leer repos/diffs de GitHub y, opcionalmente, comentar en un PR real.

### Arquitectura técnica

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
│   Subir repo/código  │  Progreso en vivo  │  Aprobar PR     │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP + WebSockets
┌─────────────────────────▼───────────────────────────────────┐
│                    FastAPI (Backend principal)                │
│  Recibe solicitud  │  Orquesta el grafo  │  WebSocket hub    │
└──────────┬──────────────────────────┬──────────────────────-┘
           │                          │
┌──────────▼──────────────┐  ┌───────▼───────────────────────-┐
│    LangGraph Engine      │  │      Servidor MCP propio        │
│                          │  │   (puerto 8001, sufijo /mcp)    │
│        router            │  │                                  │
│      ╱   │    ╲          │  │  Tool: read_repository_files()  │
│  security perf design··· │  │  Tool: get_pr_diff()             │
│      ╲   │    ╱          │  │  Tool: post_pr_comment()         │
│      synthesizer          │  │  Tool: list_open_prs() (a def.) │
│           │                │  │                                  │
│    human_approval          │  │                                  │
│  (solo si post-PR pedido)  │  │                                  │
└──────────┬──────────────-┘  └───────────────────┬─────────────┘
           │                                        │
┌──────────▼──────────┐      ┌────────────────────▼───────────-┐
│  Redis (checkpoint) │      │       PostgreSQL (puerto 5434)    │
│  AsyncRedisSaver      │      │  analysis_requests / findings /  │
│  redis-stack-server   │      │  approvals (reports, si se separa) │
└──────────────────────┘      └───────────────────────────────-─┘
     ┌───────────────────────────┐   ┌────────────────────────────┐
     │          Groq API           │   │        GitHub API           │
     │  ROUTER_MODEL: gpt-oss-20b  │   │  Lectura de repos/diffs     │
     │  SPECIALIST_MODEL: gpt-oss- │   │  Comentarios en PR           │
     │  120b (razonamiento denso)  │   │  (primera integración externa│
     └───────────────────────────┘   │   real del proyecto, no      │
                                       │   simulada como create_      │
                                       │   external_ticket)            │
                                       └────────────────────────────┘
```

*Nota (2 de agosto de 2026): las tres tools del servidor MCP dibujadas arriba (`read_repository_files`, `get_pr_diff`, `post_pr_comment`) ya existen de verdad — este diagrama, escrito al planificar el pivote, describe exactamente lo que se construyó en la Fase 3. `list_open_prs` sigue como "a definir": evaluada y descartada por ahora (ver Fase 3 en el Registro de progreso real).*

### Por qué cada pieza (lo que cambia respecto al razonamiento original)

**LangGraph, fan-out dinámico**: a diferencia del grafo de tickets (una ruta condicional por vez, siempre a un único destino), aquí el Router puede activar **un subconjunto variable** de especialistas por petición — nunca todos, no siempre los mismos. Esto es un problema estructuralmente distinto de "elegir una rama entre varias", y tiene dos soluciones válidas en LangGraph, con un trade-off real entre ellas:
- **Edges estáticos + guardia interna**: todos los especialistas posibles tienen una arista fija desde el Router (LangGraph ya paraleliza automáticamente múltiples edges estáticos desde el mismo nodo); cada especialista comprueba internamente si fue seleccionado y, si no, retorna sin hacer nada. Más simple de razonar, coste de "arrancar y salir" para los no seleccionados.
- **`Send()` dinámico** (`langgraph.types.Send`): el propio edge condicional del Router devuelve una lista de objetos `Send(nombre_nodo, payload)` — solo para los especialistas realmente elegidos. Es el mecanismo "de libro" para fan-out cuyo número no se conoce en tiempo de construcción del grafo (patrón map-reduce). Más preciso, pero es sintaxis y un modelo mental genuinamente nuevos.

**Resuelto en la Fase 2.4 (ver Registro de progreso real)**: se eligió `Send()` dinámico, tras discutir los tradeoffs explícitamente.

**El reducer `operator.add` se vuelve central, no un caso raro**: en el dominio de tickets, solo `node_history` tenía múltiples escritores (todos los nodos añadían su nombre). Aquí, el campo `findings` lo escriben **N nodos especialistas distintos, ejecutándose en paralelo** — el caso de libro para el que existen los reducers. El criterio ya aprendido ("¿cuántos nodos distintos escriben esta clave?", no "¿es una lista?") aplica exactamente igual, solo que ahora con un ejemplo central del dominio en vez de uno periférico.

**GitHub API como primera integración externa real**: `create_external_ticket` (Fase 3 de tickets) simulaba un sistema externo con una tabla propia. Aquí, `post_pr_comment` habla con una API externa **de verdad** — autenticación con token real, límites de rate real, fallos de red reales. Es un salto de complejidad genuino, no cosmético. **Cerrado el 2 de agosto de 2026** (ver Registro de progreso real, Fase 3).

### Estructura de carpetas (estado tras el pivote)

```
nexus/
│
├── frontend/                          # Next.js — sin empezar, Fase 4 (patrón reutilizable, contenido a adaptar)
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # ✅ reutilizable (routers + CORS) — router de tickets retirado en la 2.10
│   │   ├── config.py                  # ✅ reutilizable — ROUTER_MODEL/SPECIALIST_MODEL ya renombrados, GITHUB_TOKEN añadido (Fase 3.1)
│   │   ├── database.py                # ✅ reutilizable tal cual
│   │   │
│   │   ├── api/
│   │   │   ├── analysis_requests.py   # ✅ CRUD del nuevo dominio, completo desde la 1.3
│   │   │   ├── approvals.py           # ✅ reconstruido en la 2.10 sobre analysis_request_id
│   │   │   └── websocket.py           # ✅ reutilizable — renombrado íntegro a analysis_request_id en la 2.10
│   │   │
│   │   ├── agents/
│   │   │   ├── state.py               # ✅ CodeReviewState completo (findings, failed_specialists, post_to_pr, pr_number, error)
│   │   │   ├── schemas.py             # ✅ RouterDecision, SpecialistFinding, SpecialistOutput
│   │   │   ├── edges.py               # ✅ route_after_entry, route_after_router (Send()), route_after_synthesizer
│   │   │   ├── graph.py               # ✅ build_graph(checkpointer) — grafo completo compilado y probado, incluye post_comment_node (3.3)
│   │   │   └── nodes/
│   │   │       ├── entry_node.py            # ✅ completo (2.2)
│   │   │       ├── router_node.py           # ✅ completo (2.3)
│   │   │       ├── specialists/             # ✅ completo (2.5-2.8)
│   │   │       │   ├── security_agent.py
│   │   │       │   ├── performance_agent.py
│   │   │       │   ├── design_patterns_agent.py
│   │   │       │   └── best_practices_agent.py
│   │   │       ├── synthesizer_node.py      # ✅ completo (2.9), diseño híbrido determinista+LLM
│   │   │       ├── human_approval_node.py   # ✅ completo (2.10)
│   │   │       ├── post_comment_node.py     # 🆕 (3.3) — ejecuta post_pr_comment tras la aprobación, nunca escribe state["error"]
│   │   │       └── failure_node.py          # 🆕 (2.11) — sin equivalente en tickets, ver Registro
│   │   │
│   │   ├── mcp_server/                # ✅ framework reutilizable (instance.py/server.py sin cambios)
│   │   │   ├── github_client.py       # 🆕 (3.1-3.3) — cliente real de la API de GitHub: read_repository_files, get_pr_diff, post_pr_comment
│   │   │   └── tools.py               # ✅ read_repository_files, get_pr_diff, post_pr_comment registradas y probadas
│   │   │
│   │   ├── repositories/              # ✅ AnalysisRequestRepository, FindingRepository, ApprovalRepository — completos
│   │   ├── models/                    # ✅ AnalysisRequest (+ pr_number, Fase 3.3), Finding, Approval — Ticket eliminado por completo (2.10)
│   │   └── schemas/                   # ✅ mismo rol, contenido nuevo completo, incluye pr_number y su validación (3.3)
│   │
│   ├── alembic/                       # ✅ reutilizable tal cual como mecanismo
│   ├── tests/                         # ✅ 118 tests en verde a fecha de este documento
│   ├── requirements.txt                # ✅ igual — httpx (ya presente) resultó suficiente para el cliente de GitHub, sin dependencias nuevas
│   └── .env.example                    # ✅ GITHUB_TOKEN añadido (Fase 3.1)
│
├── docker-compose.yml                  # ✅ reutilizable tal cual
└── README.md
```

---

## 🗺️ Fases de desarrollo (estado tras el pivote)

Leyenda: ✅ reutilizable tal cual / completo · 🔨 patrón reutilizable, contenido a reconstruir · 🆕 concepto genuinamente nuevo

### FASE 0 — Fundamentos y conceptos previos ✅ (resuelta en la práctica, ver Registro)

100% reutilizable — el concepto (grafo de estado vs. cadena de middlewares, los edges deciden el routing, no los nodos) no depende del dominio.

### FASE 1 — Infraestructura base ✅ COMPLETA (dominio Code Review)

- **1.1 Infra base** ✅ — carpetas, `.env`, Docker Compose, scaffold Next.js: sin cambios.
- **1.2 Modelos y schemas** ✅ — `AnalysisRequest`/`Finding` con `CheckConstraint` de exclusividad mutua.
- **1.3 Endpoints REST + Repository Pattern + CORS** ✅ — CRUD completo, más la primera limpieza del dominio de tickets ya obsoleto.
- **1.4 Servidor MCP base** ✅ — el framework se reutiliza; las tools reales del nuevo dominio llegaron en la Fase 3.
- **1.5 WebSocket hub** ✅ — `ConnectionManager`, la lección del bug de broadcast vs. `send_text` directo, todo reutilizable tal cual. Renombrado íntegro de `ticket_id` a `analysis_request_id` en la Fase 2.10.

### FASE 2 — El grafo de agentes ✅ COMPLETA (1 de agosto de 2026, dominio Code Review) — ver Registro de progreso real para el detalle completo de cada decisión y bug real

- **2.1 Estado compartido** ✅ — `CodeReviewState` reemplaza a `TicketState`. `findings` es aquí el caso de uso **central** del reducer `operator.add` (múltiples especialistas en paralelo), no periférico como `node_history` lo era en tickets.
- **2.2 Entry node** ✅ — determinista, sin LLM; resuelve `code_content` desde código pegado o repo (la tool MCP `read_repository_files`, construida en la Fase 3.1). `code_content` nunca se persiste — solo el `status`.
- **2.3 Router node** ✅ — reemplaza a `classifier_node`; `RouterDecision(agents_to_run: list[...])`. Decisión de arquitectura resuelta: `post_to_pr` es un campo explícito del usuario en `AnalysisRequestCreate`, **nunca** inferido por el Router desde texto libre — mismo principio que protege `human_approval_node`.
- **2.4 Fan-out tras el Router** ✅ — resuelto con **`Send()` dinámico** (`langgraph.types.Send`), elegido sobre edges estáticos + guardia interna tras discutir los tradeoffs. Cada `Send()` lleva solo el payload mínimo que cada especialista necesita, no el `CodeReviewState` completo.
- **2.5–2.8 Agentes especialistas** ✅ — Security, Performance, Design Patterns, Best Practices. Mismo patrón (structured output, persistencia inmediata por especialista) construido primero en detalle para `security_agent` y replicado para los otros tres. `failed_specialists` (reducer propio, separado de `error`) permite que el fallo de un especialista no tumbe los hallazgos reales de los demás.
- **2.9 Synthesizer node** ✅ — diseño **híbrido** determinista + LLM: una sección de Python puro garantiza que ningún finding real se pierda nunca (ordenada por severidad), y un resumen ejecutivo redactado por LLM añade valor (patrones cruzados, priorización) sin ser el único responsable de la exhaustividad. Columnas nuevas: `final_report` y el estado `"completed_with_errors"`.
- **2.10 Human approval node** ✅ — mecanismo 100% reutilizable (`interrupt()`, checkpointer Redis, `thread_id`); dispara ahora sobre `post_to_pr == True` explícito. Persiste una fila real de `Approval` (vía `ApprovalRepository`) antes de pausar, para que el estado de la aprobación sea consultable desde fuera del grafo (`GET /approvals/{id}`) mientras está pausado — no solo visible en el payload efímero del `interrupt()`. **Forzó la retirada completa del dominio de tickets** (`Approval` tenía una FK real a `tickets.id` que bloqueaba directamente este nodo) — ver Registro para el alcance completo.
- **2.11 (antes `escalation_node`)** ✅ resuelto — se descarta un equivalente directo (no hay "equipo de soporte" al que escalar en este dominio); en su lugar, se construyó `failure_node`, que cierra un hueco real distinto: sin él, una `AnalysisRequest` cuyo `entry_node`/`router_node` falla se quedaría con `status="running"` para siempre.
- **2.12 Ensamblaje + checkpointer + testing con mocks** ✅ — `build_graph(checkpointer)` compilado con Redis real. El test de integración de `human_approval_node` + grafo + checkpointer, pendiente sin resolver desde el dominio de tickets, se cerró aquí — con dos bugs reales de por medio (ver Registro).

### FASE 3 — Servidor MCP completo ✅ COMPLETA (2 de agosto de 2026) — ver Registro de progreso real para el detalle completo

- **3.1 Tool: `read_repository_files`** ✅ — primera integración externa real del proyecto. Decisión `httpx` directo vs. `PyGithub` resuelta a favor de `httpx`: solo 3 tools, cero dependencias nuevas (`httpx` ya estaba en `requirements.txt`), y el objetivo explícito de esta fase (fallos de red reales, rate limiting real) se pierde si una librería dedicada los abstrae por debajo.
- **3.2 Tool: `get_pr_diff`** ✅ — obtiene el diff de un Pull Request específico, vía content negotiation de GitHub en vez de calcularlo a mano.
- **3.3 Tool: `post_pr_comment`** ✅ — primera acción de escritura real contra la API de GitHub. Forzó resolver el hueco de `pr_number` en `AnalysisRequest`, con una decisión de dominio explícita (ver Registro).
- **3.4 Tool: listado de PRs abiertos** — evaluada y descartada por ahora: el flujo actual recibe `repo_url` + `pr_number` directamente, sin necesidad de listar PRs abiertos. Queda para revisar si la Fase 4 (dashboard) introduce un flujo de selección que sí la necesite.
- **3.5 Seguridad del servidor MCP** ✅ — sin cambios respecto a lo ya construido. La responsabilidad nueva (`GITHUB_TOKEN` nunca llega a un prompt de LLM) se cumple por construcción: el token vive únicamente dentro de `_headers()` en `github_client.py`, ningún nodo se lo pasa a ningún LLM.

### FASE 4 — Dashboard en Next.js ✅ piezas construidas y verificadas (2 de agosto de 2026) — falta componer la página real

Sin cambios de plan respecto al original en cuanto a piezas (cliente API, `useWebSocket`, componente de traza de agentes, vista de aprobación, métricas) — el contenido se adapta:
- El componente de traza de agentes (antes pensado para mostrar un nodo activo a la vez) ahora tiene la oportunidad real de mostrar **varios agentes corriendo en paralelo simultáneamente** — una superficie de UI más interesante que la original, gracias al propio pivote.
- La vista de aprobación pasa a tratarse específicamente de "aprobar el comentario que se publicará en el PR", con el diff/hallazgos como contexto.
- Las métricas pasan de "tickets resueltos vs. escalados" a algo como "hallazgos por especialidad, tiempo de análisis, PRs comentados".

**Estado real, ver Registro de progreso real para el detalle completo**: las cuatro piezas (4.1 cliente API + tipos, 4.2 `useWebSocket` + traza de agentes, 4.3 vista de aprobación, 4.4 métricas) están construidas y verificadas — 24 tests nuevos de backend (118→142) y type-check limpio en frontend. Antes de arrancar se resolvió también un pendiente heredado de la Fase 3 (wiring real del grafo a FastAPI) que bloqueaba probar cualquier endpoint de verdad. Falta una pieza de integración que ninguna sub-fase nombraba explícitamente pero que hace falta igual: ninguna página de Next.js junta `AgentTrace`/`ApprovalPanel`/`MetricsPanel` todavía — `src/app/page.tsx` sigue siendo el scaffold por defecto.

### FASE 5 — Calidad, tests y observabilidad ✅ (metodología 100% reutilizable)

Sin cambios de enfoque — testing en paralelo, mocking de LLMs, logging estructurado, CI. Solo cambia el contenido concreto sobre el que se aplican estas prácticas.

### FASE 6 — Despliegue a producción ✅ (100% reutilizable)

Sin cambios de plan. Se añade un secreto de entorno nuevo a configurar en Render/Vercel: `GITHUB_TOKEN` (personal access token; ver Fase 3.1 en el Registro para el alcance de permisos usado).

---

## 🛠️ Dependencias del proyecto

### Backend (estado heredado, sin cambios por el pivote)

```
langgraph==1.2.9
langgraph-checkpoint==4.1.1
langgraph-checkpoint-redis==0.5.1
langchain-groq==1.1.3
langchain-core==1.5.1
groq==0.37.1
redis==7.4.1
redisvl==0.23.0
fastmcp==3.4.4
```

**Resuelto en la 3.1**: httpx directo, sin dependencias nuevas — ya estaba en `requirements.txt` (usado antes para `TestClient` de tests, aunque para eso en concreto se prefiere `httpx2`). Ver Registro de progreso real, Fase 3, para el razonamiento completo frente a `PyGithub`.

**Nota pendiente sin cambios**: `pywin32`/`pywin32-ctypes` sin environment marker de plataforma — ver Adenda de metodología, sigue pospuesto a la Fase 5.6.

### Frontend Next.js

Sin cambios respecto al plan original — Fase 4 sin empezar.

---

## 🔑 Variables de entorno necesarias (actualizado)

```bash
# Backend (.env) — heredadas, sin cambios
DATABASE_URL=postgresql://user:password@localhost:5434/nexus
REDIS_URL=redis://localhost:6379
GROQ_API_KEY=tu_groq_api_key
MCP_SERVER_URL=http://localhost:8001/mcp
MCP_API_KEY=tu_clave_generada_con_secrets_token_urlsafe
GITHUB_TOKEN=tu_personal_access_token_de_github
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000

# Ya renombradas y en uso desde la Fase 2.3:
ROUTER_MODEL=openai/gpt-oss-20b
SPECIALIST_MODEL=openai/gpt-oss-120b

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

> El puerto de PostgreSQL sigue siendo `5434`. `docker-compose.yml` sigue usando `redis/redis-stack-server:latest` (necesario para `langgraph-checkpoint-redis`). `GITHUB_TOKEN` (añadido en la Fase 3.1, campo requerido en `Settings` — la app no arranca sin él) necesita, como mínimo, permiso `Contents: Read-only` sobre el repo a analizar; para `post_pr_comment` (Fase 3.3) hace falta además `Pull requests: Read and write`.

---

## 📚 Recursos de estudio recomendados

**LangGraph (heredado, sigue vigente):**
- Documentación oficial: `langchain-ai.github.io/langgraph`
- StateGraph, nodes, edges y checkpointers — ya validado en la práctica

**LangGraph — validado en esta fase del proyecto:**
- Fan-out dinámico y patrón map-reduce: la API `Send` (`langgraph.types.Send`) — diferencia entre edges estáticos paralelos (fijos en tiempo de construcción) y `Send()` (número de ramas decidido en tiempo de ejecución). **Ya implementado y probado end-to-end en la Fase 2.4/2.12.**
- Reducers en profundidad: qué pasa si dos nodos en paralelo escriben la misma clave sin reducer (se pierde uno de los dos silenciosamente) — motivo de fondo por el que `findings` necesita `Annotated[list, operator.add]` sin excepción.
- `interrupt()` + `Command(resume=...)` sobre un grafo compilado con checkpointer real — el `thread_id` debe ser único por ejecución; reutilizar un `thread_id` viejo fusiona silenciosamente el estado nuevo con un checkpoint anterior vía los reducers.

**Model Context Protocol (heredado):**
- Documentación oficial: `modelcontextprotocol.io`
- FastMCP: `gofastmcp.com`

**GitHub API — validada en la Fase 3:**
- REST API oficial: `docs.github.com/en/rest`
- Autenticación: fine-grained personal access tokens — permisos por repositorio (`Contents`, `Pull requests`) en vez de scopes anchos tipo `repo` de los tokens clásicos. Usado en Nexus por ser más granular y más apropiado para un secreto que vive en un solo servicio.
- Content negotiation vía el header `Accept` (ej. `application/vnd.github.v3.diff` para que el endpoint de un PR devuelva directamente el diff en vez de metadata JSON) — evita tener que calcular un diff a mano a partir de dos SHAs.
- Descarga de un repo completo como archivo (`zipball`) frente a recorrer el árbol pidiendo archivo por archivo vía la Contents API — la segunda opción cuesta una request por archivo y agota el rate limit rápido en repos de tamaño real; la primera cuesta 2 requests sin importar el tamaño del repo.
- Rate limiting de la API de GitHub: se reporta vía headers (`X-RateLimit-Remaining`) y con un `403`/`401` según el caso — manejado en Nexus devolviendo un error de dominio propio (`GitHubAPIError`) con mensaje claro, sin reintentos automáticos todavía (posible mejora futura, no construida).

**PostgreSQL (heredado):**
- Full-text search (`tsvector`/`tsquery`) — ya aplicado en la Fase 3 de tickets, transferible si el nuevo dominio necesita buscar código o hallazgos por texto
- `sa.Computed()` de SQLAlchemy para columnas generadas — lección real de la Fase 3.1 de tickets, transferible a cualquier columna derivada futura

**Redis (heredado, con matiz nuevo de la Fase 2.12):**
- `langgraph-checkpoint-redis`: `github.com/redis-developer/langgraph-redis`
- RediSearch (dependencia de `langgraph-checkpoint-redis`) solo crea índices sobre la base de datos lógica 0 — no es viable aislar tests de checkpointer con un índice lógico distinto, a diferencia de Postgres.

---

## 📓 Registro de progreso real

*(Esta sección documenta lo que realmente se construyó, en qué orden, con qué bugs reales y qué decisiones — se conserva íntegra a través del pivote de dominio porque casi todo su contenido es aprendizaje de ingeniería, no de dominio. Donde el pivote hace que un archivo/clase concreto ya no exista, se anota con una nota post-pivote sin borrar el hecho histórico.)*

### Fase 0 — Parcialmente cubierta ✅ (resuelta en la práctica durante la Fase 2)

Se trabajó el concepto de grafo de estado (diferencia entre cadena de middlewares tipo Express y un grafo donde los nodos no deciden a dónde ir después — esa decisión vive en los edges, mirando el estado). Validado en la práctica con el diseño de `edges.py` y su rediseño en la 2.10. MCP y human-in-the-loop se cubrieron en detalle en la Fase 1.4 y la Fase 2.7 respectivamente.

### Fase 1.1 — Infraestructura base ✅

Completada. Estructura de carpetas creada, `.gitignore` combinado Python+Node, entorno virtual con dependencias base, `.env`/`.env.example`, `main.py` con health check, Docker Compose con Postgres 16 y Redis 7 (imagen actualizada más adelante en la Fase 2.10 a `redis-stack-server`), scaffold de Next.js con TypeScript/Tailwind/pnpm.

**Aprendizajes clave:**
- Node es un runtime, no un segundo backend.
- `pydantic-settings` falla al arrancar el servidor (fail fast) si falta una variable de entorno obligatoria.
- Docker Compose necesita un `name:` explícito para no depender del nombre de la carpeta.

### Fase 1.2 — Modelos y schemas ✅ *(nota post-pivote: modelos concretos sustituidos, patrón íntegro)*

Completada en su momento con tres modelos SQLAlchemy (`Ticket`, `KnowledgeBaseEntry`, `Approval`) con relación `ForeignKey`/`relationship()` bidireccional. Refactor de español a inglés en todo el código. Alembic instalado y conectado. Schemas Pydantic v2.

**Repaso de calidad realizado tras completar la fase**, bugs reales cazados (el patrón de cada uno sigue aplicando a los modelos nuevos):
- Faltaba `relationship()` bidireccional entre dos modelos relacionados (solo estaba la `ForeignKey` a nivel de columna).
- Campos booleanos/JSON usaban `default=` de SQLAlchemy (solo aplica vía ORM) en vez de `server_default=` (aplica siempre a nivel de Postgres), permitiendo `NULL` ambiguos.
- Columnas `created_at` sin `nullable=False` a pesar de tener `server_default`.
- Un campo JSON estaba como `JSON` en vez de `JSONB` — Postgres no define operador `=` para `JSON`, rompiendo `compare_server_default` de Alembic en cuanto se activó esa opción.
- Faltaba un índice en una columna de uso constante en filtros por igualdad.
- Bug de typo real: `autoFlush` en vez de `autoflush` en `sessionmaker()` — cazado con un test, no por inspección visual.

**Aprendizajes técnicos adicionales:**
- Alembic necesita que sus modelos se importen explícitamente en `env.py`.
- `compare_server_default=True` es necesario para que `autogenerate` detecte cambios de `server_default`, pero puede romper la generación mientras una columna está a medio migrar entre tipos incompatibles.
- Migración de sintaxis antigua (`class Config:`) a Pydantic v2 (`ConfigDict`/`SettingsConfigDict`).

#### Fase 1.2 (reconstrucción, dominio Code Review) ✅ COMPLETA — 29 de julio de 2026

Diseñados y creados dos modelos SQLAlchemy nuevos: `AnalysisRequest` (origen del análisis — repo de GitHub o código pegado, nunca ambos — más el texto libre de qué revisar y el estado del pipeline) y `Finding` (un hallazgo individual producido por un especialista, con `ForeignKey` a `analysis_requests.id`, mismo patrón que `Approval` tenía con `ticket_id`).

**Decisión de diseño discutida con Alan**: `repo_url`/`pasted_code` como dos columnas nullable separadas, no un único campo genérico de "contenido" con un discriminador — son mutuamente excluyentes y la lógica downstream de cada una es genuinamente distinta (clonar/leer un repo vs. analizar texto directo).

**Concepto nuevo introducido: `CheckConstraint`**. A diferencia de `nullable`/`server_default`/`unique`, que validan una sola columna, un `CheckConstraint` evalúa una expresión booleana sobre la fila completa — aquí, que exactamente una de `repo_url`/`pasted_code` esté rellena según `source_type`. Se decidió imponer la garantía a nivel de base de datos (`ck_analysis_requests_exactly_one_source` en `__table_args__`) y no solo en Pydantic, porque hay puntos de escritura que no pasan por el schema de la API (nodos del grafo escribiendo directo con `SessionLocal()`) — mismo espíritu que `server_default` sobre `default`: la regla vive donde no puede ser esquivada. *(Este mismo patrón se reutilizó en la Fase 3.3 para una segunda constraint, `ck_analysis_requests_post_to_pr_requires_pr_number` — ver Registro, Fase 3.)*

**Estados definidos para `AnalysisRequest.status`**: `pending` → `running` → `completed` | `failed`. Se separa `failed` de `completed` porque un cliente haciendo polling necesita distinguir "aún no ha terminado" de "terminó con error". *(Ampliado más adelante en la Fase 2.9 con `completed_with_errors`, ver abajo.)*

Migración generada con `alembic revision --autogenerate`, revisada a mano antes de aplicar — salió con el mismo falso positivo ya conocido de la Fase 3 (`drop_index` sobre el índice GIN de `search_vector`), descartado sin aplicar.

Commit único con modelos + migración + cableado de imports (`app/models/__init__.py`, `app/database.py`, `alembic/env.py`) — no se separó por ser acoplamiento estructural real (ver matiz añadido a la Adenda de metodología, sección "Convención de commits").

### Fase 1.3 — Endpoints REST, Repository Pattern y CORS ✅ *(patrón íntegro, contenido de CRUD a reconstruir)*

CRUD completo para las tres entidades originales, con `PATCH` protegido contra sobrescritura vía `model_dump(exclude_unset=True)`. `get_db()` como dependencia de FastAPI. **CORS** restringido a `FRONTEND_URL`, nunca `allow_origins=["*"]`.

**Bug real cazado al levantar el servidor real** (no en Alembic ni en tests): `relationship("Approval")` fallaba con `KeyError` porque en la cadena real de ejecución nunca se importaba ese modelo, solo el otro. Resuelto centralizando la importación de todos los modelos en `app/models/__init__.py`. Este mismo patrón (módulo neutral que centraliza imports) se reutilizó después en `app/mcp_server/instance.py` para el problema análogo de import circular.

#### Fase 1.3 (reconstrucción, dominio Code Review) ✅ COMPLETA — 29 de julio de 2026

Schemas Pydantic (`AnalysisRequestCreate` con un `model_validator` que valida en la frontera de la API la misma regla que ya garantiza el `CheckConstraint` de la 1.2 — capa de error temprano y amigable, no la garantía real; `AnalysisRequestResponse` anidando `findings` directamente, a diferencia de `TicketResponse`, que nunca anidaba `approvals` — aquí ver los hallazgos **es** el propósito del endpoint, no un extra), `AnalysisRequestRepository` y `FindingRepository` (mismo patrón de Dependency Inversion que `ApprovalRepository`/`TicketRepository`), y el CRUD REST completo en `app/api/analysis_requests.py`.

**Pendiente cerrado**: `AnalysisRequestRepository.update()` lanza `AnalysisRequestNotFoundError` en vez de devolver `None` en silencio — corrige la inconsistencia arrastrada desde `TicketRepository.update()` (ver Adenda de metodología, sección "Errores de dominio").

Construido en tres commits separados por capa (`feat(schemas):`, `feat(repositories):`, `feat(api):`), decisión consciente de Alan tras discutirla: cada capa es una decisión de diseño independiente y coherente por sí sola, a diferencia de modelo+migración (ver matiz añadido a la Adenda de metodología). Los tests de cada capa se mantuvieron pegados a su capa, no en un commit aparte, por escribirse y verificarse en la misma sesión que el código que prueban.

**Limpieza del dominio de tickets, ya obsoleto** (mismo día, commit `chore: remove obsolete ticket-domain files no longer needed after the code review pivot`): se retiraron `KnowledgeBaseEntry`/`ExternalTicket`/`Notification` (modelo, schema, repository), los 4 nodos de grafo sin equivalente por nombre en el nuevo dominio (`classifier_node`, `kb_searcher_node`, `diagnosis_node`, `response_node`, `escalation_node`), `graph.py` completo (dependía de esos nodos por import; se reconstruye desde cero en la Fase 2 nueva reutilizando el patrón ya documentado de checkpointer async) y 3 de las 4 tools MCP (`search_knowledge_base`, `create_external_ticket`, `notify_team` — se queda solo `query_tickets_db`, huérfana por ahora pero viva porque depende de `TicketRepository`, que a su vez no se puede borrar todavía).

**Lección real de esta limpieza**: `Ticket` y `Approval` (modelo, schema, repository, endpoints) **no se pudieron eliminar** pese a estar marcados como "a sustituir" en el mapa de arriba — `Approval` tiene una `ForeignKey` real a `tickets.id`, así que `Ticket` queda de acompañante forzoso hasta que se rediseñe `Approval` apuntando a `analysis_request_id` (Fase 2.10 nueva). Antes de borrar cualquier archivo por "ya no se usa", hay que rastrear sus dependencias reales, no solo su rol conceptual — un primer análisis por categorías sin mirar el código real dejó pasar dos roturas concretas (`app/main.py` seguía importando y registrando el router de `knowledge_base`; `conftest.py` importaba `KnowledgeBaseEntry` directamente), detectadas solo al revisar el código línea por línea a petición explícita de Alan. Ninguna migración de Alembic se tocó ni se borró — el historial de la base de datos no se reescribe nunca por esto. *(Esta misma lección — rastrear consumidores reales, no solo el rol conceptual — reaparecería, más grande, en la retirada completa del dominio de tickets en la Fase 2.10.)*

### Fase 1.4 — Servidor MCP base ✅ *(framework íntegro, tools a reconstruir)*

Instalado `fastmcp`. Estructura en 3 archivos para evitar import circular (`tools.py` necesita `mcp` para `@mcp.tool`; `server.py` necesita importar `tools.py`; un tercer módulo neutral `instance.py` rompe el ciclo). 4 tools placeholder con datos fijos, cada una con docstring Google-style completo — remarcando que, a diferencia de cualquier otro docstring del proyecto, ese es literalmente el texto que el LLM lee para decidir cuándo y cómo llamar a la tool.

Testing en memoria con `fastmcp.Client(mcp)` — habla el protocolo MCP real sin abrir ningún puerto.

**Aprendizajes clave**: MCP tiene 3 primitivas (Tools/Resources/Prompts), solo se usan Tools; JSON-RPC 2.0 como protocolo base; la descripción de una tool es la interfaz de decisión del LLM, no documentación decorativa.

### Fase 1.5 — WebSocket hub ✅ *(100% reutilizable, sin nota post-pivote necesaria en su momento)*

`ConnectionManager` con `dict[int, list[WebSocket]]` agrupando conexiones. Instancia única a nivel de módulo (no `Depends()`, porque el estado debe compartirse entre todas las conexiones).

**Bug real encontrado y corregido**: el endpoint usaba una función que difunde a **todos** los que miran ese recurso para la confirmación de conexión de un único cliente — con dos clientes en el mismo recurso, el segundo en conectarse disparaba una confirmación fantasma también al primero. Corregido usando `await websocket.send_text(...)` directamente sobre el socket recién conectado. Test de regresión añadido.

*Nota post-pivote añadida el 1 de agosto de 2026*: `ConnectionManager`, la ruta y `send_to_ticket` se renombraron íntegros a `analysis_request_id`/`send_to_analysis_request` en la Fase 2.10, como parte de la retirada del dominio de tickets — el mecanismo en sí no cambió una línea de lógica, solo nombres.

### Fase 2 — El grafo de agentes ✅ COMPLETA (2.1 a 2.10, dominio de tickets)

#### 2.1 — Estado compartido

`TypedDict` (no Pydantic `BaseModel`) — no valida en tiempo de ejecución; decisión consciente porque los nodos son código propio cooperando, no una frontera de confianza. Cada nodo devuelve un **delta**, nunca muta el estado completo.

**Criterio de reducers, corregido durante la sesión**: la necesidad de `Annotated[list, operator.add]` depende de **cuántos nodos distintos escriben esa clave**, no de si el campo es una lista.

#### 2.2 — Nodo de entrada

Determinista, sin LLM. Reutiliza el repositorio directamente vía `SessionLocal()` manual — no llama al endpoint HTTP correspondiente, porque no hay ninguna frontera de proceso real que cruzar.

#### 2.3 — Nodo clasificador

Primer nodo con LLM real. **Migración de modelo descubierta aquí**: Llama 3.3 70B deprecado, migrado a `openai/gpt-oss-20b`. Schema de salida vive en `app/agents/schemas.py`, no en `app/schemas/` — es una frontera de Pydantic distinta (respuesta no determinista de un LLM). Nodo `async`, `try/except` acotado solo a la llamada al LLM.

#### 2.4 — Edges condicionales tras el clasificador

Comprobación de `error` primero, siempre. Categorías con el mismo destino se mantuvieron como ramas separadas por si necesitaran divergir más adelante.

#### 2.5 — Nodo buscador de KB

Primer cliente real (no en memoria) del servidor MCP. **Bug real cazado por los propios tests en la 2.10**: el `try` envolvía solo la llamada a la tool, no la apertura de la conexión — un fallo de conexión se propagaba sin capturar.

#### 2.6 — Nodo de diagnóstico

El nodo más denso de la fase: combina contexto ya reunido + una nueva consulta MCP + LLM con el modelo grande. **Bug real cazado ejecutando contra Groq real**: el proveedor devolvió `null` en un campo que el schema no permitía como `None`, violando el contrato — corregido ampliando el tipo y normalizando en el nodo.

#### 2.7 — Nodo de aprobación humana ✅ *(100% reutilizable tras el pivote)*

Concepto genuinamente nuevo en su momento: `interrupt()` congela la ejecución del grafo a mitad de un nodo, devolviendo el control a quien invocó el grafo. Exige un checkpointer (Redis vía `AsyncRedisSaver`). `thread_id` como identificador único ya disponible. Decisión de vuelta mantenida como string simple, no un diccionario con motivo — decisión consciente de no construir infraestructura para un caso de uso que el pipeline no necesitaba todavía.

#### 2.8 — Nodo de respuesta

Sin `with_structured_output()` — el consumidor final es un humano leyendo texto.

#### 2.9 — Nodo de escalado *(nota post-pivote: sin equivalente directo en code review, ver Fase 2.11 de la reconstrucción, más abajo)*

Reutiliza el diagnóstico ya generado como resumen, sin gastar una llamada extra al LLM para "resumir el resumen".

#### 2.10 — Ensamblaje completo, checkpointer de Redis, validación end-to-end y testing con mocks

**Bug de infraestructura real**: la imagen Docker de Redis por defecto no incluye RediSearch, necesario por `langgraph-checkpoint-redis` — corregido cambiando a `redis/redis-stack-server:latest`.

**Testing con mocks, 17 tests**: cazó un tercer bug real (`kb_searcher_node`, `try` mal posicionado) que había pasado desapercibido en revisión de código y prueba manual.

**Pendientes que quedaron explícitos al cerrar la Fase 2** (algunos ya resueltos en la Fase 3, ver abajo; otros quedan obsoletos por el pivote; **todos resueltos definitivamente en la reconstrucción de la Fase 2 del dominio Code Review, ver más abajo**):
- Test de integración de `human_approval_node` con grafo + checkpointer reales — **resuelto el 1 de agosto de 2026**, en la Fase 2.12 de la reconstrucción.
- Conectar `build_graph()` a FastAPI vía lifespan events — **sigue pendiente**, incluso tras la reconstrucción y el cierre de la Fase 3 (ver Fase 2.12 de la reconstrucción y el cierre de Fase 3 más abajo).
- Inconsistencia de `TicketRepository.update()` — **cerrada del todo el 1 de agosto de 2026**: el archivo se eliminó por completo en la retirada del dominio de tickets.
- Marker de plataforma de `pywin32` — **sigue pendiente**, Fase 5.6.

#### Fase 2 (reconstrucción, dominio Code Review) ✅ COMPLETA — 1 de agosto de 2026

Los 12 puntos del roadmap (2.1 a 2.12) completos y verificados con 88 tests en verde. El grafo funciona de extremo a extremo: `entry_node` → `router_node` → fan-out paralelo de especialistas → `synthesizer_node` → `human_approval_node`, con `failure_node` como terminal honesto para cualquier fallo pre-fan-out.

**2.1 — `CodeReviewState`**: mismo `TypedDict` + reducers que en tickets, pero `findings` es ahora el caso de uso **central** del patrón (hasta 4 escritores concurrentes reales), no periférico como `node_history` lo era antes. Verificado con una pregunta de control: un campo con un único escritor (ej. un futuro `documentation_summary`) no necesitaría `operator.add` — respondida correctamente, confirmando que el criterio real es "cuántos nodos distintos escriben esta clave", no "es una lista".

**2.2 — `entry_node`**: determinista, sin LLM. Resuelve `code_content` desde `pasted_code` directo o vía la tool MCP `read_repository_files` — diseñado contra el contrato de esa tool (`{"repo_url": str} → contenido`) antes de que exista de verdad (pendiente hasta la Fase 3.1), mismo principio Open/Closed ya validado con `kb_searcher_node` en tickets. **Decisión de persistencia**: `code_content` nunca se persiste en `analysis_requests` — el criterio real no es "en qué punto del grafo estamos" sino "¿existe una columna de dominio para esto?". Solo se persiste `status="running"`.

**2.3 — `router_node` + `RouterDecision`**: reemplaza a `classifier_node`. Mismo patrón LLM + `with_structured_output()`, pero la salida pasa de un valor único a una lista (`agents_to_run`), reflejando que el Router elige un subconjunto de tamaño variable, no una categoría entre fijas.

**Decisión de arquitectura discutida con Alan**: ¿quién decide si el sistema debe comentar en el PR real (`post_to_pr`)? Dos opciones sobre la mesa — que el Router lo infiera del texto libre de `review_request` (más "agéntico", pero no determinista sobre una acción pública e irreversible), o un campo explícito en `AnalysisRequestCreate` marcado por el usuario. Se eligió la segunda, por el mismo principio ya establecido con `human_approval_node`: ningún LLM debe controlar el gatillo de un efecto externo irreversible. `RouterDecision` (en `agents/schemas.py`) por tanto nunca incluye `post_to_pr`.

Deuda mecánica encontrada y cerrada de paso: `config.py` seguía con `CLASSIFIER_MODEL`/`DIAGNOSIS_MODEL` (nombres de tickets) en vez de `ROUTER_MODEL`/`SPECIALIST_MODEL` ya documentados en el roadmap — renombrado en commit propio (`fix(config):`).

**2.4 — Fan-out dinámico con `Send()`**: concepto genuinamente nuevo, decisión de arquitectura tomada con Alan tras explicar tradeoffs entre edges estáticos + guardia interna (más simple, arranca-y-sale para los no elegidos) vs. `Send()` dinámico (`langgraph.types.Send`, patrón map-reduce "de libro", solo invoca lo realmente elegido). Se eligió **`Send()`**.

Punto de confusión real superado en la explicación: entender que cada `Send(nombre_nodo, payload)` no reenvía el `CodeReviewState` completo — cada especialista invocado vía `Send()` solo ve el payload específico que se le pasó (`code_content`, `review_request`, `analysis_request_id`), nunca `agents_to_run` ni los `findings` de otros. El mecanismo de combinar los resultados de vuelta sigue siendo el mismo reducer `operator.add` de la 2.1 — `Send()` solo decide a quién invocar y con qué, no cómo se fusionan los resultados. Se usó un diagrama para trazar el recorrido completo (Router → `route_after_router` → fan-out paralelo → merge vía reducer) hasta que quedó claro.

**2.5–2.8 — Los cuatro especialistas**: `security_agent`, `performance_agent`, `design_patterns_agent`, `best_practices_agent` — mismo patrón (LLM + `with_structured_output()` con `SPECIALIST_MODEL`, persistencia inmediata de cada `Finding` vía `FindingRepository`), escrito primero en detalle para `security_agent` y luego replicado para los otros tres tras confirmarse que el patrón ya estaba entendido (código mecánico, no genuinamente nuevo).

**Concepto nuevo real**: `failed_specialists: Annotated[list[str], operator.add]` se añade a `CodeReviewState`, separado de `error`. Un especialista que falla (LLM o persistencia) **nunca** toca `state["error"]` — ese campo sigue reservado para fallos secuenciales pre-fan-out (`entry_node`/`router_node`) que sí deben parar el grafo entero. Perder un especialista de cuatro no debe descartar los tres hallazgos reales de los demás; por eso `failed_specialists` tiene su propio reducer, por la misma razón que `findings` lo necesita: múltiples escritores concurrentes.

**2.9 — `synthesizer_node`**: decisión de arquitectura discutida — ¿el informe final lo redacta un LLM libremente, o es puro formateo determinista de los `findings` ya estructurados? Se descartaron ambos extremos por sus riesgos (un LLM puede omitir un hallazgo real al redactar; Python puro no puede conectar patrones entre especialistas) a favor de un **híbrido**: una sección determinista en Python, ordenada por severidad, que garantiza que ningún finding real desaparece nunca — y encima, un resumen ejecutivo redactado por LLM que añade valor (conexión de patrones, priorización) sin ser el único guardián de la exhaustividad. Mismo principio de fondo que la decisión de `post_to_pr` en la 2.3: no dejar que el LLM sea el único punto de fallo para algo que debe garantizarse.

Requirió columna nueva `final_report` (Text, nullable) en `analysis_requests`, más un matiz en `status`: se añadió el valor `"completed_with_errors"` (distinto de `"completed"`) para reflejar honestamente cuando el análisis terminó pero algún especialista falló — sin invalidar los hallazgos reales que sí se produjeron.

**Bug real cazado por los propios tests, no por revisión de código**: `"completed_with_errors"` tiene 22 caracteres, pero `status` era `String(20)` — Postgres rechazaba el `UPDATE` con `StringDataRightTruncation`. Migración de ensanche a `String(30)` generada, revisada y aplicada.

**Segundo bug real, más sutil**: tests que verificaban el `status` tras la ejecución del nodo fallaban con valores viejos (`'pending'` en vez de `'completed'`) a pesar de que el `UPDATE` sí se ejecutaba correctamente contra la base real. Causa: el nodo persiste con su propia sesión (`SessionLocal()`), distinta a la sesión del fixture del test — y esa sesión del test ya tenía el objeto cacheado en su identity map desde que lo creó, antes del `UPDATE` externo. Solución: `db_session.expire_all()` antes de releer, para forzar una lectura fresca en vez de servir la copia en caché. Lección transferible a cualquier test futuro que verifique una escritura hecha por una sesión distinta a la del fixture.

**2.10 — `human_approval_node` + retirada completa del dominio de tickets**: mecanismo 100% reutilizable (`interrupt()`, checkpointer Redis, `thread_id`) — cambia solo el disparador: ya no es "hay `pending_actions`" sino `post_to_pr == True` explícito. A diferencia del dominio de tickets, aquí el nodo también persiste una fila real de `Approval` (vía `ApprovalRepository`) antes de pausar, para que el estado de la aprobación sea consultable desde fuera del grafo (`GET /approvals/{id}`) mientras está pausado — no solo visible en el payload efímero del `interrupt()`. Si el humano rechaza, `post_to_pr` se pone a `False` en el estado, para que futuros nodos (`post_pr_comment`, Fase 3.3) no necesiten lógica extra para enterarse del rechazo.

**Bloqueante real encontrado al construir esto, no anticipado**: `Approval` seguía con una `ForeignKey` real a `tickets.id` — ya no era deuda teórica, bloqueaba directamente la construcción de este nodo. Se discutieron dos caminos con Alan: rediseño polimórfico (`Approval` admite `ticket_id` **o** `analysis_request_id`, con `CheckConstraint` de exclusividad mutua, igual que `source_type` en `AnalysisRequest` — no rompe nada del dominio de tickets) vs. **retirada completa** del dominio de tickets ahora que ya no se usa. Alan eligió la retirada completa, decisión consciente de no arrastrar código muerto solo por comodidad.

**Alcance real de la retirada** (mayor de lo que parecía a primera vista — se hizo paso a paso, verificando en cada uno):
- Modelo `Ticket` eliminado; `Approval` rediseñado con `analysis_request_id` como único FK (migración con `DELETE FROM approvals` explícito para las filas huérfanas del dominio viejo, documentado en el propio archivo de migración como pérdida de datos intencionada, no accidental).
- `schemas/ticket.py`, `repositories/ticket_repository.py`, `api/tickets.py` eliminados; `schemas/approval.py`, `repositories/approval_repository.py`, `api/approvals.py` reescritos sobre `analysis_request_id`.
- `query_tickets_db` (última tool MCP viva del dominio viejo) retirada; servidor MCP queda sin tools hasta la Fase 3.1, con placeholder documentado — mismo patrón ya usado con `edges.py` en la 1.3.
- WebSocket (`ConnectionManager`, ruta, `send_to_ticket`) renombrado íntegro a `analysis_request_id`/`send_to_analysis_request`.
- `tests/test_database.py` migrado de `Ticket` a `AnalysisRequest`.

**Bugs reales encontrados en el proceso** (cadena de imports rotos tras borrar `ticket.py`, cazados uno a uno con `pytest`, no todos anticipados por `grep` de antemano): `app/database.py`, `app/models/__init__.py`, `alembic/env.py` y `tests/conftest.py` seguían importando `Ticket` directamente. Mismo patrón de lección que en la 1.3 (rastrear consumidores reales, no solo el rol conceptual de un archivo) — pero esta vez con una variante nueva: un `relationship("Approval", back_populates="ticket")` colgando en el propio modelo `Ticket` (ya reescrito `Approval` sin su lado, así que el `back_populates` apuntaba a nada) habría roto la configuración de mappers de SQLAlchemy **para toda la suite**, no solo para tests de tickets, de no haberse detectado que `Ticket` ya se había borrado por completo en el mismo paso.

**Migración de Alembic con orden de dependencias real, lección de ingeniería genuina**: al generar la migración de la retirada, `--autogenerate` propuso `drop_table('tickets')` **antes** de quitar la FK de `approvals` que apuntaba a esa tabla — Postgres rechaza borrar una tabla mientras algo la referencia. Corregido a mano: quitar la FK primero, borrar `tickets` al final; y en el `downgrade()`, crear la tabla `tickets` **antes** de intentar recrear la FK hacia ella (el orden inverso exacto). `autogenerate` no razona sobre estas dependencias entre operaciones — solo describe el diff final deseado, no un orden de aplicación seguro.

**2.11 — Sin `escalation_node`, pero con `failure_node`**: conclusión tras analizar el rol de `escalation_node` en tickets — no existe un "equipo de soporte humano" al que escalar en este dominio, y si los especialistas fallan parcialmente, `synthesizer_node` ya lo refleja honestamente (`completed_with_errors` + `failed_specialists`) sin necesitar ningún paso adicional.

Pero el análisis destapó un **hueco real, no inventado**: si `entry_node` o `router_node` fallan antes del fan-out, nada actualizaba el `status` de la `AnalysisRequest` — se quedaría en `"running"` para siempre, aunque el análisis ya hubiera muerto. Se añadió `failure_node`, un nodo terminal mínimo que persiste `status="failed"` antes de terminar, y dos edges nuevos que faltaban (`route_after_entry`, que no existía hasta ahora, y `route_after_synthesizer`, que salta `human_approval_node` si `synthesizer_node` mismo falló al persistir) redirigiendo a este nodo en vez de a `END` directamente.

**2.12 — Ensamblaje completo, checkpointer de Redis, test de integración real**: `build_graph(checkpointer)` recibe el checkpointer ya creado en vez de abrir su propia conexión — decisión consciente de mantener la función de ensamblaje puro, desacoplada del ciclo de vida de la conexión (que sigue pendiente de resolver vía lifespan events de FastAPI, mismo pendiente heredado sin resolver de tickets — **sigue pendiente incluso tras el cierre de la Fase 3**, ver más abajo).

**El test de integración de `human_approval_node` + grafo + checkpointer real, pendiente sin resolver desde el dominio de tickets, se cerró aquí — con dos bugs reales de por medio**:
1. `SessionLocal` sin parchear en los nodos que tocan BD dentro del test de integración — los nodos golpeaban la base de dev real en vez de `nexus_test`, y el grafo fallaba en `entry_node` antes incluso de llegar a `router_node`. Mismo gotcha ya documentado desde la Fase 3 de tickets (`Depends(get_db)` no protege código que llama a `SessionLocal()` directo), aplicado ahora al propio test de grafo.
2. Colisión de `thread_id`: usar `str(analysis_request.id)` como `thread_id` colisionaba con un checkpoint viejo en Redis bajo la misma clave (`"1"`, de pruebas manuales del grafo de tickets original) — el estado nuevo se fusionaba silenciosamente con el checkpoint viejo vía los reducers, mostrando nombres de nodos del dominio de tickets (`classifier`, `kb_searcher`, `response`) en `node_history`. Un primer intento de aislar con un índice lógico de Redis distinto (`/1`) falló porque **RediSearch solo permite crear índices en la base de datos lógica 0** (`langgraph-checkpoint-redis` depende de RediSearch) — limitación real de la tecnología, no error de configuración. Solución final: `thread_id` como UUID único por ejecución, sin tocar la base de Redis de desarrollo en absoluto.

**Pendiente documentado a propósito, no resuelto**: cada ejecución de este test deja un checkpoint huérfano en Redis bajo un UUID que nunca se reutiliza — deuda de bajo impacto, limpiable con `FLUSHDB` manual en desarrollo si hiciera falta, no automatizada por ahora.

Con esto, la Fase 2 del dominio Code Review queda **completa de extremo a extremo**: 88 tests en verde, grafo funcional desde `entry_node` hasta `human_approval_node`/`failure_node`, con el mecanismo de `Send()`, reducers, `interrupt()` y checkpointer de Redis validados juntos por primera vez, no solo en aislamiento por nodo.

### Fase 3 — Servidor MCP completo, dominio de tickets ✅ COMPLETA (3.1 a 3.5) — cerrada justo antes del pivote

Las 4 tools placeholder de la Fase 1.4 se conectaron a PostgreSQL real, con autenticación y validación añadidas al final. **Todo el contenido de dominio (tickets, knowledge base) queda obsoleto tras el pivote** — pero los tres aprendizajes de ingeniería siguientes son de propósito general y se llevan intactos a la reconstrucción:

**1. `sa.Computed()` para columnas generadas**: al añadir búsqueda full-text (`tsvector`/`tsquery`) sobre una tabla, la columna `search_vector` se definió con `Computed(..., persisted=True)` **en el modelo SQLAlchemy**, no solo en la migración de Alembic — porque los tests usan `Base.metadata.create_all()` (no Alembic) para levantar la base de test, y una columna generada solo descrita en SQL crudo de la migración nunca aparecería en esa base de test, rompiendo los tests por columna inexistente. Transferible a cualquier columna derivada futura.

**2. `autogenerate` de Alembic no es de fiar a ciegas con columnas funcionales/generadas**: se detectó dos veces el mismo falso positivo — Alembic proponía `drop_index` sobre el índice GIN de `search_vector` en migraciones que no tenían nada que ver con esa tabla, simplemente por cómo compara índices sobre columnas `Computed`/`TSVECTOR`. Regla adoptada: **revisar siempre a mano el archivo generado por `--autogenerate` antes de aplicar**, nunca correr `alembic upgrade head` a ciegas tras generar. *(Confirmado necesario una vez más en la Fase 2.10 de la reconstrucción, con un tipo de error distinto: orden de dependencias entre operaciones, no falsos positivos sobre columnas generadas.)*

**3. Las tools MCP no heredan `Depends(get_db)` de FastAPI**: usan `SessionLocal()` directo, así que sus tests necesitan parchear `SessionLocal` en el módulo `tools.py` específicamente — `app.dependency_overrides` (que sí protege los tests de endpoints REST) no tiene ningún efecto aquí. Ya documentado arriba, en la Adenda de metodología.

**Además, en esta fase**:
- Se implementó idempotencia real (no solo en Python, sino garantizada por un índice único a nivel de base de datos) para la tool que simulaba un sistema externo — patrón transferible a `post_pr_comment` en el nuevo dominio, donde comentar dos veces el mismo hallazgo sería un problema real y visible en un PR de verdad.
- Se añadió autenticación al servidor MCP con `StaticTokenVerifier` de FastMCP (elegido sobre `JWTVerifier`/`BearerAuthProvider` porque el caso de uso es un secreto único y estático, no un flujo OAuth con múltiples usuarios) y validación de parámetros en la frontera de cada tool con `Literal`/`Annotated[..., Field(...)]` — ambos 100% reutilizables tal cual.
- Se discutió el concepto de **prompt injection**: el texto de entrada, controlado por el usuario, se inserta directo en el prompt de varios nodos, sin frontera dura entre "instrucción" y "dato". Mitigaciones de bajo coste identificadas: delimitar claramente el contenido del usuario dentro del prompt (ej. con tags), y el hecho de que `human_approval_node` ya actúa como defensa estructural — ninguna acción de alto impacto se ejecuta sola, sin importar qué tan manipulado esté el razonamiento de un nodo anterior. Este mismo principio aplica ahora a `post_pr_comment`, con el matiz añadido de que además hay un secreto real (`GITHUB_TOKEN`) que nunca debe llegar al prompt de un LLM.
- Se clarificó, a raíz de una duda real de Alan, el criterio correcto para decidir dónde cortar un commit — ver Adenda de metodología arriba.

### Fase 3 (reconstrucción, dominio Code Review) ✅ COMPLETA — 2 de agosto de 2026

Las tres tools planificadas (3.1 a 3.3) construidas y probadas; 3.4 evaluada y descartada por ahora; 3.5 ya estaba resuelta. 118 tests en verde en total.

**3.1 — `read_repository_files`**: decisión `httpx` directo vs. `PyGithub` tomada explícitamente por un tradeoff pedagógico, no solo técnico — con solo 3 tools sobre la mesa, `PyGithub` habría abstraído exactamente lo que esta fase busca aprender de verdad (rate limiting real, headers de auth reales), a cambio de una dependencia nueva para poco beneficio real. `httpx` ya vivía en `requirements.txt`.

Diseño interno: en vez de recorrer el árbol del repo pidiendo cada archivo individualmente vía la Contents API (1 request por archivo — quema el rate limit en un repo de cientos de archivos), se descarga el repo completo como zipball (`GET /repos/{owner}/{repo}/zipball/{ref}`) y se filtra en memoria — 2 requests sin importar el tamaño del repo. Filtrado por extensión de código + exclusión de directorios de ruido (`node_modules`, `.git`, `venv`, etc.) + límites de tamaño por archivo (100 KB) y total (500 KB), porque `code_content` termina entero en el prompt de los especialistas — límites de arranque, no ajustados contra un modelo real todavía.

**3.2 — `get_pr_diff`**: en vez de pedir metadata del PR y calcular el diff a mano contra la compare API, se usa content negotiation de GitHub (`Accept: application/vnd.github.v3.diff` sobre el endpoint de pulls) para que la API devuelva el diff unificado ya armado en un solo request. Un PR sin cambios devuelve string vacío — tratado como resultado válido, no como error.

No quedó cableada a ningún nodo del grafo todavía (a diferencia de `read_repository_files`, que `entry_node` ya esperaba desde la Fase 2.2) — decisión consciente de mantener el análisis (repo completo vía `read_repository_files`) desacoplado de "a qué PR se comenta" (`pr_number`), en vez de hacer que `entry_node` analice solo el diff del PR. Motivo: cambiar `entry_node` (Fase 2.2, ya cerrada y probada) ampliaba mucho el alcance de esta fase; queda anotado como mejora futura posible, no como deuda oculta — candidata natural si en algún momento se decide que el análisis debería ceñirse exactamente al diff del PR en vez de al repo completo.

**3.3 — `post_pr_comment` + resolución de `pr_number`**: primera acción de escritura real del proyecto contra una API externa (`POST /repos/{owner}/{repo}/issues/{pr_number}/comments` — GitHub trata los PRs como issues para comentarios generales, no es una simplificación de Nexus).

Construir esta tool obligó a resolver un hueco real: `AnalysisRequest` no tenía forma de identificar a qué PR pertenecía un análisis. Se agregó `pr_number` (columna nullable + migración) y una constraint nueva: `post_to_pr=True` exige `source_type='github_repo'` **y** `pr_number` no nulo (misma técnica de `CheckConstraint` ya usada en la 1.2 para `ck_analysis_requests_exactly_one_source`).

Decisión de diseño explícita, no obvia: se discutió con Alan permitir `post_to_pr=True` también con `source_type='pasted_code'`, agregando un campo `target_repo_url` independiente del origen del análisis. Se descartó — publicar un comentario automático en un PR real sobre código pegado que puede no ser el diff de ese PR es engañoso para quien lo lee después; coherencia de dominio sobre flexibilidad especulativa que nadie había pedido.

Esta restricción **rompió dos tests existentes** que combinaban `pasted_code` + `post_to_pr=True` (`test_graph.py` y, en una segunda pasada, `test_human_approval_node.py` — este último se pasó por alto en la primera revisión y solo se detectó al correr `pytest` completo localmente). **Lección de metodología real, añadida a la Adenda**: cuando se agrega una constraint sobre un campo existente, hay que grepear ese campo en **toda** la carpeta de tests, no solo revisar el archivo que a priori parece afectado.

`post_comment_node` nuevo, cableado justo después de `human_approval_node` (edge fija, no condicional — el nodo se auto-anula internamente si `post_to_pr` es `False`, mismo idioma que usa `human_approval_node` para su propio gate). Decisión de manejo de errores explícita, tercera variante del mismo principio ya visto con `failed_specialists`: una falla al postear el comentario **nunca** escribe `state["error"]`. Para cuando este nodo corre, `synthesizer_node` ya persistió un status final exitoso (`completed`/`completed_with_errors`) — la revisión en sí ya tuvo éxito. Tratar la falla del comentario como `error` enrutaría a `failure_node` y sobreescribiría ese status con `"failed"`, lo cual sería falso respecto a lo que realmente pasó. No hay todavía un campo persistido para "se publicó el comentario y cuál es su URL" — se notifica solo por WebSocket de forma transitoria; deuda anotada explícitamente, candidata natural para cuando se construya el dashboard de la Fase 4.

**3.4 — evaluada y descartada por ahora**: el flujo actual recibe `repo_url` + `pr_number` directamente del usuario, sin necesidad de listar PRs abiertos primero. No es deuda — es una tool que el diseño actual del flujo de entrada no necesita.

**3.5 — sin cambios**: responsabilidad de que `GITHUB_TOKEN` nunca llegue al prompt de un LLM verificada por construcción — el token vive únicamente dentro de `_headers()` en `github_client.py`.

**Verificación**: el trabajo de esta fase se hizo sin acceso a una instancia real de Postgres/Redis en el entorno donde se escribió el código, así que la verificación se hizo en dos niveles — tests unitarios con la red completamente mockeada (`httpx.AsyncClient` parcheado con el mismo patrón ya usado para clientes MCP) corridos en un entorno Python aislado, y `pytest --collect-only` contra la suite completa para detectar errores de import sin depender de servicios reales. Los tests que sí requieren Postgres/Redis reales (`test_graph.py`, los de modelo/repositorio/API) se corrieron localmente por Alan, donde se encontró y corrigió la colisión de `test_human_approval_node.py` mencionada arriba.

**Pendiente heredado, no de esta fase**: conectar `build_graph()` a FastAPI vía lifespan events sigue sin resolver — a fecha de cierre de la Fase 3, no hay ningún endpoint que dispare el grafo de verdad contra una petición real. Es el bloqueante real antes de poder probar el flujo completo end-to-end o de empezar la Fase 4.

### Pendiente heredado resuelto: wiring del grafo a FastAPI — 2 de agosto de 2026

Antes de arrancar la Fase 4 de verdad, se cerró el pendiente anotado arriba. Resultó ser más grande de lo que su nombre ("lifespan events") sugería — al revisar el código real se confirmó que **ningún** endpoint invocaba `build_graph()` ni disparaba `ainvoke()`, y que tampoco existía forma de reanudar un grafo pausado en `human_approval_node` vía HTTP. Se resolvió en tres piezas:

1. **Lifespan en `main.py`**: `AsyncRedisSaver.from_conn_string(settings.REDIS_URL)` se abre una vez al arrancar la app (dentro de un `@asynccontextmanager`), se llama `checkpointer.asetup()`, y el grafo compilado se guarda en `app.state.graph` — mismo principio que `engine`/`SessionLocal` ya aplican para Postgres en `database.py`, hecho explícito aquí porque `AsyncRedisSaver` no trae pooling propio.
2. **`app/agents/runner.py` (nuevo)**: dos funciones, `run_analysis()` y `resume_analysis()`, que llaman a `graph.ainvoke()` (más tarde migrado a `graph.astream()`, ver Fase 4.2) con `thread_id=str(analysis_request_id)` — la convención que permite que una request posterior (la decisión de aprobación) encuentre y reanude el mismo hilo. Ambas corren como `BackgroundTasks`: cualquier excepción se loggea, nunca se relanza.
3. **Dos endpoints nuevos disparan esas funciones**: `POST /analysis-requests/` ahora agenda `run_analysis()` tras crear la fila; y se añadió `POST /approvals/{id}/decision` (schema `ApprovalDecision`, `Literal["approved", "rejected"]`) — endpoint que no existía en absoluto — que agenda `resume_analysis()`. Decisión de diseño explícita: este endpoint no actualiza el registro de `Approval` directamente (eso lo sigue haciendo `human_approval_node` al despertar); su único trabajo es encontrar el hilo pausado correcto y entregarle la decisión. Guarda 409 contra decidir dos veces la misma aprobación.

**Gotcha real descubierto al verificar**: `TestClient` de Starlette corre los `BackgroundTasks` de forma síncrona dentro de la propia request de test — así que cualquier test existente que simplemente creara un `AnalysisRequest` habría disparado un run real del grafo, con llamadas reales a Groq y GitHub. Corregido en `tests/api/conftest.py`: el fixture `client` deja un grafo mockeado en `app.state.graph` antes de construir el `TestClient`.

**Incidente de esta sesión, anotado por transparencia**: al verificar imports, la IA sobreescribió accidentalmente `backend/.env` con valores dummy. Como `.env` está en `.gitignore`, no hubo forma de recuperarlo — Alan tuvo que rellenar de nuevo sus credenciales reales. Regla adoptada desde entonces: nunca leer, copiar ni escribir sobre un `.env` real; solo `.env.example`, y variables de entorno inline para cualquier verificación en sandbox.

### FASE 4.1 — Cliente API + tipos TypeScript ✅ — 2 de agosto de 2026

`src/lib/api/types.ts`: tipos que reflejan los schemas de Pydantic, escritos a mano (no generados — con 8 endpoints en total, un paso de codegen sería más ceremonia que problema). El caso interesante: `AnalysisRequestCreate` es una **unión discriminada** que codifica en TypeScript las mismas dos reglas que los `model_validator` del backend imponen (exactamente una fuente según `source_type`; `post_to_pr=true` exige `github_repo` + `pr_number`) — un formulario que intente una combinación inválida falla al compilar, no al hacer el roundtrip a la API.

`src/lib/api/client.ts`: wrapper de `fetch` con una clase `ApiError` que parsea el campo `detail` que FastAPI pone tanto en `HTTPException` (404/409) como en errores de validación de Pydantic (422) — necesario porque "Approval not found" y "Approval already decided" son errores que una UI necesita distinguir, no solo un código de estado.

Verificado con `tsc --noEmit` en un proyecto TypeScript aislado (mismas opciones del `tsconfig.json` real) — el `node_modules` de pnpm tenía symlinks rotos al montarse desde Windows en el sandbox Linux donde se verificó, así que no se pudo correr `tsc` directo sobre el proyecto real; recomendado confirmarlo también en local.

### FASE 4.2 — `useWebSocket` + traza de agentes en paralelo ✅ — 2 de agosto de 2026

**Decisión de diseño**: en vez de instrumentar cada uno de los nueve nodos del grafo para que mande su propio mensaje WebSocket, se aprovechó que LangGraph ya sabe qué nodo terminó y cuándo. `runner.py` pasó de `graph.ainvoke()` a `graph.astream(..., stream_mode="updates")`, que entrega un chunk `{nombre_nodo: delta}` por cada nodo que termina — iterarlo hasta el final tiene los mismos efectos que `ainvoke()` (cada nodo corre igual una vez), solo que de paso se ve cada paso.

`app/agents/ws_events.py` (nuevo): función pura `build_event(chunk)` que traduce cada chunk a un evento JSON, sin ningún async ni mock de por medio (mismo espíritu que las funciones de `edges.py`, directamente testeables). El caso interesante del fan-out: no existe una señal explícita de "estos especialistas empezaron ahora" — se deriva del propio chunk de `router_node`, leyendo `agents_to_run` de su delta, porque ese es exactamente el momento real en que el fan-out de la Fase 2.4 los dispara. Un chunk con un `error` truthy en su delta, de cualquier nodo, se trata como señal general de fallo (`run_failed`), sin hardcodear qué nodo puede fallar. El chunk especial `"__interrupt__"` (con el payload real de `human_approval_node`) se traduce a `approval_required`.

Frontend: `useAnalysisRequestSocket` (`src/lib/hooks/useWebSocket.ts`) separa los eventos JSON estructurados (con campo `type`) de los avisos de texto plano que `entry_node`/`post_comment_node` ya mandaban antes — ambos conviven en el mismo socket, distinguidos solo por si el mensaje parsea como JSON con `type`. `src/lib/agent-trace.ts` deriva, de forma pura, el estado de cada especialista (running/done/failed) a partir del stream de eventos — separado del componente `AgentTrace.tsx` por la misma razón que `ws_events.py` está separado de `runner.py`: lógica testeable sin montar nada.

**Gotcha al verificar los tests existentes**: el fixture `client` de `tests/api/conftest.py` mockeaba `ainvoke`, que dejó de usarse — hubo que cambiarlo a un `astream` mockeado (un generador async que termina sin producir nada, `async def _empty_astream(): return; yield`), y ajustar la aserción de `test_approvals.py` de `ainvoke.assert_awaited()` a `astream.assert_called()`.

### FASE 4.3 — Vista de aprobación (`ApprovalPanel`) ✅ — 2 de agosto de 2026

Escucha el mismo WebSocket buscando el evento `approval_required` (payload directo del `interrupt()` de `human_approval_node`: `approval_id`, `proposed_action`, `final_report`) y expone los botones de aprobar/rechazar contra `POST /approvals/{id}/decision`. Sabe que la decisión surtió efecto real cuando llega el evento `node_finished` de `human_approval` o `post_comment` — no solo por la respuesta 200 del POST, que únicamente confirma que se agendó.

**Hueco real encontrado y cerrado**: si el usuario recargaba la página después de que el `interrupt()` ya hubiera saltado, no había forma de recuperar esa aprobación pendiente — `GET /approvals/` devolvía todas sin filtrar. Se añadió un filtro `analysis_request_id` opcional al endpoint (más `ApprovalRepository.get_by_analysis_request_id()`), y `ApprovalPanel` ahora hace un fallback por REST (`GET /approvals/?analysis_request_id=` + `GET /analysis-requests/{id}` para el `final_report`, que no vive en `ApprovalResponse`) cuando no hay evento en vivo que capturar.

**De paso**: al intentar comitear `frontend/.env.example`, se descubrió que `frontend/.gitignore` tiene `.env*` sin ninguna excepción (a diferencia del `.gitignore` raíz, que sí tiene `!.env.example`) — se añadió esa misma línea de excepción al del frontend.

### FASE 4.4 — Métricas ✅ — 2 de agosto de 2026

Antes de construir nada: de las tres métricas que este mismo documento nombra como ejemplo ("hallazgos por especialidad, tiempo de análisis, PRs comentados"), la tercera no se podía calcular con datos reales — `post_comment_node` nunca persistía si el comentario se había publicado ni su URL, solo lo notificaba por WebSocket de forma efímera (deuda ya anotada en el cierre de la Fase 3.3). Se decidió cerrar ese hueco en vez de construir la vista de métricas incompleta desde el día uno: migración nueva (columna `pr_comment_url`, nullable, en `analysis_requests`) y `post_comment_node` persistiéndola al publicar con éxito — nunca en fallo, sin tocar `state["error"]`, mismo invariante de siempre.

`app/repositories/metrics_repository.py` (nuevo): repositorio propio, no métodos añadidos a `AnalysisRequestRepository`/`FindingRepository` — agregar across ambas entidades es una responsabilidad distinta a la de cada una. Agregación en SQL (`func.count`/`group_by`), no cargando todo a Python y contando ahí, para no convertirse en un full-table scan accidental el día que haya miles de filas en vez de docenas. `average_analysis_seconds` es una aproximación explícita, no una medición exacta: se deriva de `created_at`/`updated_at` porque no existe una columna `completed_at` dedicada — asume que nada vuelve a tocar la fila tras llegar a un status terminal, cierto hoy pero no garantizado por ninguna constraint.

`GET /metrics/` nuevo, registrado en `main.py`. `MetricsPanel.tsx` en el frontend: fetch simple al montar, sin WebSocket — una fotografía agregada no necesita vivir en tiempo real como sí lo necesita una ejecución en curso.

**Verificación de todo este bloque (pendiente + 4.1-4.4)**: sin acceso a Postgres/Redis reales en el entorno donde se escribió el código (sin Docker/sudo disponibles), la verificación se limitó a `python -m py_compile`, importar `app.main` de extremo a extremo con variables de entorno dummy (confirmando lifespan + rutas nuevas en el schema de OpenAPI), y `pytest --collect-only` sobre la suite completa — 142 tests recolectados sin error de import, frente a los 118 de cierre de la Fase 3. La ejecución real contra Postgres/Redis, y `tsc`/`pnpm build` reales del frontend, se corrieron en local por Alan y confirmaron verde.

**Pendiente explícito para retomar la Fase 4**: ninguna página de Next.js compone `AgentTrace`/`ApprovalPanel`/`MetricsPanel` todavía contra un `analysisRequestId` real — `src/app/page.tsx` sigue siendo el scaffold por defecto de `create-next-app`. Los tres componentes existen, compilan y están verificados por separado, pero no hay una ruta real que los muestre juntos.

---

## 🔄 Nota de pivote (29 de julio de 2026)

En este punto, con la Fase 3 recién cerrada y las Fases 0-2 completas y probadas en el dominio de gestión de tickets, el proyecto pivota a un sistema de Code Review multi-agente (ver sección "Pivote de dominio" al principio de este documento para el razonamiento completo). A partir de aquí, el Registro de progreso real continúa documentando el trabajo bajo el nuevo dominio — reconstruyendo la Fase 1.2 en adelante con los modelos y nodos nuevos, mientras se apoya en toda la mecánica ya validada arriba.

---

## 📝 Cómo usar este documento como base de documentación

A medida que vayas construyendo cada fase (ahora bajo el dominio de Code Review), documenta lo que aprendes directamente en este archivo, en la sección "Registro de progreso real", continuando después de la "Nota de pivote". Añade una entrada por fase con los conceptos que más costó entender, las decisiones de arquitectura tomadas y por qué, los errores cometidos y cómo se resolvieron, y los recursos más útiles — igual que se hizo con las Fases 0 a 3 del dominio original, y con la reconstrucción completa de la Fase 1, la Fase 2 y la Fase 3.

---

*Última actualización: 2 de agosto de 2026 (sesión posterior) — pendiente heredado de la Fase 3 resuelto (wiring real de `build_graph()` a FastAPI vía lifespan events, `runner.py`, endpoints de disparo/reanudación); Fase 4 con sus cuatro piezas construidas y verificadas: 4.1 cliente API + tipos, 4.2 `useWebSocket`/traza de agentes vía `astream` + `ws_events.py`, 4.3 `ApprovalPanel` con recuperación por REST tras reload, 4.4 métricas (cerrando de paso el hueco de `pr_comment_url` para que "PRs comentados" fuera un dato real). 142 tests en verde (desde 118), type-check limpio en frontend. Pendiente para retomar: componer una página real de Next.js que junte `AgentTrace`/`ApprovalPanel`/`MetricsPanel`.*
