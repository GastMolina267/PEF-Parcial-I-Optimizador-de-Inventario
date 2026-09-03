---
name: analisis-complejidad
description: Automatización Origin 1 — deriva complejidad temporal de las funciones fundamentales del motor y refresca docs/analisis.md en cada push.
---

# Análisis de complejidad temporal (Origin)

Ejecutá esta skill cuando el disparador sea un **push** o una **PR** de este repositorio.

## Qué hacer

1. Clonar / usar el commit que disparó el trigger.
2. Recorrer **solo** funciones fundamentales del motor (inventario, pedidos, ranking, caché). Inventario canónico: `automations/inventario_funciones.py`.
3. Correr el núcleo reproducible:

   ```bash
   python -m automations.ejecutar --complejidad
   ```

   El script recorre el AST, deriva mejor/promedio/peor con evidencia del cuerpo y reemplaza el bloque entre `<!-- ORIGIN-AUTO-COMPLEJIDAD:INICIO -->` y `<!-- ORIGIN-AUTO-COMPLEJIDAD:FIN -->` en `docs/analisis.md`.
4. Revisá que cada cota cite constructos reales (bucles, `dict.get`, `heapq.nlargest`, recursión, `_memo_cache`, `ProcessPoolExecutor`). Si el script omitió una función nueva del motor, agregala al inventario y re-ejecutá. **No inventes Big-O** sin abrir el cuerpo.
5. Idioma de toda salida: **español**.

## Qué no hacer

- No reescribas lógica de negocio en `src/`.
- No toques UI Flet, tests ni datasets.
- No borres las secciones 1–8 de `docs/analisis.md` (comentario del grupo).
- No commitees sobre la rama que disparó el trigger (evita bucles). Si hay cambios, abrí un PR nuevo `cursor/…` solo con docs, o comentá el resumen en la PR existente.

## Criterio de “fundamental”

Operaciones del enunciado y del motor/benchmarks: búsqueda, agrupación, top-N, combinaciones, procesamiento de pedidos, caché/memo. Ignorar wrappers de Flet, handlers y tests.

## Comentario de PR (si el trigger es una PR)

Resumen breve: funciones tocadas, cotas que cambiaron, SHA analizado. No pegues el Markdown completo.
