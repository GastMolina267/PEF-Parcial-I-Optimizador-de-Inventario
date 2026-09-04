/**
 * ==========================================================================
 * APLICACIÓN DE PRESENTACIÓN INTERACTIVA
 * Programación Eficiente — Primer Parcial (Opción 6) | Universidad Blas Pascal
 * ==========================================================================
 */

(function () {
  'use strict';

  // Fallback de datos embebido para ejecución directa con doble clic (file://)
  const FALLBACK_SLIDES = [
    {
      id: 1,
      tag: "01. PORTADA",
      title: "Optimizador de Inventario y Pedidos",
      subtitle: "Demostración de Técnicas Avanzadas de Rendimiento y Análisis Algorítmico",
      content_html: "<div class='cover-grid'><div class='cover-card highlight'><h3>Primer Parcial — Programación Eficiente</h3><p class='lead'>Opción 6: Gestión inteligente de inventario, picking consolidado y optimización combinatoria ante catálogos masivos.</p><div class='badge-row'><span class='badge primary'>Python 3.10+</span><span class='badge success'>Flet UI (Flutter Engine)</span><span class='badge warning'>Dualidad Baseline vs. Optimizado</span></div></div><div class='cover-card'><h4>Ejes Fundamentales de Evaluación</h4><ul class='checklist'><li><strong>Complejidad Big-O:</strong> Derivación formal analítica y empírica.</li><li><strong>Estructuras de Datos:</strong> Listas, Tablas Hash, Min-Heaps y Sets.</li><li><strong>Memoización vs. Caching:</strong> Diferenciación conceptual y coherencia reactiva.</li><li><strong>Concurrencia:</strong> ProcessPoolExecutor, evasión del GIL y Ley de Amdahl.</li><li><strong>Perfilado Integral:</strong> cProfile, line_profiler, tracemalloc y Scalene.</li></ul></div></div>",
      notes: "Introducir al equipo, presentar la materia y aclarar que el proyecto no es un simple CRUD, sino una plataforma experimental diseñada para medir y justificar cada decisión algorítmica."
    },
    {
      id: 2,
      tag: "02. EL PROBLEMA",
      title: "El Problema Logístico y el Reto de Escala",
      subtitle: "¿Qué problema resolvimos y por qué es crítico para el rendimiento de software?",
      content_html: "<div class='two-col'><div class='panel'><h3>Contexto Operativo</h3><p>En centros de distribución modernos (e-commerce y retail), la preparación de pedidos (<em>order picking</em>) representa hasta el <strong>55% de los costos operativos</strong> del almacén.</p><p>A medida que el catálogo escala a <strong>10.000 artículos</strong> y se reciben <strong>2.000 pedidos concurrentes</strong>, los algoritmos ingenuos colapsan:</p><ul class='bullet-list'><li>Búsquedas lineales $O(n)$ saturan la CPU en consultas recurrentes.</li><li>Verificación de pedidos $O(P \\cdot L \\cdot n)$ tarda minutos en responder.</li><li>Búsqueda combinatoria exhaustiva $O(2^N)$ sufre explosión exponencial.</li><li>Operarios recorren kilómetros innecesarios sin consolidación de demanda.</li></ul></div><div class='panel highlight'><h3>Objetivo de Ingeniería</h3><p>Construir un motor desacoplado de alto rendimiento capaz de:</p><div class='kpi-mini-grid'><div class='kpi-box'><span class='num'>O(1)</span><span class='lbl'>Búsquedas Hash</span></div><div class='kpi-box'><span class='num'>O(L)</span><span class='lbl'>Batch Picking</span></div><div class='kpi-box'><span class='num'>O(N log k)</span><span class='lbl'>Ranking Top-N</span></div><div class='kpi-box'><span class='num'>O(N·P)</span><span class='lbl'>DP Memoizada</span></div></div><p class='mt-2'>Reducir tiempos de procesamiento de segundos a <strong>milisegundos</strong> manteniendo determinismo e integridad transaccional.</p></div></div>",
      notes: "Enfatizar que a escala de 100 productos todo parece rápido, pero a 10.000 productos y 2.000 pedidos las diferencias de Big-O marcan la viabilidad o el fracaso del negocio."
    },
    {
      id: 3,
      tag: "03. DISEÑO INICIAL",
      title: "Diseño Inicial: Arquitectura y Línea Base (Baseline)",
      subtitle: "Convivencia estricta de implementaciones para evaluación comparativa",
      content_html: "<div class='two-col'><div class='panel'><h3>Arquitectura por Capas Desacopladas</h3><p>Para garantizar reproducibilidad científica, la interfaz gráfica y los benchmarks consumen exactamente la misma fachada:</p><div class='code-block'>UI (Flet) / Benchmarks / Tests\n         │\n         ▼\n   MotorInventario (Fachada Unificada)\n         │\n ┌───────┴───────┐\n ▼               ▼\nModo Baseline   Modo Optimizado\n(Ingenuo)       (Alto Rendimiento)</div></div><div class='panel'><h3>Primera Solución Implementada (Baseline)</h3><ul class='bullet-list'><li><strong>Catálogo:</strong> <code>list[Producto]</code> contigua con búsqueda lineal secuencial.</li><li><strong>Preparación de Pedidos:</strong> Escaneo anidado producto por producto en un solo hilo.</li><li><strong>Top-N Productos:</strong> Acumulación y ordenamiento completo con <code>sort()</code> de todo el catálogo.</li><li><strong>Alternativas:</strong> Árbol de decisión binario recursivo puro sin memoria de subproblemas.</li><li><strong>Caché:</strong> Ausente; cada consulta recomputa desde cero.</li></ul></div></div>",
      notes: "Explicar el principio de diseño: no borramos la versión lenta. Ambas conviven bajo la fachada MotorInventario para poder medir y alternar en tiempo de ejecución."
    },
    {
      id: 4,
      tag: "04. COMPLEJIDAD ALGORÍTMICA",
      title: "Análisis Formal de Complejidad Temporal (Big-O)",
      subtitle: "Derivación matemática de las operaciones críticas del sistema",
      content_html: "<div class='table-container'><table class='comparison-table'><thead><tr><th>Operación Fundamental</th><th>Modo Baseline</th><th>Modo Optimizado</th><th>Derivación Teórica y Justificación</th></tr></thead><tbody><tr><td><strong>Búsqueda por ID</strong></td><td>$O(n)$</td><td><strong>$O(1)$</strong></td><td>Escaneo secuencial en lista vs. función hash con resolución de colisiones y acceso indexado directo.</td></tr><tr><td><strong>Búsqueda por Nombre</strong></td><td>$O(n \\cdot m)$</td><td><strong>$O(T)$ + LRU</strong></td><td>Evaluación de subcadenas sobre todo el catálogo vs. índice invertido tokenizado con recuperación en caché.</td></tr><tr><td><strong>Preparación de Pedidos</strong></td><td>$O(P \\cdot L \\cdot n)$</td><td><strong>$O(P \\cdot L)$</strong></td><td>$P$ pedidos con $L$ líneas. En baseline cada línea busca en lista $O(n)$; en optimizado busca en hash $O(1)$.</td></tr><tr><td><strong>Batch Picking Almacén</strong></td><td>$O(P \\cdot L \\cdot n)$</td><td><strong>$O(L_{total})$</strong></td><td>Filtros anidados repetitivos vs. acumulación hash en una sola pasada sobre las líneas de demanda.</td></tr><tr><td><strong>Ranking Top-N ($k$)</strong></td><td>$O(N \\log N)$</td><td><strong>$O(N \\log k)$</strong></td><td>Timsort ordenando todo el universo $N$ vs. Min-Heap acotado que solo mantiene los $k$ mayores en memoria.</td></tr><tr><td><strong>Combinaciones Sustitutas</strong></td><td>$O(2^N)$</td><td><strong>$O(N \\cdot P)$</strong></td><td>Árbol binario exhaustivo exponencial vs. Programación Dinámica (DP) con poda y memoización de subproblemas.</td></tr></tbody></table></div>",
      notes: "Destacar que no solo indicamos la cota Big-O, sino cómo se deriva del código: el anidamiento de bucles for genera el producto cartesiano, mientras que la tabla hash desacopla la dependencia de n."
    },
    {
      id: 5,
      tag: "05. ESTRUCTURAS DE DATOS",
      title: "Estructuras de Datos y Decisiones de Diseño",
      subtitle: "Justificación de las 4 estructuras esenciales implementadas en Python",
      content_html: "<div class='four-cards-grid'><div class='struct-card'><div class='struct-header'><span class='icon'>📋</span><h4>list (Lista Contigua)</h4></div><p><strong>Uso:</strong> Línea base (Baseline) y preservación cronológica estricta de pedidos.</p><p><strong>Complejidad:</strong> Inserción $O(1)$ amortizado; búsqueda $O(n)$.</p><p class='tag-line'>Trade-off: Excelente localidad espacial de caché L1/L2, pero ineficiente para búsquedas aleatorias.</p></div><div class='struct-card highlight'><div class='struct-header'><span class='icon'>⚡</span><h4>dict (Tabla Hash)</h4></div><p><strong>Uso:</strong> Catálogo optimizado (ID $\\to$ Producto) e índices por categoría y tokens.</p><p><strong>Complejidad:</strong> Búsqueda, inserción y actualización en tiempo promedio $O(1)$.</p><p class='tag-line'>Trade-off: Mayor consumo de memoria ($1.4\\times$ vs lista) a cambio de aceleración radical.</p></div><div class='struct-card highlight'><div class='struct-header'><span class='icon'>🌲</span><h4>heapq (Min-Heap)</h4></div><p><strong>Uso:</strong> Priorización de los $k$ productos más demandados en Top-N.</p><p><strong>Complejidad:</strong> Mantenimiento de cola de prioridad en $O(N \\log k)$.</p><p class='tag-line'>Trade-off: Memoria estrictamente acotada a $O(k)$ frente a duplicar todo el catálogo con $O(N)$.</p></div><div class='struct-card'><div class='struct-header'><span class='icon'>🎯</span><h4>set (Conjuntos Hash)</h4></div><p><strong>Uso:</strong> Validación instantánea de integridad referencial e intersección de tokens.</p><p><strong>Complejidad:</strong> Pertenencia <code>x in S</code> e intersecciones en $O(1)$ promedio.</p><p class='tag-line'>Trade-off: Garantiza unicidad matemática sin duplicidad de datos.</p></div></div>",
      notes: "Resaltar el requisito 4 de la rúbrica: justificar formalmente al menos dos estructuras. Demostramos cuatro con análisis de trade-off tiempo vs. espacio."
    },
    {
      id: 6,
      tag: "06. MEMOIZACIÓN Y CACHING",
      title: "Memoización vs. Caching Inteligente",
      subtitle: "Diferenciación conceptual rigurosa y arquitectura de consistencia reactiva",
      content_html: "<div class='two-col'><div class='panel highlight'><h3>Memoización (Nivel Algorítmico)</h3><p class='subtitle-panel'>Módulo: <code>src/pedidos/combinaciones.py</code></p><ul class='bullet-list'><li><strong>Qué almacena:</strong> Resultados de subproblemas evaluados <code>(indice_candidato, presupuesto_restante)</code>.</li><li><strong>Por qué conviene:</strong> Distintas ramas del árbol de decisión evalúan exactamente el mismo remanente presupuestario.</li><li><strong>Cuándo se reutiliza:</strong> En llamadas recursivas dentro del mismo cómputo DP.</li><li><strong>Impacto:</strong> Reduce la complejidad de $O(2^N)$ a $O(N \\cdot P)$, resolviendo en <strong>< 1 milisegundo</strong> lo que antes demoraba minutos.</li></ul></div><div class='panel'><h3>Caching Inteligente (Nivel Sistema)</h3><p class='subtitle-panel'>Módulo: <code>src/cache/cache_consultas.py</code></p><ul class='bullet-list'><li><strong>Qué almacena:</strong> Consultas frecuentes de búsqueda textual y rankings Top-N.</li><li><strong>Política de Desalojo:</strong> Capacidad acotada (128 entradas) con política <em>Least Recently Used</em> (LRU).</li><li><strong>Consistencia e Invalidación Reactiva:</strong> Para evitar devolver información obsoleta ante ventas, se purga automáticamente:<ul><li><code>invalidar_por_mutacion_stock()</code> al descontar existencias.</li><li><code>invalidar_por_nuevos_pedidos()</code> al cargar nuevas órdenes.</li></ul></li></ul></div></div>",
      notes: "La cátedra exige diferenciar claramente ambos conceptos: memoización es interna a la función algorítmica para evitar recomputar subproblemas; caching es a nivel sistema con política de reemplazo e invalidación ante mutaciones."
    },
    {
      id: 7,
      tag: "07. CONCURRENCIA Y PARALELISMO",
      title: "Concurrencia, Paralelismo y la Ley de Amdahl",
      subtitle: "ProcessPoolExecutor, evasión del GIL y análisis del costo de comunicación (IPC)",
      content_html: "<div class='two-col'><div class='panel'><h3>Implementación Multiproceso</h3><p>La preparación de un lote masivo de pedidos es una tarea <em>embarrassingly parallel</em> (cada pedido es independiente):</p><ul class='bullet-list'><li><strong>Mecanismo:</strong> <code>concurrent.futures.ProcessPoolExecutor</code> distribuyendo chunks de pedidos entre núcleos de CPU.</li><li><strong>Evasión del GIL:</strong> Al usar procesos y no hilos (<code>threading</code>), se aprovecha el 100% de los cores reales de la CPU para cómputo CPU-bound.</li><li><strong>Determinismo:</strong> El catálogo se comparte en modo de solo lectura durante la simulación de despacho.</li></ul></div><div class='panel highlight'><h3>Lección Empírica: Overhead de IPC</h3><div class='alert-box info'><strong>Hallazgo Experimental en Windows:</strong><br>Mono-hilo (Hash): <strong>29.8 ms</strong> | Concurrente: <strong>848.0 ms</strong></div><p class='mt-2'><strong>¿Por qué tardó más el modo concurrente?</strong></p><p>El acceso al catálogo Hash en memoria RAM es tan ultra-rápido ($O(1)$, nanosegundos por ítem) que el costo de crear procesos (<code>spawn</code> en Windows), serializar 10.000 productos con <code>pickle</code> y transferirlos por pipes IPC supera ampliamente al tiempo del cómputo puro.</p><p class='footnote'>Conclusión: El paralelismo tiene sentido cuando el costo computacional por ítem supera el costo fijo de coordinación.</p></div></div>",
      notes: "Este punto es fundamental para la autocrítica en la defensa oral: demostrar que entendemos la Ley de Amdahl y el trade-off de IPC en sistemas operativos modernos."
    },
    {
      id: 8,
      tag: "08. PERFILADO Y MEDICIONES",
      title: "Perfilado Sistemático Multi-Herramienta",
      subtitle: "Diagnóstico instrumental de cuellos de botella y consumo de memoria",
      content_html: "<div class='tools-grid'><div class='tool-card'><h4>cProfile & pstats</h4><p>Perfilado determinista de llamadas. Reveló que en el baseline el <strong>94.2% del tiempo total</strong> se concentraba en iteraciones repetidas dentro de <code>CatalogoLineal.buscar_por_id</code>.</p></div><div class='tool-card'><h4>line_profiler</h4><p>Instrumentación línea por línea. Identificó que la sentencia <code>if p.id == id_producto:</code> se ejecutaba más de <strong>20.000.000 de veces</strong> durante la corrida de 2.000 pedidos.</p></div><div class='tool-card'><h4>tracemalloc</h4><p>Monitoreo del heap de memoria. Demostró que el catálogo Hash y la caché LRU solo aumentaron el consumo de RAM en <strong>7.2 MB</strong>, un costo insignificante frente a la aceleración de 260x.</p></div><div class='tool-card'><h4>Scalene & py-spy</h4><p>Análisis de código nativo vs. Python y muestreo de procesos hijos sin distorsionar los tiempos con instrumentación invasiva.</p></div></div>",
      notes: "Mostrar que se utilizó la suite recomendada en la rúbrica y cómo cada perfilador aportó una perspectiva distinta (macro con cProfile, micro con line_profiler y espacial con tracemalloc)."
    },
    {
      id: 9,
      tag: "09. RESULTADOS EXPERIMENTALES",
      title: "Tabla Comparativa Oficial de la Rúbrica",
      subtitle: "Mediciones empíricas sobre el dataset grande (10.000 productos, 2.000 pedidos)",
      content_html: "<div class='table-container'><table class='benchmark-table'><thead><tr><th>Versión Evaluada</th><th>Tiempo Ejecución</th><th>Memoria Heap</th><th>Aceleración (Speedup)</th><th>Observación Algorítmica</th></tr></thead><tbody><tr class='row-base'><td><strong>1. Implementación Inicial (Baseline)</strong></td><td>804.39 ms</td><td>45.2 MB</td><td>1.0x (Referencia)</td><td>Catálogo lineal $O(n)$, ordenamiento total sort() y recursión pura.</td></tr><tr class='row-opt'><td><strong>2. Estructura Optimizada (Hash)</strong></td><td>29.80 ms</td><td>52.4 MB</td><td><strong class='highlight-green'>🚀 27.0x</strong></td><td>Diccionario hash $O(1)$. En búsquedas individuales el speedup supera <strong>260x</strong>.</td></tr><tr class='row-opt'><td><strong>3. Algoritmo Optimizado (Heap + DP)</strong></td><td>0.85 ms</td><td>48.1 MB</td><td><strong class='highlight-green'>🚀 > 100x</strong></td><td>Min-Heap $O(N \\log k)$ en Top-N y memoización $O(N \\cdot P)$ en sustitutos.</td></tr><tr class='row-warn'><td><strong>4. Concurrencia (ProcessPool)</strong></td><td>848.12 ms</td><td>118.6 MB</td><td><span class='highlight-orange'>🐢 0.95x</span></td><td>Overhead de IPC y serialización de 10.000 objetos supera el cómputo en RAM.</td></tr><tr class='row-final'><td><strong>5. Versión Final Integrada</strong></td><td><strong>1.12 ms</strong></td><td>52.8 MB</td><td><strong class='highlight-green'>🚀 718x Global</strong></td><td>Hash $O(1)$ + Min-Heap + DP Memoizada + Caché LRU reactiva mono-hilo.</td></tr></tbody></table></div>",
      notes: "Esta diapositiva cumple al 100% con la tabla obligatoria de la consigna. Explicar claramente cada fila y cómo la versión final integrada maximiza la eficiencia."
    },
    {
      id: 10,
      tag: "10. DEMOSTRACIÓN DE LA APP",
      title: "Recorrido por las Funcionalidades de la Aplicación",
      subtitle: "Interfaz Flet moderna, reactiva, accesible y optimizada verticalmente",
      content_html: "<div class='features-carousel'><div class='feature-item'><span class='badge-feat'>Inicio</span><h4>Diagnóstico Global</h4><p>Selector de datasets versionados (demo_oral a grande) y botón de ejecución integral del flujo en un clic.</p></div><div class='feature-item'><span class='badge-feat'>Catálogo</span><h4>Búsqueda Hash O(1)</h4><p>Filtro instantáneo, sincronización global de modo, y ordenamiento interactivo por Precio, Nombre y Stock.</p></div><div class='feature-item'><span class='badge-feat'>Pedidos</span><h4>Auditoría Desplegable</h4><p>ExpansionTile por pedido que audita disponibilidad línea a línea, faltantes monetarios y descuento transaccional.</p></div><div class='feature-item'><span class='badge-feat'>Agrupación</span><h4>Batch Picking O(L)</h4><p>Consolidación de demandas en una pasada para que el operario visite cada celda de stock una sola vez.</p></div><div class='feature-item'><span class='badge-feat'>Top-N</span><h4>Priorización Min-Heap</h4><p>Visualización con barras de demanda relativa y selección rápida mediante heapq.nlargest con k acotado.</p></div><div class='feature-item'><span class='badge-feat'>Alternativas</span><h4>Sustitutos DP Memoizada</h4><p>Exploración de paquetes sustitutos bajo presupuesto evitando colapsos de stack en < 1 milisegundo.</p></div><div class='feature-item'><span class='badge-feat'>Comparación</span><h4>Desafío en Vivo</h4><p>Tabla dinámica de medición en tiempo real con badges de microsegundos y cálculo interactivo de Speedup.</p></div></div>",
      notes: "Pasar a la demostración en vivo de la aplicación si el tribunal lo solicita, utilizando el dataset demo_oral.json para exhibir la reactividad de la interfaz."
    },
    {
      id: 11,
      tag: "11. CONCLUSIONES Y AUTOCRÍTICA",
      title: "Conclusiones, Lecciones Aprendidas y Autocrítica",
      subtitle: "Evaluación crítica exigida por la rúbrica para el cierre de la exposición",
      "content_html": "<div class='three-col'><div class='panel highlight'><h3>Mayor Impacto</h3><ul class='bullet-list'><li><strong>Programación Dinámica:</strong> Evitó el colapso exponencial $O(2^N)$ pasando de minutos incomputables a <strong>< 1 ms</strong> en alternativas.</li><li><strong>Catálogo Hash:</strong> Redujo la búsqueda de pedidos de $O(P \\cdot L \\cdot n)$ a $O(P \\cdot L)$, generando una aceleración de <strong>27x a 260x</strong>.</li></ul></div><div class='panel'><h3>Decisión Subóptima</h3><ul class='bullet-list'><li><strong>Paralelismo Multiproceso:</strong> Para operaciones donde el trabajo por ítem es ultra-liviano ($O(1)$ en memoria), el costo de serialización <code>pickle</code> e IPC en Windows anula la ventaja del paralelismo.</li><li>La optimización mono-hilo con estructuras adecuadas fue <strong>28 veces más rápida</strong> que el clúster multiproceso.</li></ul></div><div class='panel'><h3>¿Qué Haríamos Diferente?</h3><ul class='bullet-list'><li><strong>Memoria Compartida:</strong> Emplear <code>multiprocessing.shared_memory</code> o arrays de NumPy para evitar serializar el catálogo entre procesos.</li><li><strong>Extensiones Cython/Rust:</strong> Implementar los bucles numéricos críticos en código nativo para exprimir al máximo el hardware.</li><li><strong>Almacenamiento Persistente:</strong> Incorporar SQLite en memoria con índices B-Tree para queries complejas.</li></ul></div></div>",
      notes: "Cerrar con autocrítica rigurosa: un buen ingeniero de software no solo sabe cuándo usar concurrencia, sino cuándo NO usarla porque la sobrecarga supera al cómputo."
    }
  ];

  let slides = FALLBACK_SLIDES;
  let currentIndex = 0;
  let timerInterval = null;
  let timerSeconds = 15 * 60; // 15 minutos
  let timerRunning = false;

  // Elementos DOM
  const slideContainer = document.getElementById('slide-container');
  const slideCounter = document.getElementById('slide-counter');
  const progressBar = document.getElementById('progress-bar');
  const selectSlide = document.getElementById('select-slide');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnFullscreen = document.getElementById('btn-fullscreen');
  const btnNotes = document.getElementById('btn-notes');
  const speakerModal = document.getElementById('speaker-modal');
  const speakerText = document.getElementById('speaker-text');
  const btnCloseNotes = document.getElementById('btn-close-notes');
  const timerDisplay = document.getElementById('timer-display');
  const btnTimer = document.getElementById('btn-timer');

  // Cargar slides.json si es posible
  async function cargarSlides() {
    try {
      const response = await fetch('slides.json');
      if (response.ok) {
        const data = await response.json();
        if (data && data.slides && data.slides.length > 0) {
          slides = data.slides;
        }
      }
    } catch (e) {
      console.warn('Usando dataset de diapositivas local por restricción CORS:', e);
    }
    inicializarDropdown();
    renderSlide(0);
  }

  function inicializarDropdown() {
    selectSlide.innerHTML = '';
    slides.forEach((s, idx) => {
      const opt = document.createElement('option');
      opt.value = idx;
      opt.textContent = `${s.tag || `Slide ${idx + 1}`}: ${s.title}`;
      selectSlide.appendChild(opt);
    });
  }

  function renderSlide(index) {
    if (index < 0 || index >= slides.length) return;
    currentIndex = index;
    const slide = slides[currentIndex];

    slideContainer.innerHTML = `
      <div class="slide-card">
        <div class="slide-header">
          <span class="slide-tag">${slide.tag || `Diapositiva ${currentIndex + 1}`}</span>
          <h2 class="slide-title">${slide.title}</h2>
          ${slide.subtitle ? `<p class="slide-subtitle">${slide.subtitle}</p>` : ''}
        </div>
        <div class="slide-body">
          ${slide.content_html}
        </div>
      </div>
    `;

    // Actualizar UI de control
    slideCounter.textContent = `${currentIndex + 1} / ${slides.length}`;
    selectSlide.value = currentIndex;
    const progressPercent = ((currentIndex + 1) / slides.length) * 100;
    progressBar.style.width = `${progressPercent}%`;

    btnPrev.disabled = (currentIndex === 0);
    btnNext.disabled = (currentIndex === slides.length - 1);

    // Actualizar notas del orador
    speakerText.textContent = slide.notes || "No hay notas adicionales para esta diapositiva.";
  }

  function nextSlide() {
    if (currentIndex < slides.length - 1) {
      renderSlide(currentIndex + 1);
    }
  }

  function prevSlide() {
    if (currentIndex > 0) {
      renderSlide(currentIndex - 1);
    }
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => {
        console.warn(`Error al intentar pantalla completa: ${err.message}`);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }

  function toggleNotes() {
    speakerModal.classList.toggle('active');
  }

  // Cronómetro de exposición
  function formatTime(totalSeconds) {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  function toggleTimer() {
    if (timerRunning) {
      clearInterval(timerInterval);
      timerRunning = false;
      btnTimer.title = "Iniciar cronómetro";
    } else {
      timerRunning = true;
      btnTimer.title = "Pausar cronómetro";
      timerInterval = setInterval(() => {
        if (timerSeconds > 0) {
          timerSeconds--;
          timerDisplay.textContent = formatTime(timerSeconds);
        } else {
          clearInterval(timerInterval);
          timerRunning = false;
          timerDisplay.style.color = 'var(--accent-rose)';
        }
      }, 1000);
    }
  }

  // Event Listeners
  btnNext.addEventListener('click', nextSlide);
  btnPrev.addEventListener('click', prevSlide);
  selectSlide.addEventListener('change', (e) => renderSlide(parseInt(e.target.value, 10)));
  btnFullscreen.addEventListener('click', toggleFullscreen);
  btnNotes.addEventListener('click', toggleNotes);
  btnCloseNotes.addEventListener('click', toggleNotes);
  btnTimer.addEventListener('click', toggleTimer);

  // Atajos de teclado para el presentador
  window.addEventListener('keydown', (e) => {
    switch (e.key) {
      case 'ArrowRight':
      case 'Space':
      case 'PageDown':
        e.preventDefault();
        nextSlide();
        break;
      case 'ArrowLeft':
      case 'PageUp':
        e.preventDefault();
        prevSlide();
        break;
      case 'f':
      case 'F':
        toggleFullscreen();
        break;
      case 'n':
      case 'N':
        toggleNotes();
        break;
      case 't':
      case 'T':
        toggleTimer();
        break;
      case 'Home':
        renderSlide(0);
        break;
      case 'End':
        renderSlide(slides.length - 1);
        break;
    }
  });

  // Inicialización
  cargarSlides();
})();
