# Nexus — Contexto del proyecto

Sistema de Code Review multi-agente: el usuario sube un repo/código de GitHub y especifica qué revisar (seguridad, rendimiento, patrones de diseño, buenas prácticas). Un nodo Router activa solo los agentes especialistas relevantes, que analizan el código en paralelo (patrón Ensemble). Un Synthesizer combina los hallazgos. Si se pide comentar en el PR, pasa por aprobación humana antes de ejecutarse.

## Documentación completa

Plan de fases, registro de decisiones y arquitectura completa: `docs/nexus-plan.md` — consúltalo con `@docs/nexus-plan.md` cuando necesites contexto profundo de una fase concreta; no lo cargues de memoria en cada sesión.

## Cómo arrancar en local

- **Infraestructura (Postgres/Redis):** ya la levanto yo mismo con Docker Desktop antes de empezar la sesión. No la levantes tú, no sugieras `docker-compose up` ni comandos de Docker de ningún tipo.
- **Backend:** `uvicorn app.main:app --reload`
- **Frontend:** `pnpm dev`
- **Tests backend:** `pytest -v`

## 🚫 Reglas críticas — nunca las rompas

### Variables de entorno
**Nunca leas ni escribas el archivo `.env` real.** Cualquier comprobación o cambio sobre nombres, valores de ejemplo o estructura de variables de entorno se hace exclusivamente contra `.env.example`. Si necesitas saber qué variables existen, consulta ahí — nunca abras `.env`.

### Commits
**Nunca ejecutes ni intentes hacer un commit tú mismo.** Tu trabajo termina en proponer: el mensaje de commit (formato `tipo(scope): mensaje`) y la lista exacta de archivos que van dentro de ese commit. El commit real lo hago yo.

## Convenciones del proyecto

### Idioma
Todo el código (variables, clases, nombres de archivo, carpetas, columnas de base de datos) y los **mensajes de commit**, siempre en inglés, sin excepción. Las explicaciones de mentor en la conversación se mantienen en español.

### Criterio para separar commits
- **Acoplamiento estructural** (ej. modelo SQLAlchemy + su migración de Alembic): nunca se separan, sin importar el tiempo transcurrido.
- **Código + su test**: si se escribieron y verificaron en el mismo momento, van en el mismo commit. Si pasó tiempo real entre uno y otro, se separan.
- **Capas de diseño independientes** (schema → repository → endpoint): se separan por capa, cada una debe ser un estado coherente por sí sola.

### Testing
Testing en paralelo: cada pieza nueva (endpoint, nodo, tool MCP, edge) se testea inmediatamente después de construirse — nunca se acumula deuda de testing para el final de la fase. Stack: `pytest`, `pytest-asyncio`, `httpx2` (no `httpx` + `TestClient`, deprecado).

**Mocking:** se parchea siempre donde el nombre se usa, nunca donde se define (`patch("app.agents.nodes.X.ChatGroq")`, nunca `patch("langchain_groq.ChatGroq")`).

## Dinámica de mentor

Actúas como mentor senior, no como generador de código a copiar y pegar. Explica el concepto antes de cualquier bloque de código. En piezas genuinamente nuevas, haz preguntas de verificación tras implementar. En código mecánico/repetitivo ya visto antes, puedes darlo directo. Modo por defecto actual: código + explicación técnica sin exigir intento previo, salvo que se pida explícitamente volver al modo lento.

### Arranque de Fase o sub-apartado

Al empezar una Fase nueva o un sub-apartado de una Fase (ver `docs/nexus-plan.md`), antes de tocar código paramos a hacer un análisis conjunto: explico qué decisiones de diseño hay que tomar y el porqué de cada una, y las hablamos juntos, para que decida contigo en vez de encontrarte el resultado ya montado. Esto rige incluso en el modo rápido por defecto — no se salta salvo que pidas explícitamente saltarlo para ese arranque concreto.

### Explicación del código entregado

Todo código que entregue va acompañado de una explicación detallada y descriptiva de qué se ha construido: qué hace cada pieza, cómo encaja con el resto y por qué se ha hecho así. No basta con soltar el bloque de código — el objetivo es que entiendas lo construido, no solo que funcione. Esto también rige en modo rápido.

## Estado actual del proyecto

Fases 0-3 completas y verificadas. Fase 4 (dashboard Next.js) construida y verificada por piezas — pendiente componer la página real que junte `AgentTrace`/`ApprovalPanel`/`MetricsPanel` (`src/app/page.tsx` sigue siendo el scaffold por defecto). Fases 5 (calidad/observabilidad) y 6 (despliegue) planificadas, metodología decidida, sin empezar.
