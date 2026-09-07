import json
import os

with open('docs/presentation/slides.json', 'r', encoding='utf-8') as f:
    slides_data = json.load(f)

fallback_slides_json = json.dumps(slides_data['slides'], ensure_ascii=False, indent=2)

js_template = f"""/**
 * ==========================================================================
 * APLICACIÓN DE PRESENTACIÓN INTERACTIVA (PAPER STYLE & REACTIVE CANVAS)
 * Programación Eficiente — Primer Parcial (Opción 6) | Universidad Blas Pascal
 * ==========================================================================
 */

(function () {{
  'use strict';

  // Fallback de datos embebido sincronizado con slides.json (para ejecución offline y file://)
  const FALLBACK_SLIDES = {fallback_slides_json};

  let slides = FALLBACK_SLIDES;
  let currentIndex = 0;
  let timerInterval = null;
  let timerSeconds = 15 * 60; // 15 minutos oficiales
  let timerRunning = false;
  let simRunning = false;

  // Elementos DOM Principales
  const slideContainer = document.getElementById('slide-container');
  const slideCounter = document.getElementById('slide-counter');
  const progressBar = document.getElementById('progress-bar');
  const selectSlide = document.getElementById('select-slide');
  const btnPrev = document.getElementById('btn-prev');
  const btnNext = document.getElementById('btn-next');
  const btnFullscreen = document.getElementById('btn-fullscreen');
  const btnNotes = document.getElementById('btn-notes');
  const btnShortcuts = document.getElementById('btn-shortcuts');
  const speakerModal = document.getElementById('speaker-modal');
  const shortcutsModal = document.getElementById('shortcuts-modal');
  const speakerText = document.getElementById('speaker-text');
  const btnCloseNotes = document.getElementById('btn-close-notes');
  const btnCloseShortcuts = document.getElementById('btn-close-shortcuts');
  const timerDisplay = document.getElementById('timer-display');
  const btnTimer = document.getElementById('btn-timer');
  const slidePills = document.getElementById('slide-pills');
  const bgCanvas = document.getElementById('bg-canvas');

  // ==========================================================================
  // MOTOR CANVAS REACTIVO Y CINÉTICO (PAPER STYLE BACKGROUND ENGINE)
  // ==========================================================================
  class PaperCanvasEngine {{
    constructor(canvas) {{
      this.canvas = canvas;
      if (!this.canvas) return;
      this.ctx = canvas.getContext('2d');
      this.particles = [];
      this.ripples = [];
      this.waves = [];
      this.slideTheme = 1;
      this.width = 0;
      this.height = 0;
      this.dpr = Math.min(window.devicePixelRatio || 1, 2);
      this.mouse = {{ x: -1000, y: -1000, active: false }};
      this.time = 0;
      this.orbitFocus = null; // 'baseline' o 'opt' para slide 3
      this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      this.initDimensions();
      this.initParticles();
      this.initEvents();
      this.startLoop();
    }}

    initDimensions() {{
      this.width = window.innerWidth;
      this.height = window.innerHeight;
      this.canvas.width = this.width * this.dpr;
      this.canvas.height = this.height * this.dpr;
      this.ctx.scale(this.dpr, this.dpr);
    }}

    initParticles() {{
      this.particles = [];
      const count = 48;
      const palette = [
        {{ r: 194, g: 65, b: 12, a: 0.18 }},   // Terracotta stamp
        {{ r: 29, g: 78, b: 216, a: 0.15 }},   // Blueprint blue
        {{ r: 21, g: 128, b: 61, a: 0.15 }},   // Sage green
        {{ r: 15, g: 23, b: 42, a: 0.12 }}     // Archival ink
      ];

      for (let i = 0; i < count; i++) {{
        const pColor = palette[i % palette.length];
        this.particles.push({{
          x: Math.random() * this.width,
          y: Math.random() * this.height,
          vx: (Math.random() - 0.5) * 0.7,
          vy: (Math.random() - 0.5) * 0.7,
          size: Math.random() * 3 + 1.5,
          color: pColor,
          angle: Math.random() * Math.PI * 2,
          angularSpeed: (Math.random() - 0.5) * 0.02,
          length: Math.random() * 10 + 4, // Aspecto de fibra de papel
          targetX: 0,
          targetY: 0
        }});
      }}
    }}

    initEvents() {{
      window.addEventListener('resize', () => {{
        this.initDimensions();
      }});

      window.addEventListener('mousemove', (e) => {{
        this.mouse.x = e.clientX;
        this.mouse.y = e.clientY;
        this.mouse.active = true;
        if (Math.random() < 0.12) {{
          this.addRipple(e.clientX, e.clientY, 35, 'rgba(194, 65, 12, 0.12)');
        }}
      }});

      window.addEventListener('mouseleave', () => {{
        this.mouse.active = false;
      }});
    }}

    addRipple(x, y, maxRadius, strokeColor) {{
      this.ripples.push({{
        x: x,
        y: y,
        radius: 4,
        maxRadius: maxRadius || 80,
        alpha: 0.35,
        color: strokeColor || 'rgba(194, 65, 12, 0.2)'
      }});
    }}

    onSlideChange(slideIndex, direction) {{
      this.slideTheme = slideIndex + 1;
      this.orbitFocus = null;

      // Onda de choque de transición
      const startX = direction === 'left' ? this.width * 0.15 : (direction === 'right' ? this.width * 0.85 : this.width * 0.5);
      this.addRipple(startX, this.height * 0.5, this.width * 0.55, 'rgba(29, 78, 216, 0.22)');

      // Impulso físico a partículas según la temática de la diapositiva
      this.particles.forEach((p, idx) => {{
        if (this.slideTheme === 2) {{
          // Slide 2: Problema / Caos logístico ➔ velocidad alta y dispersión
          p.vx = (Math.random() - 0.5) * 3.2;
          p.vy = (Math.random() - 0.5) * 3.2;
        }} else if (this.slideTheme === 3) {{
          // Slide 3: Arquitectura Dual ➔ atracción a dos centros
          const isLeft = idx % 2 === 0;
          p.targetX = isLeft ? this.width * 0.28 : this.width * 0.72;
          p.targetY = this.height * 0.65;
        }} else if (this.slideTheme === 5) {{
          // Slide 5: Estructuras de Datos ➔ 4 cuadrantes
          const quad = idx % 4;
          const qx = (quad % 2 === 0 ? 0.25 : 0.75) * this.width;
          const qy = (quad < 2 ? 0.35 : 0.75) * this.height;
          p.targetX = qx;
          p.targetY = qy;
        }} else if (this.slideTheme === 7) {{
          // Slide 7: Concurrencia ➔ canales horizontales
          const stream = (idx % 3);
          p.targetY = this.height * (0.3 + stream * 0.22);
          p.vx = (stream + 1) * 1.5;
          p.vy = 0;
        }} else if (this.slideTheme === 9) {{
          // Slide 9: Resultados / Speedup 718x ➔ propulsión horizontal veloz
          p.vx = (Math.random() * 4 + 2);
          p.vy = (Math.random() - 0.5) * 0.4;
        }} else {{
          // Velocidad normal suave
          p.vx = (Math.random() - 0.5) * 0.8;
          p.vy = (Math.random() - 0.5) * 0.8;
        }}
      }});
    }}

    setOrbitFocus(branch) {{
      this.orbitFocus = branch;
      const targetCenterX = branch === 'baseline' ? this.width * 0.28 : this.width * 0.72;
      const targetCenterY = this.height * 0.65;
      this.addRipple(targetCenterX, targetCenterY, 120, branch === 'baseline' ? 'rgba(225, 29, 72, 0.3)' : 'rgba(21, 128, 61, 0.3)');
    }}

    update() {{
      this.time += 0.016;

      // Actualizar ondas concéntricas
      for (let i = this.ripples.length - 1; i >= 0; i--) {{
        const r = this.ripples[i];
        r.radius += (r.maxRadius - r.radius) * 0.07 + 0.8;
        r.alpha -= 0.008;
        if (r.alpha <= 0 || r.radius >= r.maxRadius) {{
          this.ripples.splice(i, 1);
        }}
      }}

      // Actualizar partículas
      this.particles.forEach((p, idx) => {{
        p.angle += p.angularSpeed;

        // Comportamientos reactivos según slide activa
        if (this.slideTheme === 3) {{
          // Dual orbit (Baseline vs Optimizado)
          let targetX = (idx % 2 === 0) ? this.width * 0.28 : this.width * 0.72;
          let targetY = this.height * 0.65;
          if (this.orbitFocus === 'baseline' && idx % 2 === 0) {{
            p.vx += (targetX - p.x) * 0.004;
            p.vy += (targetY - p.y) * 0.004;
          }} else if (this.orbitFocus === 'opt' && idx % 2 !== 0) {{
            p.vx += (targetX - p.x) * 0.004;
            p.vy += (targetY - p.y) * 0.004;
          }} else {{
            p.vx += (targetX - p.x) * 0.001;
            p.vy += (targetY - p.y) * 0.001;
          }}
          p.vx *= 0.95;
          p.vy *= 0.95;
        }} else if (this.slideTheme === 5 && p.targetX && p.targetY) {{
          // Gravitación a cuadrantes
          p.vx += (p.targetX - p.x) * 0.0015;
          p.vy += (p.targetY - p.y) * 0.0015;
          p.vx *= 0.94;
          p.vy *= 0.94;
        }} else if (this.slideTheme === 7) {{
          // Canales de concurrencia
          if (p.x > this.width + 20) p.x = -20;
        }} else if (this.slideTheme === 9) {{
          // Ráfaga horizontal de aceleración
          if (p.x > this.width + 20) p.x = -20;
        }} else {{
          // Deriva ambiental estándar
          p.vx += Math.sin(this.time * 0.5 + idx) * 0.015;
          p.vy += Math.cos(this.time * 0.5 + idx) * 0.015;
          p.vx = Math.max(-1.2, Math.min(1.2, p.vx));
          p.vy = Math.max(-1.2, Math.min(1.2, p.vy));
        }}

        // Reactividad ante el cursor
        if (this.mouse.active) {{
          const dx = p.x - this.mouse.x;
          const dy = p.y - this.mouse.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 100 && dist > 0) {{
            const force = (100 - dist) / 100 * 1.5;
            p.vx += (dx / dist) * force;
            p.vy += (dy / dist) * force;
          }}
        }}

        p.x += p.vx;
        p.y += p.vy;

        // Rebote suave en los límites
        if (p.x < -30) p.x = this.width + 30;
        if (p.x > this.width + 30) p.x = -30;
        if (p.y < -30) p.y = this.height + 30;
        if (p.y > this.height + 30) p.y = -30;
      }});
    }}

    draw() {{
      this.ctx.clearRect(0, 0, this.width, this.height);

      // 1. Dibujar curvas topográficas de papel fluido en el fondo
      this.drawTopographicWaves();

      // 2. Dibujar líneas de conexión entre partículas cercanas si es Slide 6 (Memoización)
      if (this.slideTheme === 6) {{
        this.drawTreeConnections();
      }}

      // 3. Dibujar escaneo radar en Slide 8 (Perfilado)
      if (this.slideTheme === 8) {{
        this.drawScannerBar();
      }}

      // 4. Dibujar ondas de choque y ripples
      this.ripples.forEach(r => {{
        this.ctx.beginPath();
        this.ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
        this.ctx.strokeStyle = r.color;
        this.ctx.lineWidth = 1.5;
        this.ctx.globalAlpha = Math.max(0, r.alpha);
        this.ctx.stroke();
      }});
      this.ctx.globalAlpha = 1;

      // 5. Dibujar fibras de papel / partículas de tinta
      this.particles.forEach(p => {{
        this.ctx.save();
        this.ctx.translate(p.x, p.y);
        this.ctx.rotate(p.angle);
        this.ctx.fillStyle = `rgba(${{p.color.r}}, ${{p.color.g}}, ${{p.color.b}}, ${{p.color.a}})`;

        // Dibujar pequeñas fibras rectangulares alargadas tipo grano de papel
        this.ctx.beginPath();
        this.ctx.roundRect(-p.length / 2, -p.size / 2, p.length, p.size, 2);
        this.ctx.fill();
        this.ctx.restore();
      }});
    }}

    drawTopographicWaves() {{
      const waveConfigs = [
        {{ yFactor: 0.35, amp: 28, freq: 0.0018, color: 'rgba(194, 65, 12, 0.035)', speed: 0.6 }},
        {{ yFactor: 0.65, amp: 36, freq: 0.0014, color: 'rgba(29, 78, 216, 0.03)', speed: 0.4 }},
        {{ yFactor: 0.88, amp: 24, freq: 0.0022, color: 'rgba(15, 23, 42, 0.025)', speed: 0.8 }}
      ];

      waveConfigs.forEach(w => {{
        this.ctx.beginPath();
        const baseY = this.height * w.yFactor;
        this.ctx.moveTo(0, baseY);

        for (let x = 0; x <= this.width; x += 30) {{
          const offset = Math.sin(x * w.freq + this.time * w.speed) * w.amp;
          this.ctx.lineTo(x, baseY + offset);
        }}

        this.ctx.strokeStyle = w.color;
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
      }});
    }}

    drawTreeConnections() {{
      this.ctx.strokeStyle = 'rgba(21, 128, 61, 0.12)';
      this.ctx.lineWidth = 1;
      for (let i = 0; i < this.particles.length; i++) {{
        for (let j = i + 1; j < this.particles.length; j++) {{
          const p1 = this.particles[i];
          const p2 = this.particles[j];
          const dx = p1.x - p2.x;
          const dy = p1.y - p2.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 120) {{
            this.ctx.beginPath();
            this.ctx.moveTo(p1.x, p1.y);
            this.ctx.lineTo(p2.x, p2.y);
            this.ctx.stroke();
          }}
        }}
      }}
    }}

    drawScannerBar() {{
      const scanX = ((this.time * 90) % (this.width + 100)) - 50;
      this.ctx.save();
      this.ctx.beginPath();
      this.ctx.moveTo(scanX, 0);
      this.ctx.lineTo(scanX, this.height);
      this.ctx.strokeStyle = 'rgba(29, 78, 216, 0.14)';
      this.ctx.lineWidth = 3;
      this.ctx.setLineDash([8, 6]);
      this.ctx.stroke();
      this.ctx.restore();
    }}

    startLoop() {{
      if (this.reducedMotion) {{
        this.update();
        this.draw();
        return;
      }}

      const loop = () => {{
        this.update();
        this.draw();
        requestAnimationFrame(loop);
      }};
      requestAnimationFrame(loop);
    }}
  }}

  // Instanciar el motor de fondo
  const canvasEngine = new PaperCanvasEngine(bgCanvas);

  // ==========================================================================
  // CARGA DE DIAPOSITIVAS Y NAVEGACIÓN
  // ==========================================================================
  async function cargarSlides() {{
    try {{
      const response = await fetch('slides.json');
      if (response.ok) {{
        const data = await response.json();
        if (data && data.slides && data.slides.length > 0) {{
          slides = data.slides;
        }}
      }}
    }} catch (e) {{
      console.warn('Usando dataset de diapositivas local por restricción CORS (file://):', e);
    }}
    inicializarDropdown();
    inicializarPills();
    renderSlide(0, 'none');
  }}

  function inicializarDropdown() {{
    selectSlide.innerHTML = '';
    slides.forEach((s, idx) => {{
      const opt = document.createElement('option');
      opt.value = idx;
      opt.textContent = `${{s.tag || `Slide ${{idx + 1}}`}}: ${{s.title}}`;
      selectSlide.appendChild(opt);
    }});
  }}

  function inicializarPills() {{
    if (!slidePills) return;
    slidePills.innerHTML = '';
    slides.forEach((s, idx) => {{
      const pill = document.createElement('button');
      pill.className = 'slide-pill' + (idx === currentIndex ? ' active' : '');
      pill.textContent = idx + 1;
      pill.title = s.tag || `Diapositiva ${{idx + 1}}`;
      pill.type = 'button';
      pill.setAttribute('aria-label', `Saltar a diapositiva ${{idx + 1}}: ${{s.title}}`);
      pill.addEventListener('click', () => {{
        const dir = idx > currentIndex ? 'right' : 'left';
        renderSlide(idx, dir);
      }});
      slidePills.appendChild(pill);
    }});
  }}

  function renderSlide(index, direction) {{
    if (index < 0 || index >= slides.length) return;
    currentIndex = index;
    const slide = slides[currentIndex];

    // Notificar al motor de fondo animado
    if (canvasEngine) {{
      canvasEngine.onSlideChange(currentIndex, direction);
    }}

    const animClass = direction === 'left' ? 'slide-enter-left' : (direction === 'right' ? 'slide-enter-right' : '');

    slideContainer.innerHTML = `
      <div class="slide-card ${{animClass}}" id="current-slide-card">
        <div class="slide-header">
          <span class="slide-tag">${{slide.tag || `Diapositiva ${{currentIndex + 1}}`}}</span>
          <h2 class="slide-title">${{slide.title}}</h2>
          ${{slide.subtitle ? `<p class="slide-subtitle">${{slide.subtitle}}</p>` : ''}}
        </div>
        <div class="slide-body">
          ${{slide.content_html}}
        </div>
      </div>
    `;

    // Actualizar Controles de Navegación
    slideCounter.textContent = `${{currentIndex + 1}} / ${{slides.length}}`;
    selectSlide.value = currentIndex;
    const progressRatio = (currentIndex + 1) / slides.length;
    progressBar.style.transform = `scaleX(${{progressRatio}})`;

    if (slidePills) {{
      const pills = slidePills.querySelectorAll('.slide-pill');
      pills.forEach((p, idx) => {{
        p.classList.toggle('active', idx === currentIndex);
      }});
    }}

    btnPrev.disabled = (currentIndex === 0);
    btnNext.disabled = (currentIndex === slides.length - 1);

    // Actualizar Notas del Orador
    speakerText.textContent = slide.notes || "No hay notas adicionales para esta diapositiva.";

    // Inicializar comportamientos interactivos específicos
    initSlideInteractiveBehaviors(slide.id);
  }}

  // ==========================================================================
  // COMPORTAMIENTOS INTERACTIVOS DENTRO DE LAS DIAPOSITIVAS
  // ==========================================================================
  function initSlideInteractiveBehaviors(slideId) {{
    // 1. Manejo genérico de Pestañas (Tabs)
    const tabButtons = slideContainer.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {{
      btn.addEventListener('click', () => {{
        const targetTabId = btn.getAttribute('data-tab');
        const tabsContainer = btn.closest('.tabs-container');
        if (!tabsContainer) return;

        tabsContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        tabsContainer.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        const targetPane = tabsContainer.querySelector(`#${{targetTabId}}`);
        if (targetPane) {{
          targetPane.classList.add('active');
          if (targetTabId === 'tab-bench-chart') {{
            animateSpeedupBars();
          }}
        }}
      }});
    }});

    // 2. Diapositiva 03: Inspección Interactiva de Arquitectura Dual
    if (slideId === 3) {{
      const branchBase = document.getElementById('branch-baseline-card');
      const branchOpt = document.getElementById('branch-optimized-card');
      const flowMsg = document.getElementById('arch-flow-indicator');

      if (branchBase && branchOpt && flowMsg) {{
        branchBase.addEventListener('click', () => {{
          branchBase.classList.add('active');
          branchOpt.classList.remove('active');
          flowMsg.className = 'alert-box alert-base mt-3';
          flowMsg.style.borderColor = 'var(--stamp-crimson)';
          flowMsg.style.background = 'var(--stamp-crimson-bg)';
          flowMsg.innerHTML = "<strong>Ruta Baseline Activa:</strong> La fachada <code>MotorInventario</code> delega a <code>CatalogoLineal</code> en memoria contigua O(n). Sin indexación previa ni caching.";
          if (canvasEngine) canvasEngine.setOrbitFocus('baseline');
        }});

        branchOpt.addEventListener('click', () => {{
          branchOpt.classList.add('active');
          branchBase.classList.remove('active');
          flowMsg.className = 'alert-box info mt-3';
          flowMsg.style.borderColor = 'var(--stamp-sage)';
          flowMsg.style.background = 'var(--stamp-sage-bg)';
          flowMsg.innerHTML = "<strong>Ruta Optimizada Activa:</strong> La fachada delega a <code>dict</code> hash indexado O(1), min-heaps acotados y caché LRU reactiva con aceleración global de 718x.";
          if (canvasEngine) canvasEngine.setOrbitFocus('opt');
        }});
      }}
    }}

    // 3. Diapositiva 04: Simulador Interactivo O(n) vs O(1)
    if (slideId === 4) {{
      const btnRunSim = document.getElementById('btn-run-sim');
      const catalogSelect = document.getElementById('sim-catalog-size');
      const targetInput = document.getElementById('sim-target-id');

      if (catalogSelect && targetInput) {{
        catalogSelect.addEventListener('change', () => {{
          const n = parseInt(catalogSelect.value, 10);
          const targetIndex = Math.floor(n * 0.842);
          targetInput.value = `PROD-${{targetIndex.toString().padStart(5, '0')}}`;
          resetSimUI();
        }});
      }}

      if (btnRunSim) {{
        btnRunSim.addEventListener('click', runSearchSimulation);
      }}
    }}

    // 4. Diapositiva 05: Inspector Interactivo de Estructuras de Datos
    if (slideId === 5) {{
      const structCards = slideContainer.querySelectorAll('.struct-card');
      const detailBox = document.getElementById('struct-detail-box');
      const structData = {{
        'list': "<strong>list en Python:</strong> Implementada como arreglo de punteros contiguos en C (<code>PyListObject</code>). Ofrece acceso indexado <code>O(1)</code> gracias a la fórmula <code>base_ptr + i * ptr_size</code>, pero la búsqueda secuencial por valor requiere escaneo elemento a elemento <code>O(n)</code>.",
        'dict': "<strong>dict en Python:</strong> Tabla hash compacta con arreglo denso de entradas y tabla de índices dispersa. La función <code>hash()</code> evalúa el ID en tiempo constante; ante colisiones utiliza perturbación pseudoaleatoria, logrando consultas <code>O(1)</code>.",
        'heap': "<strong>heapq (Min-Heap):</strong> Árbol binario implícito mapeado en un array donde cada nodo cumple <code>heap[k] <= heap[2*k+1]</code>. Al mantener solo <code>k</code> elementos con <code>heapq.nlargest</code>, la inserción cuesta <code>O(log k)</code> en lugar de <code>O(N log N)</code>.",
        'set': "<strong>set en Python:</strong> Conjunto hash puro sin almacenamiento de valores asociados. Permite validaciones de membresía <code>x in set</code> en <code>O(1)</code> e intersección vectorial instantánea para filtrado multicriterio de pedidos."
      }};

      structCards.forEach(card => {{
        card.addEventListener('click', () => {{
          structCards.forEach(c => c.style.outline = 'none');
          card.style.outline = '2px solid var(--stamp-terracotta)';
          const st = card.getAttribute('data-struct');
          if (detailBox && structData[st]) {{
            detailBox.innerHTML = `🔬 ${{structData[st]}}`;
          }}
        }});
      }});
    }}

    // 5. Diapositiva 06: Demostración Interactiva de Cache LRU y Consistencia
    if (slideId === 6) {{
      const btnHit = document.getElementById('btn-cache-demo-hit');
      const btnMiss = document.getElementById('btn-cache-demo-miss');
      const btnInvalidate = document.getElementById('btn-cache-demo-invalidate');
      const slot1 = document.getElementById('slot-1');
      const slot2 = document.getElementById('slot-2');
      const slot3 = document.getElementById('slot-3');
      const feedback = document.getElementById('cache-feedback');

      if (btnHit && slot1 && feedback) {{
        btnHit.addEventListener('click', () => {{
          slot1.style.background = 'var(--stamp-sage-bg)';
          slot1.style.borderColor = 'var(--stamp-sage)';
          feedback.innerHTML = "⚡ <strong>CACHE HIT (0.01 ms):</strong> La consulta 'laptop' residía en la tabla LRU. Retorno instantáneo desde memoria sin tocar el motor de búsqueda.";
        }});
      }}

      if (btnMiss && slot3 && feedback) {{
        btnMiss.addEventListener('click', () => {{
          slot3.textContent = 'Slot 3: "teclado" [Nuevo]';
          slot3.style.background = 'var(--stamp-blueprint-bg)';
          slot3.style.borderColor = 'var(--stamp-blueprint)';
          feedback.innerHTML = "📥 <strong>CACHE MISS (28 ms):</strong> 'teclado' no estaba en caché. Se ejecutó la búsqueda completa y se insertó en la caché desalojando el elemento más antiguo (LRU).";
        }});
      }}

      if (btnInvalidate && feedback) {{
        btnInvalidate.addEventListener('click', () => {{
          if (slot1) slot1.textContent = 'Slot 1: [Vacío]';
          if (slot2) slot2.textContent = 'Slot 2: [Vacío]';
          if (slot3) slot3.textContent = 'Slot 3: [Vacío]';
          [slot1, slot2, slot3].forEach(s => {{
            if (s) {{
              s.style.background = 'var(--stamp-crimson-bg)';
              s.style.borderColor = 'var(--stamp-crimson-border)';
            }}
          }});
          feedback.innerHTML = "🛡️ <strong>INVALIDACIÓN REACTIVA ATÓMICA:</strong> Se despachó un pedido y mutó el stock disponible. El motor purgó automáticamente la caché para garantizar 100% de consistencia transaccional y cero lecturas obsoletas.";
        }});
      }}
    }}

    // 6. Diapositiva 07: Auditoría Interactiva de Sobrecarga IPC
    if (slideId === 7) {{
      const ipcButtons = slideContainer.querySelectorAll('.ipc-seg');
      const ipcDetail = document.getElementById('ipc-detail-box');
      const explanations = {{
        'spawn': "<strong>Spawn de Procesos en Windows (25% - ~210 ms):</strong> A diferencia del <code>fork()</code> rápido en Linux, Windows debe instanciar un nuevo ejecutable de Python completo con sus DLLs y módulos desde disco para cada worker.",
        'pickle': "<strong>Serialización Pickle (38% - ~320 ms):</strong> Transferir 10.000 objetos <code>Producto</code> y 2.000 pedidos requirió serializar estructuras complejas a bytes y reconstruirlas en la memoria del subproceso.",
        'pipe': "<strong>Tuberías IPC del Sistema Operativo (32% - ~270 ms):</strong> La transmisión de megabytes de datos serializados a través de pipes del kernel introdujo latencias de cambio de contexto y sincronización.",
        'calc': "<strong>Cómputo Puro en RAM (Solo 5% - ~48 ms):</strong> El tiempo real de validación lógica fue mínimo. La sobrecarga de coordinación costó 28 veces más que el cálculo en sí, confirmando la Ley de Amdahl."
      }};

      ipcButtons.forEach(btn => {{
        btn.addEventListener('click', () => {{
          const key = btn.getAttribute('data-ipc');
          if (ipcDetail && explanations[key]) {{
            ipcDetail.innerHTML = explanations[key];
          }}
        }});
      }});
    }}

    // 7. Diapositiva 09: Animación de Barras de Rendimiento
    if (slideId === 9) {{
      animateSpeedupBars();
    }}

    // 8. Diapositiva 10: Interacción con Tarjetas de Características
    if (slideId === 10) {{
      const featureItems = slideContainer.querySelectorAll('.feature-item');
      featureItems.forEach(item => {{
        item.addEventListener('click', () => {{
          featureItems.forEach(i => i.classList.remove('active'));
          item.classList.add('active');
        }});
      }});
    }}
  }}

  // ==========================================================================
  // MOTOR DEL SIMULADOR DE BÚSQUEDA (SLIDE 04)
  // ==========================================================================
  function resetSimUI() {{
    const baseProgress = document.getElementById('sim-base-progress');
    const optProgress = document.getElementById('sim-opt-progress');
    const baseOps = document.getElementById('sim-base-ops');
    const optOps = document.getElementById('sim-opt-ops');
    const baseTime = document.getElementById('sim-base-time');
    const optTime = document.getElementById('sim-opt-time');
    const baseStatus = document.getElementById('sim-base-status');
    const optStatus = document.getElementById('sim-opt-status');
    const summaryBox = document.getElementById('sim-summary-box');

    if (baseProgress) baseProgress.style.transform = 'scaleX(0)';
    if (optProgress) optProgress.style.transform = 'scaleX(0)';
    if (baseOps) baseOps.textContent = '0';
    if (optOps) optOps.textContent = '0';
    if (baseTime) baseTime.textContent = '0.00 ms';
    if (optTime) optTime.textContent = '0.00 ms';
    if (baseStatus) {{ baseStatus.textContent = 'Listo'; baseStatus.className = 'lane-status'; }}
    if (optStatus) {{ optStatus.textContent = 'Listo'; optStatus.className = 'lane-status'; }}
    if (summaryBox) {{
      summaryBox.innerHTML = "Presiona 'Simular Búsqueda Comparativa' para observar en tiempo real la diferencia algorítmica entre recorrer secuencialmente una lista versus indexar directamente con función hash.";
    }}
  }}

  function runSearchSimulation() {{
    if (simRunning) return;
    simRunning = true;

    const btnRun = document.getElementById('btn-run-sim');
    if (btnRun) btnRun.disabled = true;

    const catalogSelect = document.getElementById('sim-catalog-size');
    const n = catalogSelect ? parseInt(catalogSelect.value, 10) : 10000;
    const targetIdx = Math.floor(n * 0.842);

    const baseProgress = document.getElementById('sim-base-progress');
    const optProgress = document.getElementById('sim-opt-progress');
    const baseOps = document.getElementById('sim-base-ops');
    const optOps = document.getElementById('sim-opt-ops');
    const baseTime = document.getElementById('sim-base-time');
    const optTime = document.getElementById('sim-opt-time');
    const baseStatus = document.getElementById('sim-base-status');
    const optStatus = document.getElementById('sim-opt-status');
    const summaryBox = document.getElementById('sim-summary-box');

    // 1. Optimizada O(1): Ejecución Instantánea
    if (optStatus) {{ optStatus.textContent = 'Cálculo Hash Directo O(1)'; optStatus.className = 'lane-status completed'; }}
    if (optProgress) optProgress.style.transform = 'scaleX(1)';
    if (optOps) optOps.textContent = '1 operación';
    if (optTime) optTime.textContent = '0.001 ms';

    // 2. Baseline O(n): Simulación Animada de Escaneo
    if (baseStatus) {{ baseStatus.textContent = 'Escaneando lista secuencialmente...'; baseStatus.className = 'lane-status running'; }}
    let currentStep = 0;
    const totalSteps = 40;
    const stepIncrement = Math.floor(targetIdx / totalSteps);
    const intervalMs = 25;

    const scanInterval = setInterval(() => {{
      currentStep++;
      const currentOps = Math.min(targetIdx, currentStep * stepIncrement);
      const ratio = currentOps / n;

      if (baseProgress) baseProgress.style.transform = `scaleX(${{ratio}})`;
      if (baseOps) baseOps.textContent = `${{currentOps.toLocaleString('es-AR')}} ops`;
      const simulatedMs = (currentOps * 0.00005).toFixed(2);
      if (baseTime) baseTime.textContent = `${{simulatedMs}} ms`;

      if (currentStep >= totalSteps) {{
        clearInterval(scanInterval);
        if (baseOps) baseOps.textContent = `${{targetIdx.toLocaleString('es-AR')}} ops`;
        if (baseTime) baseTime.textContent = `${{(targetIdx * 0.00005).toFixed(2)}} ms`;
        if (baseStatus) {{ baseStatus.textContent = `Encontrado en pos. ${{targetIdx.toLocaleString('es-AR')}}`; baseStatus.className = 'lane-status completed'; }}

        const speedup = Math.round(targetIdx / 1);
        if (summaryBox) {{
          summaryBox.innerHTML = `<strong>Resultado Demostrado:</strong> El escaneo lineal Baseline recorrió secuencialmente <strong>${{targetIdx.toLocaleString('es-AR')}} elementos</strong> en memoria, mientras que la tabla Hash Optimizada saltó al registro en <strong>1 sola operación indexada</strong> (aceleración teórica de <strong>${{speedup.toLocaleString('es-AR')}}x</strong> en esta búsqueda).`;
        }}

        simRunning = false;
        if (btnRun) btnRun.disabled = false;
      }}
    }}, intervalMs);
  }}

  // Animación de Barras en Diapositiva 09 (Hardware-accelerated)
  function animateSpeedupBars() {{
    const fills = slideContainer.querySelectorAll('.bar-fill');
    fills.forEach(fill => {{
      fill.style.transform = 'scaleX(0)';
      requestAnimationFrame(() => {{
        setTimeout(() => {{
          fill.style.transform = 'scaleX(1)';
        }}, 40);
      }});
    }});
  }}

  // ==========================================================================
  // NAVEGACIÓN Y CONTROLADORES
  // ==========================================================================
  function nextSlide() {{
    if (currentIndex < slides.length - 1) {{
      renderSlide(currentIndex + 1, 'right');
    }}
  }}

  function prevSlide() {{
    if (currentIndex > 0) {{
      renderSlide(currentIndex - 1, 'left');
    }}
  }}

  function toggleFullscreen() {{
    if (!document.fullscreenElement) {{
      document.documentElement.requestFullscreen().catch(err => {{
        console.warn(`Error al intentar pantalla completa: ${{err.message}}`);
      }});
    }} else {{
      if (document.exitFullscreen) {{
        document.exitFullscreen();
      }}
    }}
  }}

  function toggleNotes() {{
    speakerModal.classList.toggle('active');
  }}

  function toggleShortcuts() {{
    shortcutsModal.classList.toggle('active');
  }}

  // Cronómetro de Exposición
  function formatTime(totalSeconds) {{
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${{mins.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}`;
  }}

  function toggleTimer() {{
    if (timerRunning) {{
      clearInterval(timerInterval);
      timerRunning = false;
      btnTimer.classList.remove('running');
      btnTimer.title = "Iniciar cronómetro (Atajo: T)";
    }} else {{
      timerRunning = true;
      btnTimer.classList.add('running');
      btnTimer.title = "Pausar cronómetro (Atajo: T)";
      timerInterval = setInterval(() => {{
        if (timerSeconds > 0) {{
          timerSeconds--;
          timerDisplay.textContent = formatTime(timerSeconds);

          if (timerSeconds <= 60) {{
            btnTimer.classList.remove('warning');
            btnTimer.classList.add('danger');
          }} else if (timerSeconds <= 180) {{
            btnTimer.classList.add('warning');
          }}
        }} else {{
          clearInterval(timerInterval);
          timerRunning = false;
          btnTimer.classList.remove('running');
          btnTimer.classList.remove('warning');
          btnTimer.classList.add('danger');
        }}
      }}, 1000);
    }}
  }}

  // Event Listeners de Controles UI
  btnNext.addEventListener('click', nextSlide);
  btnPrev.addEventListener('click', prevSlide);
  selectSlide.addEventListener('change', (e) => {{
    const targetIdx = parseInt(e.target.value, 10);
    const dir = targetIdx > currentIndex ? 'right' : 'left';
    renderSlide(targetIdx, dir);
  }});
  btnFullscreen.addEventListener('click', toggleFullscreen);
  btnNotes.addEventListener('click', toggleNotes);
  btnCloseNotes.addEventListener('click', toggleNotes);
  btnShortcuts.addEventListener('click', toggleShortcuts);
  btnCloseShortcuts.addEventListener('click', toggleShortcuts);
  btnTimer.addEventListener('click', toggleTimer);

  // Atajos de Teclado Profesionales para la Defensa Oral
  window.addEventListener('keydown', (e) => {{
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT' || e.target.tagName === 'TEXTAREA') {{
      return;
    }}

    switch (e.key) {{
      case 'ArrowRight':
      case ' ':
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
        e.preventDefault();
        toggleFullscreen();
        break;
      case 'n':
      case 'N':
        e.preventDefault();
        toggleNotes();
        break;
      case 'h':
      case 'H':
      case '?':
        e.preventDefault();
        toggleShortcuts();
        break;
      case 't':
      case 'T':
        e.preventDefault();
        toggleTimer();
        break;
      case 'Escape':
        speakerModal.classList.remove('active');
        shortcutsModal.classList.remove('active');
        break;
      case 'Home':
        e.preventDefault();
        renderSlide(0, 'left');
        break;
      case 'End':
        e.preventDefault();
        renderSlide(slides.length - 1, 'right');
        break;
      default:
        if (e.key >= '1' && e.key <= '9') {{
          const targetIndex = parseInt(e.key, 10) - 1;
          if (targetIndex < slides.length) {{
            const dir = targetIndex > currentIndex ? 'right' : 'left';
            renderSlide(targetIndex, dir);
          }}
        }}
        break;
    }}
  }});

  // Inicialización
  cargarSlides();
}})();
"""

with open('docs/presentation/app.js', 'w', encoding='utf-8') as f:
    f.write(js_template)

print("Successfully generated docs/presentation/app.js!")
