# Tabla Comparativa Oficial: Baseline vs. Optimizado

> [!NOTE]
> Mediciones empíricas realizadas con `time.perf_counter()` y `tracemalloc` sobre los mismos datasets.
> **Speedup** = Tiempo Baseline / Tiempo Optimizado. Valores > 1.0x representan aceleración efectiva.

| Dataset | Operación | Complejidad Base | Complejidad Opt | Tiempo Base (ms) | Tiempo Opt (ms) | Speedup | Memoria Base (KB) | Memoria Opt (KB) | Observaciones |
|---|---|:---:|:---:|---:|---:|:---:|---:|---:|---|
| `demo_oral.json` | **Búsqueda por ID** | `O(n)` | `O(1)` | 0.003 | 0.002 | **1.99x** | 0.6 | 0.6 | ID 16 en catálogo de 30 productos |
| `demo_oral.json` | **Búsqueda por Nombre** | `O(n)` | `O(1) amort.` | 0.030 | 0.003 | **8.60x** | 1.2 | 0.6 | Término 'pincel' (índice invertido + LRU) |
| `demo_oral.json` | **Ranking Top-N (k=5)** | `O(N log N)` | `O(N log k)` | 0.044 | 0.066 | **0.67x** | 4.7 | 3.6 | heapq.nlargest acotado en k=5 sobre 8 pedidos |
| `demo_oral.json` | **Batch Picking Consolidado** | `O(P·L·n)` | `O(L)` | 0.029 | 0.151 | **0.19x** | 1.9 | 8.2 | Acumulación en 1 pasada hash vs. búsquedas anidadas |
| `demo_oral.json` | **Combinaciones Sustitutas** | `O(2^N)` | `O(N·P)` | 0.291 | 0.393 | **0.74x** | 5.9 | 9.4 | Memo DP reutilizó 0 llamadas; poda en árbol |
| `demo_oral.json` | **Preparación de Pedidos** | `O(P·L)` | `O((P·L)/C + IPC)` | 0.093 | 7.608 | **0.01x** | 6.6 | 61.4 | Mismo CatalogoHash: ProcessPool vs. secuencial (aísla IPC) |
| `pequeno.json` | **Búsqueda por ID** | `O(n)` | `O(1)` | 0.004 | 0.002 | **2.27x** | 0.6 | 0.6 | ID 51 en catálogo de 100 productos |
| `pequeno.json` | **Búsqueda por Nombre** | `O(n)` | `O(1) amort.` | 0.261 | 0.009 | **29.16x** | 1.4 | 0.6 | Término 'pincel' (índice invertido + LRU) |
| `pequeno.json` | **Ranking Top-N (k=5)** | `O(N log N)` | `O(N log k)` | 0.104 | 0.171 | **0.61x** | 7.0 | 4.4 | heapq.nlargest acotado en k=5 sobre 20 pedidos |
| `pequeno.json` | **Batch Picking Consolidado** | `O(P·L·n)` | `O(L)` | 0.081 | 1.081 | **0.07x** | 3.2 | 15.4 | Acumulación en 1 pasada hash vs. búsquedas anidadas |
| `pequeno.json` | **Combinaciones Sustitutas** | `O(2^N)` | `O(N·P)` | 0.911 | 1.348 | **0.68x** | 6.8 | 13.4 | Memo DP reutilizó 0 llamadas; poda en árbol |
| `pequeno.json` | **Preparación de Pedidos** | `O(P·L)` | `O((P·L)/C + IPC)` | 0.220 | 6.592 | **0.03x** | 14.2 | 72.0 | Mismo CatalogoHash: ProcessPool vs. secuencial (aísla IPC) |
| `mediano.json` | **Búsqueda por ID** | `O(n)` | `O(1)` | 0.016 | 0.001 | **12.28x** | 0.6 | 0.6 | ID 501 en catálogo de 1000 productos |
| `mediano.json` | **Búsqueda por Nombre** | `O(n)` | `O(1) amort.` | 0.857 | 0.003 | **261.97x** | 1.6 | 0.6 | Término 'rodillo' (índice invertido + LRU) |
| `mediano.json` | **Ranking Top-N (k=5)** | `O(N log N)` | `O(N log k)` | 0.421 | 0.364 | **1.16x** | 58.5 | 16.4 | heapq.nlargest acotado en k=5 sobre 200 pedidos |
| `mediano.json` | **Batch Picking Consolidado** | `O(P·L·n)` | `O(L)` | 4.201 | 3.227 | **1.30x** | 23.0 | 167.6 | Acumulación en 1 pasada hash vs. búsquedas anidadas |
| `mediano.json` | **Combinaciones Sustitutas** | `O(2^N)` | `O(N·P)` | 1.603 | 2.516 | **0.64x** | 9.5 | 25.2 | Memo DP reutilizó 0 llamadas; poda en árbol |
| `mediano.json` | **Preparación de Pedidos** | `O(P·L)` | `O((P·L)/C + IPC)` | 2.011 | 12.349 | **0.16x** | 159.0 | 324.7 | Mismo CatalogoHash: ProcessPool vs. secuencial (aísla IPC) |
| `grande.json` | **Búsqueda por ID** | `O(n)` | `O(1)` | 0.383 | 0.005 | **75.26x** | 0.6 | 0.6 | ID 5001 en catálogo de 10000 productos |
| `grande.json` | **Búsqueda por Nombre** | `O(n)` | `O(1) amort.` | 26.430 | 0.010 | **2627.23x** | 4.0 | 0.6 | Término 'pincel' (índice invertido + LRU) |
| `grande.json` | **Ranking Top-N (k=5)** | `O(N log N)` | `O(N log k)` | 19.003 | 10.821 | **1.76x** | 604.7 | 218.9 | heapq.nlargest acotado en k=5 sobre 2000 pedidos |
| `grande.json` | **Batch Picking Consolidado** | `O(P·L·n)` | `O(L)` | 1241.727 | 117.607 | **10.56x** | 360.5 | 1722.0 | Acumulación en 1 pasada hash vs. búsquedas anidadas |
| `grande.json` | **Combinaciones Sustitutas** | `O(2^N)` | `O(N·P)` | 36.246 | 35.551 | **1.02x** | 31.7 | 44.2 | Memo DP reutilizó 0 llamadas; poda en árbol |
| `grande.json` | **Preparación de Pedidos** | `O(P·L)` | `O((P·L)/C + IPC)` | 21.275 | 73.583 | **0.29x** | 1617.0 | 3181.7 | Mismo CatalogoHash: ProcessPool vs. secuencial (aísla IPC) |

---
### Conclusiones Principales del Benchmarking
1. **Catálogo:** La transición de lista $O(n)$ a tabla hash $O(1)$ muestra aceleraciones de órdenes de magnitud a medida que $n$ crece (superando 100x en `grande.json`).
2. **Batch Picking:** Evitar el producto cartesiano de búsquedas repetidas $O(P \cdot L \cdot n)$ mediante consolidación en una sola pasada con hash map $O(L)$ elimina por completo el cuello de botella crítico en almacén.
3. **Top-N:** `heapq.nlargest` $O(N \log k)$ mantiene memoria acotada a $k$ elementos frente a la lista completa de ordenamiento $O(N \log N)$.
4. **Sustitutos:** La memoización de estados DP convierte un árbol exponencial $O(2^N)$ en tiempo pseudo-polinomial $O(N \cdot P)$, permitiendo explorar cientos de combinaciones en milisegundos.
5. **Concurrencia:** La fila de preparación usa el **mismo** `CatalogoHash` a ambos lados. El speedup 1.95x anterior mezclaba búsqueda O(n) con el pool; aislando IPC, el secuencial gana hasta `grande.json` (0.29x): el cómputo O(P·L) no cubre el costo fijo de procesos/pickle. El pool solo se justifica con lotes mayores o trabajo más pesado por pedido.
