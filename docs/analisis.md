# Análisis de Complejidad, Perfilado y Optimización

Este documento constituye el informe técnico fundamental del **Parcial I de Programación Eficiente (Opción 6: Optimizador de Inventario y Pedidos)**. Contiene la derivación formal de cotas asintóticas de complejidad temporal y espacial, la justificación de las estructuras de datos seleccionadas, la discusión teórica de memoización, caching y concurrencia, y el análisis exhaustivo de las mediciones empíricas recopiladas.

---

## 1. Contexto del Problema y Diagnóstico Inicial

En centros de distribución y logística masiva de *e-commerce*, los catálogos crecen de miles a cientos de miles de artículos (`SKUs`), mientras los lotes de pedidos entrantes demandan procesamiento continuo.

El diseño ingenuo (*baseline*) adolece de tres fallas arquitectónicas severas:
1. **Catálogo basado en listas:** Cualquier consulta de existencia o precio requiere un escaneo secuencial exhaustivo de la lista de productos ($O(n)$).
2. **Batch Picking anidado:** Agrupar los artículos solicitados por múltiples pedidos para los operarios de almacén genera un producto cartesiano cuadrático ($O(P \cdot L \cdot n)$), donde cada línea de cada pedido vuelve a recorrer la lista completa.
3. **Exploración combinatoria sin poda:** Para pedidos con faltante de stock, la búsqueda de combinaciones sustitutas dentro del presupuesto explora un árbol binario completo de decisión, incurriendo en tiempo exponencial ($O(2^N)$).

---

## 2. Derivación Formal de Complejidad Temporal y Espacial

A continuación se detalla la deducción matemática de las cotas asintóticas en notación Big-O para el mejor, promedio y peor caso de cada componente del sistema.

### 2.1 Búsqueda en Catálogo de Productos

Sea $n$ la cantidad total de productos en catálogo y $m$ la longitud promedio del nombre del producto.

| Operación | Versión | Mejor Caso | Caso Promedio | Peor Caso | Complejidad Espacial |
|---|---|:---:|:---:|:---:|:---:|
| **Búsqueda por ID** | Baseline (`CatalogoLineal`) | $\Omega(1)$ (primer elemento) | $\Theta(n)$ | $O(n)$ (ausente o al final) | $O(1)$ aux. |
| **Búsqueda por ID** | Optimizado (`CatalogoHash`) | $\Omega(1)$ | $\Theta(1)$ | $O(n)$ (colisión patológica) | $O(n)$ aux. |
| **Búsqueda por Nombre** | Baseline (`CatalogoLineal`) | $\Omega(n \cdot m)$ | $\Theta(n \cdot m)$ | $O(n \cdot m)$ | $O(k)$ aux. |
| **Búsqueda por Nombre** | Optimizado (`CatalogoHash`) | $\Omega(1)$ (en caché) | $\Theta(k)$ | $O(n)$ | $O(n \cdot m)$ aux. |

#### Derivación matemática:
- **Catálogo Lineal:**  
  La búsqueda secuencial evalúa la condición `producto.id == id_producto` recorriendo un array contiguo de punteros. El número de comparaciones promedio para un elemento presente es:
  $$\mathbb{E}[C] = \frac{1}{n} \sum_{i=1}^{n} i = \frac{n + 1}{2} \in \Theta(n)$$
  Si el elemento no existe, se efectúan exactamente $n$ comparaciones ($O(n)$).

- **Catálogo Hash:**  
  Utiliza la tabla hash nativa de CPython implementada mediante sondeo perturbado (*perturbed open addressing*) con factor de carga acotado ($\alpha \le \frac{2}{3}$). El costo esperado de sondeo exitoso es:
  $$\mathbb{E}[\text{sondeo}] \approx 1 + \frac{\alpha}{2(1 - \alpha)} = 1 + \frac{2/3}{2/3} = 2 \in O(1)$$
  Para la búsqueda por texto, el índice invertido descompone el catálogo en un vocabulario de palabras normalizadas; la consulta recupera el conjunto precomputado de IDs en tiempo $O(1)$ promedio, requiriendo únicamente $O(k)$ para instanciar la lista de resultados (donde $k$ es el número de coincidencias, $k \ll n$).

---

### 2.2 Ranking de Productos Más Solicitados (Top-N)

Sea $N$ la cantidad de productos con demanda acumulada positiva ($N \le n$) y $k$ la cantidad de artículos a exhibir en el ranking ($k \ll N$).

| Versión | Algoritmo | Tiempo Mejor Caso | Tiempo Promedio | Tiempo Peor Caso | Espacio Auxiliar |
|---|---|:---:|:---:|:---:|:---:|
| **Baseline** | Timsort global (`sorted()`) | $\Omega(N)$ | $\Theta(N \log N)$ | $O(N \log N)$ | $O(N)$ |
| **Optimizado** | Min-Heap (`heapq.nlargest`) | $\Omega(N)$ | $\Theta(N \log k)$ | $O(N \log k)$ | $O(k)$ |

#### Derivación matemática:
- **Baseline (Timsort):**  
  Construye una lista completa de $N$ pares `(producto, demanda)` y aplica Timsort. La relación de recurrencia de división y fusión genera:
  $$T(N) = 2\,T(N/2) + \Theta(N) \implies T(N) \in \Theta(N \log N)$$
  Requiere además $O(N)$ espacio auxiliar para retener la lista intermedia antes de extraer los $k$ primeros elementos.

- **Optimizado (Min-Heap de tamaño fijo $k$):**  
  1. Se construye un min-heap inicial con los primeros $k$ elementos en tiempo $O(k)$.
  2. Para los restantes $(N - k)$ elementos, cada elemento se compara con la raíz del heap (el mínimo de los top-k actuales).
  3. Si es mayor, se reemplaza la raíz mediante `heapreplace`, lo que toma a lo sumo $\lfloor \log_2 k \rfloor$ comparaciones de rebalanceo (sift-down).
  
  Costo temporal total:
  $$T(N, k) = O(k) + (N - k) \cdot O(\log k) = O(N \log k)$$
  
  Cuando $k$ es pequeño y constante (por ejemplo $k = 5$ o $k = 10$), $\log k$ es una constante insignificante ($\log_2 5 \approx 2.32$), por lo que:
  $$T(N, k) \in O(N)$$
  El ahorro espacial es crítico: solo se retienen $k$ referencias en memoria heap en lugar de los $N$ registros completos.

---

### 2.3 Agrupación de Pedidos para Batch Picking Consolidado

Sea $P$ el número total de pedidos en el lote y $L$ el número promedio de líneas por pedido. El número total de líneas a consolidar es $|L_{\text{total}}| = P \cdot L$.

| Versión | Algoritmo | Complejidad Temporal | Complejidad Espacial |
|---|---|:---:|:---:|
| **Baseline** | Recorrido anidado con búsqueda lineal | $O(P \cdot L \cdot n)$ | $O(U)$ |
| **Optimizado** | Consolidación en 1 pasada con acumulador Hash | $O(P \cdot L) = O(|L_{\text{total}}|)$ | $O(U)$ |

#### Derivación matemática:
- **Baseline:** Por cada uno de los $P$ pedidos y por cada una de sus $L$ líneas, se invoca `catalogo_lineal.buscar_por_id()`, que efectúa en promedio $n/2$ operaciones:
  $$T_{\text{base}} = \sum_{p=1}^{P} \sum_{l=1}^{L} \Theta(n) = \Theta(P \cdot L \cdot n)$$
  Para un escenario mediano ($P = 200, L = 5, n = 1.000$), se realizan del orden de $1.000.000$ de operaciones.

- **Optimizado:**  
  En una única pasada lineal sobre las líneas de pedidos, se agrega la demanda acumulada en un diccionario hash indexado por `id_producto` ($O(1)$ por inserción/acumulación). Finalizada la pasada, se resuelve el producto desde `CatalogoHash` en $O(1)$ por producto único $U$ ($U \le n$):
  $$T_{\text{opt}} = O(P \cdot L) + O(U) \in O(P \cdot L)$$
  La complejidad se desacopla completamente del tamaño del catálogo $n$.

---

### 2.4 Búsqueda de Alternativas y Combinaciones Sustitutas

Sea $N$ el número de productos candidatos en la misma categoría del artículo agotado y $P$ el presupuesto máximo disponible expresado en centavos enteros ($P \in \mathbb{N}$).

| Versión | Algoritmo | Complejidad Temporal | Complejidad Espacial |
|---|---|:---:|:---:|
| **Baseline** | Árbol recursivo exhaustivo | $O(2^N)$ | $O(N)$ (pila de llamadas) |
| **Optimizado** | Programación Dinámica con Memoización | $O(N \cdot P)$ | $O(N \cdot P)$ (tabla de memoización) |

#### Derivación matemática:
- **Baseline (Fuerza bruta recursiva):**  
  Cada producto candidato $i \in \{1, \dots, N\}$ presenta una decisión binaria: incluirlo o excluirlo de la combinación. El árbol de recurrencia tiene profundidad $N$ y un total de nodos dado por:
  $$\sum_{i=0}^{N} \binom{N}{i} = 2^N$$
  Para $N = 30$, $2^{30} \approx 1.07 \times 10^9$ llamadas, lo cual es inabordable en tiempo real.

- **Optimizado (Programación Dinámica Top-Down con Memoización):**  
  El subproblema queda unívocamente definido por la tupla de estado:
  $$\text{Estado} = (i, p)$$
  donde $i \in [0, N]$ es el índice del candidato bajo evaluación y $p \in [0, P]$ es el presupuesto restante.
  
  El espacio de estados discretos es a lo sumo:
  $$|\mathcal{S}| = (N + 1) \times (P + 1) \in O(N \cdot P)$$
  Al memoizar los resultados de cada estado en una tabla hash, ningún estado $(i, p)$ se evalúa más de una vez. La transición de cada estado realiza trabajo $O(1)$ (combinar las listas de combinaciones retornadas acotadas a un límite superior $M$).
  Por tanto:
  $$T(N, P) \in O(N \cdot P)$$
  Esto transforma un problema de complejidad exponencial en uno de tiempo **pseudo-polinomial**.

---

### 2.5 Preparación y Validación de Pedidos

| Versión | Modelo de Ejecución | Complejidad Temporal | Complejidad Espacial |
|---|---|:---:|:---:|
| **Secuencial** | Mono-hilo en hilo principal | $O(P \cdot L)$ | $O(P \cdot L)$ |
| **Concurrente** | Multi-proceso (`ProcessPoolExecutor`) | $O\left(\frac{P \cdot L}{C}\right) + O(C_{\text{IPC}})$ | $O(P \cdot L + C \cdot \text{chunk})$ |

donde $C$ es la cantidad de núcleos CPU disponibles y $C_{\text{IPC}}$ es el costo de serialización/deserialización (Pickling) entre procesos.

---

## 3. Justificación de Algoritmos y Estructuras de Datos

### 3.1 Tabla Hash con Índices Invertidos (`CatalogoHash`)
- **Por qué no listas:** Una lista requiere un recorrido de punteros secuencial en memoria heap; a medida que el catálogo crece de $1.000$ a $10.000$ artículos, la latencia de búsqueda pasa de milisegundos a décimas de segundo, multiplicada por cada línea de pedido.
- **Por qué índices invertidos:** Para las búsquedas parciales de texto, buscar subcadenas con `in` sobre la lista completa cuesta $O(n \cdot m)$. El índice invertido indexa palabras normalizadas (minúsculas, sin acentos), mapeando cada término directamente a un `set[int]` de IDs en $O(1)$.

### 3.2 Min-Heap para Top-N (`heapq.nlargest`)
- **Por qué no `sorted()`:** Ordenar todo el catálogo para mostrar únicamente los 5 productos más demandados realiza trabajo innecesario sobre el 99.9% de los productos restantes. Timsort reordena la lista completa en $O(N \log N)$; `heapq.nlargest` filtra dinámicamente conservando un heap invertido de $k$ elementos con costo $O(N \log k)$ y huella de memoria minúscula.

### 3.3 Programación Dinámica para Combinaciones Sustitutas
- **Por qué no recursión pura:** Los árboles de decisión combinatoria reevalúan los mismos estados de saldo restante decenas de miles de veces en diferentes ramas. La memoización almacena la tupla `(indice, presupuesto_restante)` cortando inmediatamente la exploración de ramas redundantes.

---

## 4. Memoización vs. Caching

Una de las distinciones fundamentales evaluadas en la materia radica en no confundir la **memoización algorítmica** con el **caching de consultas**:

| Dimensión | Memoización (Programación Dinámica) | Caching de Consultas (GestorCacheConsultas) |
|---|---|---|
| **Ámbito** | Interno al algoritmo de optimización (`BuscadorAlternativas`). | Periférico a las llamadas del usuario y la UI (`MotorInventario`). |
| **Determinismo** | Estrictamente determinista: para una entrada $(i, p)$, la salida es matemática e invariante. | Dependiente del estado del inventario; puede quedar obsoleto si el stock muta. |
| **Ciclo de vida** | Efímero (se crea para una ejecución o se preserva mientras el catálogo no cambie). | Persistente entre múltiples pantallas y acciones del usuario. |
| **Política de desalojo** | Sin desalojo durante la corrida del subproblema (almacena el grafo de estados completo). | Política estricta **LRU (Least Recently Used)** con capacidad máxima fija $O(C)$. |
| **Protocolo de invalidación** | No requiere invalidación durante la llamada recursiva. | **Invalidación reactiva:** ante una mutación de stock o nuevo lote de pedidos, se purgan selectivamente las claves afectadas. |

### Demostración del Protocolo de Invalidación Reactiva
Cuando un pedido se procesa con descuento de inventario:
1. Se muta el atributo `stock` del producto.
2. `MotorInventario` invoca automáticamente:
   - `_cache.invalidar_por_mutacion_stock()`: limpia las búsquedas de texto y filtros por categoría, asegurando que ninguna pantalla devuelva productos con existencias obsoletas.
   - `_cache.invalidar_por_nuevos_pedidos()`: purga el Top-N previamente calculado.

---

## 5. Concurrencia y Paralelismo: El GIL y el Overhead de IPC

### El Global Interpreter Lock (GIL) de CPython
En Python, el GIL es un mecanismo de sincronización que restringe la ejecución de bytecode a un único hilo nativo por proceso. En tareas intensivas de cómputo (CPU-bound) como la validación masiva de cientos de pedidos con múltiples líneas de inventario:
- `threading` o `ThreadPoolExecutor` **no logran aceleración real**: los hilos compiten por el GIL, alternando ejecución y generando sobrecosto por cambios de contexto (*context switching*).
- La solución requerida es **multi-procesamiento** (`ProcessPoolExecutor`), que genera procesos independientes del sistema operativo, cada uno con su propio intérprete de Python, su propio espacio de memoria y su propio GIL.

### Análisis del Punto de Inflexión (*Break-Even Point*) y Overhead de IPC
El multi-procesamiento introduce un costo fijo no despreciable:
1. **Creación de procesos:** `_winapi.CreateProcess` en Windows.
2. **Serialización IPC (Pickling):** La serialización binaria de lotes de pedidos y su envío por tuberías o colas inter-proceso.
3. **Sincronización:** `_winapi.WaitForSingleObject`.

#### Evidencia empírica obtenida en benchmarking:
- **`demo_oral.json` (8 pedidos):**  
  - Mono-hilo: **0.17 ms**
  - Concurrente: **396.76 ms** (Speedup **0.00x**)
  - *Diagnóstico:* El costo de instanciar procesos en Windows y serializar los datos supera ampliamente el tiempo de cómputo de 8 pedidos.
- **`grande.json` (2.000 pedidos, 10.000 productos):**  
  - Mono-hilo: **1.417,17 ms**
  - Concurrente: **727,48 ms** (Speedup **1.95x**)
  - *Diagnóstico:* Con 2.000 pedidos, la carga computacional supera con creces el costo fijo de IPC, logrando una aceleración real de casi **2x** en una máquina multi-núcleo.

---

## 6. Evidencia Empírica: Tabla Comparativa Oficial

Las siguientes mediciones fueron registradas automáticamente mediante `time.perf_counter()` y `tracemalloc` ejecutando `python -m benchmarks.comparar` sobre los datasets oficiales:

| Dataset | Operación | Complejidad Base | Complejidad Opt | Tiempo Base (ms) | Tiempo Opt (ms) | Speedup | Memoria Base (KB) | Memoria Opt (KB) | Observaciones |
|---|---|:---:|:---:|---:|---:|:---:|---:|---:|---|
| `demo_oral.json` | **Búsqueda por ID** | `O(n)` | `O(1)` | 0.003 | 0.002 | **1.99x** | 0.6 | 0.6 | ID 16 en catálogo de 30 productos |
| `demo_oral.json` | **Búsqueda por Nombre** | `O(n)` | `O(1) amort.` | 0.030 | 0.003 | **8.60x** | 1.2 | 0.6 | Término 'pincel' (índice invertido + LRU) |
| `demo_oral.json` | **Ranking Top-N (k=5)** | `O(N log N)` | `O(N log k)` | 0.044 | 0.066 | **0.67x** | 4.7 | 3.6 | heapq.nlargest acotado en k=5 sobre 8 pedidos |
| `demo_oral.json` | **Batch Picking Consolidado** | `O(P·L·n)` | `O(L)` | 0.029 | 0.151 | **0.19x** | 1.9 | 8.2 | Acumulación en 1 pasada hash vs. búsquedas anidadas |
| `demo_oral.json` | **Combinaciones Sustitutas** | `O(2^N)` | `O(N·P)` | 0.291 | 0.393 | **0.74x** | 5.9 | 9.4 | Poda en árbol combinatorio |
| `demo_oral.json` | **Preparación de Pedidos** | `O(P·L·n)` | `O(P·L/cores)` | 0.169 | 396.764 | **0.00x** | 6.8 | 213.3 | Dominancia de IPC en volumen pequeño |
| `pequeno.json` | **Búsqueda por ID** | `O(n)` | `O(1)` | 0.004 | 0.002 | **2.27x** | 0.6 | 0.6 | ID 51 en catálogo de 100 productos |
| `pequeno.json` | **Búsqueda por Nombre** | `O(n)` | `O(1) amort.` | 0.261 | 0.009 | **29.16x** | 1.4 | 0.6 | Índice invertido + LRU |
| `pequeno.json` | **Ranking Top-N (k=5)** | `O(N log N)` | `O(N log k)` | 0.104 | 0.171 | **0.61x** | 7.0 | 4.4 | 20 pedidos |
| `pequeno.json` | **Batch Picking Consolidado** | `O(P·L·n)` | `O(L)` | 0.081 | 1.081 | **0.07x** | 3.2 | 15.4 | Hash map consolidado |
| `pequeno.json` | **Combinaciones Sustitutas** | `O(2^N)` | `O(N·P)` | 0.911 | 1.348 | **0.68x** | 6.8 | 13.4 | DP memoizada |
| `pequeno.json` | **Preparación de Pedidos** | `O(P·L·n)` | `O(P·L/cores)` | 0.911 | 367.719 | **0.00x** | 14.4 | 226.8 | IPC overhead |
| `mediano.json` | **Búsqueda por ID** | `O(n)` | `O(1)` | 0.016 | 0.001 | **12.28x** | 0.6 | 0.6 | ID 501 en catálogo de 1000 productos |
| `mediano.json` | **Búsqueda por Nombre** | `O(n)` | `O(1) amort.` | 0.857 | 0.003 | **261.97x** | 1.6 | 0.6 | 261x más rápido con caché |
| `mediano.json` | **Ranking Top-N (k=5)** | `O(N log N)` | `O(N log k)` | 0.421 | 0.364 | **1.16x** | 58.5 | 16.4 | Ahorro sustancial de memoria |
| `mediano.json` | **Batch Picking Consolidado** | `O(P·L·n)` | `O(L)` | 4.201 | 3.227 | **1.30x** | 23.0 | 167.6 | Inicio de ventaja de consolidación |
| `mediano.json` | **Combinaciones Sustitutas** | `O(2^N)` | `O(N·P)` | 1.603 | 2.516 | **0.64x** | 9.5 | 25.2 | Poda en árbol combinatorio |
| `mediano.json` | **Preparación de Pedidos** | `O(P·L·n)` | `O(P·L/cores)` | 7.625 | 641.920 | **0.01x** | 159.2 | 380.1 | Break-even aún no alcanzado |
| `grande.json` | **Búsqueda por ID** | `O(n)` | `O(1)` | 0.383 | 0.005 | **75.26x** | 0.6 | 0.6 | ID 5001 en 10.000 productos |
| `grande.json` | **Búsqueda por Nombre** | `O(n)` | `O(1) amort.` | 26.430 | 0.010 | **2627.23x** | 4.0 | 0.6 | **2627x de aceleración** con hash invertido |
| `grande.json` | **Ranking Top-N (k=5)** | `O(N log N)` | `O(N log k)` | 19.003 | 10.821 | **1.76x** | 604.7 | 218.9 | **63% de ahorro de memoria** en heap |
| `grande.json` | **Batch Picking Consolidado** | `O(P·L·n)` | `O(L)` | 1241.727 | 117.607 | **10.56x** | 360.5 | 1722.0 | **10.5x más rápido** evitando recorridos |
| `grande.json` | **Combinaciones Sustitutas** | `O(2^N)` | `O(N·P)` | 36.246 | 35.551 | **1.02x** | 31.7 | 44.2 | Evita explosión combinatorial |
| `grande.json` | **Preparación de Pedidos** | `O(P·L·n)` | `O(P·L/cores)` | 1417.171 | 727.486 | **1.95x** | 1617.1 | 2764.9 | **Punto de corte alcanzado: ~2x más rápido** |

---

## 7. Diagnóstico de Hotspots con Evidencia de Profiling

### 7.1 Evidencia de `cProfile`
El informe en `docs/mediciones/cprofile_resumen.txt` demuestra que en la ejecución optimizada:
- El cuello de botella en tiempo propio (`tottime`) en datasets grandes se desplaza a las llamadas de sistema de Windows para crear y coordinar procesos:
  - `{built-in method _winapi.CreateProcess}` (0.364 s acumulado).
  - `{built-in method _winapi.WaitForSingleObject}` (0.354 s acumulado).
- Esto valida teóricamente la hipótesis de que las operaciones de dominio de Python ($O(1)$) se volvieron tan rápidas que la mayor latencia restante proviene del sistema operativo.

### 7.2 Evidencia de `line_profiler`
El informe en `docs/mediciones/line_profiler_resumen.txt` expone el comportamiento instrucción a instrucción:
- En `CatalogoLineal.buscar_por_id`:
  - Se registraron **197.850 iteraciones (Hits)** en el bucle `for producto in self._productos:`, consumiendo el **99.7% del tiempo total** de la función.
- En `CatalogoHash.buscar_por_id`:
  - La línea `return self._productos_por_id.get(id_producto)` insume únicamente **5.0 microsegundos por ejecución (Per Hit)** de manera constante.

### 7.3 Evidencia de `memory_profiler` y `tracemalloc`
El informe en `docs/mediciones/memoria_resumen.txt` certifica los trade-offs espaciales:
- En `grande.json`:
  - `CatalogoLineal`: 83.59 KB.
  - `CatalogoHash`: 5.339,00 KB (~5.2 MB) debido a la redundancia calculada para los índices de categoría y de palabras.
  - **Min-Heap vs Sort:** `sorted` requirió un pico de **603.25 KB**, mientras que `heapq.nlargest` requirió únicamente **216.20 KB**, logrando un **ahorro de 387.05 KB** en memoria activa.
  - **Caché LRU:** Permanece acotada en **~10.27 KB** y se reduce a **1.13 KB** tras la invalidación reactiva.

---

## 8. Guía de Respuestas para la Defensa Oral (10-15 min)

1. **¿Dónde estaba el cuello de botella original?**  
   En la búsqueda lineal en catálogo repetida en cada pedido y en la consolidación de batch picking, que generaban una complejidad algorítmica cuadrática $O(P \cdot L \cdot n)$, colapsando el sistema ante $10.000$ productos.
2. **¿Qué optimización generó el mayor impacto marginal?**  
   El reemplazo de la lista de productos por la tabla hash con índice invertido y caché LRU, logrando un **speedup de hasta 2.627x** en búsquedas textuales.
3. **¿La solución escala si el catálogo crece 10x (100.000 productos)?**  
   Sí: la búsqueda hash permanece en $O(1)$, el batch picking en $O(L)$, y el Top-N en $O(N \log k)$. La única limitación es el consumo de memoria del índice invertido, que escalaría de 5 MB a ~50 MB, perfectamente manejable en RAM moderna.
4. **¿Qué trade-offs se asumieron y qué se haría diferente?**  
   Se asumió un trade-off clásico de **tiempo por memoria**: se invirtieron ~5 MB adicionales en índices hash para eliminar los bucles $O(n)$. Para futuras iteraciones, en datasets masivos se reemplazaría la serialización de procesos de `ProcessPoolExecutor` por memoria compartida (`multiprocessing.shared_memory`) para erradicar el overhead de IPC.
