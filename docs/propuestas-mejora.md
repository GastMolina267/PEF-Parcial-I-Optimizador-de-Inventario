# Propuestas de mejora (Automatización Origin 2)

<!-- Bloque generado por la automatización de hotspots. -->
<!-- No aplicar estos cambios de forma automática: el grupo decide y vuelve a medir. -->

**Commit analizado:** `f794246` · **Generado:** 2026-09-03 00:07 UTC

## Fuentes consultadas

- `docs/mediciones/cprofile_resumen.txt`
- `docs/mediciones/line_profiler_resumen.txt`
- `docs/mediciones/memoria_resumen.txt`
- `docs/mediciones/tabla_comparativa.md`
- `docs/mediciones/tabla_comparativa.txt`

## Hotspots detectados

| Origen | Símbolo | Métrica | Valor | Detalle |
|---|---|---|---:|---|
| cProfile | `{built-in method _winapi.CreateProcess}` | tottime_s | 0.364 | cumtime=0.364s (runtime / IPC) |
| cProfile | `{built-in method _winapi.WaitForSingleObject}` | tottime_s | 0.354 | cumtime=0.354s (runtime / IPC) |
| cProfile | `{built-in method _winapi.CreateProcess}` | tottime_s | 0.167 | cumtime=0.167s (runtime / IPC) |
| cProfile | `{built-in method _winapi.WaitForSingleObject}` | tottime_s | 0.161 | cumtime=0.161s (runtime / IPC) |
| cProfile | `C:/Users/edgar/OneDrive/Escritorio/UBP/PEF/Parcial I/src/inventario/catalogo_hash.py:31(_indexar_nombre)` | tottime_s | 0.041 | cumtime=0.105s |
| cProfile | `{method 'dump' of '_pickle.Pickler' objects}` | tottime_s | 0.035 | cumtime=0.038s (runtime / IPC) |
| cProfile | `C:/Users/edgar/OneDrive/Escritorio/UBP/PEF/Parcial I/src/modelos/producto.py:26(__post_init__)` | tottime_s | 0.028 | cumtime=0.042s |
| cProfile | `C:/Users/edgar/OneDrive/Escritorio/UBP/PEF/Parcial I/src/pedidos/agrupador.py:70(agrupar_pedidos_batch)` | tottime_s | 0.02 | cumtime=0.030s |
| cProfile | `C:/Users/edgar/OneDrive/Escritorio/UBP/PEF/Parcial I/src/modelos/producto.py:53(desde_diccionario)` | tottime_s | 0.019 | cumtime=0.064s |
| cProfile | `C:/Users/edgar/OneDrive/Escritorio/UBP/PEF/Parcial I/src/inventario/catalogo_hash.py:48(agregar)` | tottime_s | 0.017 | cumtime=0.129s |
| cProfile | `C:/Users/edgar/OneDrive/Escritorio/UBP/PEF/Parcial I/src/datos/cargador.py:11(validar_dataset)` | tottime_s | 0.015 | cumtime=0.106s |
| cProfile | `{built-in method _pickle.loads}` | tottime_s | 0.012 | cumtime=0.012s (runtime / IPC) |
| line_profiler | `CatalogoHash.buscar_por_id:74` | pct_tiempo | 100.0 | return self._productos_por_id.get(id_producto) |
| line_profiler | `procesar_pedidos_secuencial:52` | pct_tiempo | 90.8 | producto = catalogo.buscar_por_id(linea.id_producto) |
| line_profiler | `CatalogoLineal.buscar_por_nombre:57` | pct_tiempo | 62.6 | if texto_norm in producto.nombre.lower(): |
| line_profiler | `CatalogoLineal.buscar_por_id:45` | pct_tiempo | 50.4 | if producto.id == id_producto: |
| line_profiler | `CatalogoLineal.buscar_por_id:44` | pct_tiempo | 49.3 | for producto in self._productos: |
| line_profiler | `calcular_top_solicitados_heap:87` | pct_tiempo | 43.1 | top_k_items = heapq.nlargest( |
| line_profiler | `CatalogoLineal.buscar_por_nombre:56` | pct_tiempo | 36.5 | for producto in self._productos: |
| line_profiler | `calcular_top_solicitados_lineal:51` | pct_tiempo | 31.8 | prod = catalogo.buscar_por_id(id_prod) |

## Propuestas (no aplicadas)

### 1. Reducir el overhead de IPC del pool de procesos

- **Prioridad:** alta
- **Hotspot:** `_winapi.CreateProcess` / `WaitForSingleObject` / `pickle.dumps` dominan tottime en cProfile (mediano y grande).
- **Evidencia:** docs/mediciones/cprofile_resumen.txt — tottime de CreateProcess 0.364 s (mediano) y 0.167 s (grande); pickle.dumps aparece en el top.
- **Alternativa:** 1) Umbral de break-even: si P < ~200 pedidos, forzar el procesador secuencial. 2) Reusar un pool persistente en vez de abrir/cerrar `ProcessPoolExecutor` por corrida. 3) Sustituir el pickle del snapshot por `multiprocessing.shared_memory` o un array de enteros (id → stock) para no serializar objetos `Pedido`.
- **Trade-off (tiempo / memoria / claridad):** Menos latencia de arranque a costa de más complejidad y, en shared_memory, de perder la API de objetos. Medir de nuevo con py-spy sobre el pool.
- **¿Ya cubierta por el motor actual?** No — queda a decisión del grupo

### 2. No usar el catálogo lineal fuera del desafío experimental

- **Prioridad:** media
- **Hotspot:** `CatalogoLineal.buscar_por_id`: el `for` sobre `self._productos` concentra ~99.7 % del tiempo de la función (line_profiler, 197 850 hits).
- **Evidencia:** docs/mediciones/line_profiler_resumen.txt
- **Alternativa:** En producción/demo dejar `estrategia='optimizado'`. Conservar el lineal solo como baseline medible. Si se necesita un modo mixto, cachear el último `buscar_por_id` con el LRU ya existente.
- **Trade-off (tiempo / memoria / claridad):** El baseline debe seguir existiendo para la rúbrica; no borrarlo. La caché no cambia la cota O(n) de la primera consulta.
- **¿Ya cubierta por el motor actual?** Sí — ya existe baseline vs optimizado

### 3. No pagar concurrencia ni heap en escalas donde no ganan

- **Prioridad:** alta
- **Hotspot:** Speedup < 1× en: demo_oral.json / **Ranking Top-N (k=5)**, demo_oral.json / **Batch Picking Consolidado**, demo_oral.json / **Combinaciones Sustitutas**, demo_oral.json / **Preparación de Pedidos**
- **Evidencia:** docs/mediciones/tabla_comparativa.md — demo_oral y pequeno muestran ProcessPool ~400 ms vs <1 ms secuencial; top-N heap a veces pierde por la constante de `heapq` cuando N es chico.
- **Alternativa:** Selector automático de estrategia: heap solo si N > 50 o k/N < 0.1; pool de procesos solo si P · L supera un umbral medido. Documentar el umbral en la oral.
- **Trade-off (tiempo / memoria / claridad):** Más ramas de código frente a una regla simple (optimizado siempre). La claridad de la demo oral puede sufrir si el selector oculta el contraste.
- **¿Ya cubierta por el motor actual?** No — queda a decisión del grupo

### 4. Compactar el índice invertido en catálogos masivos

- **Prioridad:** baja
- **Hotspot:** Catálogo hash en grande.json: pico ~5 MB frente a ~84 KB del lineal.
- **Evidencia:** docs/mediciones/memoria_resumen.txt y columna Memoria Opt de la tabla.
- **Alternativa:** Almacenar posting lists como arrays de ids (`array('I')`) en lugar de `set[int]`; o un trie/prefijo si las búsquedas son por comienzo de palabra. Para 100k SKUs evaluar un índice en disco (SQLite FTS) en vez de RAM.
- **Trade-off (tiempo / memoria / claridad):** Menos memoria y peor latencia de mutación (alta/baja de productos). El trade-off actual (tiempo por memoria) ya está justificado para 10k productos.
- **¿Ya cubierta por el motor actual?** No — queda a decisión del grupo

### 5. Evitar el sort final del lote de picking si la UI no lo requiere

- **Prioridad:** baja
- **Hotspot:** `agrupar_pedidos_batch` aparece en tottime de cProfile (grande: 0.020 s).
- **Evidencia:** docs/mediciones/cprofile_resumen.txt — src/pedidos/agrupador.py:70
- **Alternativa:** La consolidación hash ya es O(L). El `sorted(..., reverse=True)` añade O(U log U) solo para presentación. Diferir el orden a la pantalla o usar `heapq.nlargest` si solo se muestran los U′ más demandados.
- **Trade-off (tiempo / memoria / claridad):** La tabla de agrupación dejaría de venir preordenada. Impacto menor frente a la búsqueda lineal, pero es trabajo evitable.
- **¿Ya cubierta por el motor actual?** No — queda a decisión del grupo

## Qué no hace esta automatización

- No modifica `src/`, `benchmarks/` ni tests.
- No abre un PR de código: solo actualiza este informe.
- No sustituye la tabla obligatoria ni los profilers del grupo.
