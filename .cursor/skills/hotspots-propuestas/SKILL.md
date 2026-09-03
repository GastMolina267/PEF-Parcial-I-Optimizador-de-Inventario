---
name: hotspots-propuestas
description: Automatización Origin 2 — lee docs/mediciones/, identifica hotspots y actualiza docs/propuestas-mejora.md sin aplicar cambios de código.
---

# Hotspots y propuestas de mejora (Origin)

Ejecutá esta skill cuando el disparador sea un **push** o una **PR** de este repositorio.

## Qué hacer

1. Priorizá artefactos en `docs/mediciones/` si existen en el commit: `cprofile_resumen.txt`, `line_profiler_resumen.txt`, `memoria_resumen.txt`, `tabla_comparativa.md`, Scalene, py-spy.
2. Correr el núcleo reproducible:

   ```bash
   python -m automations.ejecutar --propuestas
   ```

   El script extrae tottime / % Time / speedup < 1× y escribe `docs/propuestas-mejora.md` versionado por commit.
3. Si **no** hay informes, no inventes milisegundos: usá análisis estático (bucles anidados, búsquedas lineales, GIL, copias entre procesos) y pedí que el grupo regenere mediciones.
4. Cada propuesta debe incluir: hotspot, evidencia (ruta + símbolo), alternativa, trade-off (tiempo vs memoria vs claridad) y si ya está cubierta por baseline vs optimizado.
5. Idioma de toda salida: **español**.

## Qué no hacer

- **No apliques** las optimizaciones. Solo proponé.
- No modifiques `src/`, `benchmarks/` ni tests.
- No borres informes crudos de `docs/mediciones/`.
- No commitees sobre la rama que disparó el trigger. PR nuevo solo con el informe, o comentario en la PR con el top de hotspots.

## Comentario de PR (si el trigger es una PR)

Top 3 hotspots + 1 línea de alternativa cada uno. Dejá el detalle en `docs/propuestas-mejora.md`.
