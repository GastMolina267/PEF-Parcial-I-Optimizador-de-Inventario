import json
import os

with open('docs/presentation/slides.json', 'r', encoding='utf-8') as f:
    slides_data = json.load(f)

fallback_slides_json = json.dumps(slides_data['slides'], ensure_ascii=False, indent=2)

js_template = f"""/**
 * ==========================================================================
 * APLICACIÓN DE PRESENTACIÓN INTERACTIVA (MANUAL TÉCNICO 3D & PACKAGING RITUAL)
 * Programación Eficiente — Primer Parcial (Opción 6) | Universidad Blas Pascal
 * ==========================================================================
 */

(function () {{
  'use strict';

  // Fallback de datos embebido sincronizado con slides.json (para ejecución offline y file://)
  const FALLBACK_SLIDES = {fallback_slides_json};

  let slides = FALLBACK_SLIDES;
  let currentIndex = 0;
  let isBookClosed = true;
  let isPackaging = false;
  let timerInterval = null;
  let timerSeconds = 15 * 60; // 15 minutos oficiales
  let timerRunning = false;
  let simRunning = false;

  // Elementos DOM Principales
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

  // Elementos del Libro 3D y Empaquetado
  const bookCoverClosed = document.getElementById('book-cover-closed');
  const bookOpened = document.getElementById('book-opened');
  const btnOpenBook = document.getElementById('btn-open-book');
  const currentSlideCard = document.getElementById('current-slide-card');
  const stackLeft = document.getElementById('stack-left');
  const stackRight = document.getElementById('stack-right');
  const turningSheet = document.getElementById('book-turning-sheet');
  const turningShadow = document.getElementById('turning-shadow');
  const dragHandleRight = document.getElementById('drag-handle-right');
  const dragHandleLeft = document.getElementById('drag-handle-left');
  const packagingOverlay = document.getElementById('packaging-overlay');
  const boxContainer = document.getElementById('box-container');
  const miniPackedBook = document.getElementById('mini-packed-book');
  const btnReopenBook = document.getElementById('btn-reopen-book');
  const btnPackPresentation = document.getElementById('btn-pack-presentation');

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
      this.slideTheme = 1;
      this.width = 0;
      this.height = 0;
      this.dpr = Math.min(window.devicePixelRatio || 1, 2);
      this.mouse = {{ x: -1000, y: -1000, active: false }};
      this.time = 0;
      this.orbitFocus = null;
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
          length: Math.random() * 10 + 4,
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

      const startX = direction === 'left' ? this.width * 0.15 : (direction === 'right' ? this.width * 0.85 : this.width * 0.5);
      this.addRipple(startX, this.height * 0.5, this.width * 0.55, 'rgba(29, 78, 216, 0.22)');

      this.particles.forEach((p, idx) => {{
        if (this.slideTheme === 2) {{
          p.vx = (Math.random() - 0.5) * 3.2;
          p.vy = (Math.random() - 0.5) * 3.2;
        }} else if (this.slideTheme === 3) {{
          const isLeft = idx % 2 === 0;
          p.targetX = isLeft ? this.width * 0.28 : this.width * 0.72;
          p.targetY = this.height * 0.65;
        }} else if (this.slideTheme === 5) {{
          const quad = idx % 4;
          p.targetX = (quad % 2 === 0 ? 0.25 : 0.75) * this.width;
          p.targetY = (quad < 2 ? 0.35 : 0.75) * this.height;
        }} else if (this.slideTheme === 7) {{
          const stream = (idx % 3);
          p.targetY = this.height * (0.3 + stream * 0.22);
          p.vx = (stream + 1) * 1.5;
          p.vy = 0;
        }} else if (this.slideTheme === 9) {{
          p.vx = (Math.random() * 4 + 2);
          p.vy = (Math.random() - 0.5) * 0.4;
        }} else {{
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

      for (let i = this.ripples.length - 1; i >= 0; i--) {{
        const r = this.ripples[i];
        r.radius += (r.maxRadius - r.radius) * 0.07 + 0.8;
        r.alpha -= 0.008;
        if (r.alpha <= 0 || r.radius >= r.maxRadius) {{
          this.ripples.splice(i, 1);
        }}
      }}

      this.particles.forEach((p, idx) => {{
        p.angle += p.angularSpeed;

        if (this.slideTheme === 3) {{
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
          p.vx += (p.targetX - p.x) * 0.0015;
          p.vy += (p.targetY - p.y) * 0.0015;
          p.vx *= 0.94;
          p.vy *= 0.94;
        }} else if (this.slideTheme === 7 || this.slideTheme === 9) {{
          if (p.x > this.width + 20) p.x = -20;
        }} else {{
          p.vx += Math.sin(this.time * 0.5 + idx) * 0.015;
          p.vy += Math.cos(this.time * 0.5 + idx) * 0.015;
          p.vx = Math.max(-1.2, Math.min(1.2, p.vx));
          p.vy = Math.max(-1.2, Math.min(1.2, p.vy));
        }}

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

        if (p.x < -30) p.x = this.width + 30;
        if (p.x > this.width + 30) p.x = -30;
        if (p.y < -30) p.y = this.height + 30;
        if (p.y > this.height + 30) p.y = -30;
      }});
    }}

    draw() {{
      this.ctx.clearRect(0, 0, this.width, this.height);
      this.drawTopographicWaves();

      if (this.slideTheme === 6) {{
        this.drawTreeConnections();
      }}

      if (this.slideTheme === 8) {{
        this.drawScannerBar();
      }}

      this.ripples.forEach(r => {{
        this.ctx.beginPath();
        this.ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
        this.ctx.strokeStyle = r.color;
        this.ctx.lineWidth = 1.5;
        this.ctx.globalAlpha = Math.max(0, r.alpha);
        this.ctx.stroke();
      }});
      this.ctx.globalAlpha = 1;

      this.particles.forEach(p => {{
        this.ctx.save();
        this.ctx.translate(p.x, p.y);
        this.ctx.rotate(p.angle);
        this.ctx.fillStyle = `rgba(${{p.color.r}}, ${{p.color.g}}, ${{p.color.b}}, ${{p.color.a}})`;
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

  const canvasEngine = new PaperCanvasEngine(bgCanvas);

  // ==========================================================================
  // APERTURA Y CONTROL DEL LIBRO 3D
  // ==========================================================================
  function openBook() {{
    if (!isBookClosed) return;
    if (bookCoverClosed) {{
      bookCoverClosed.classList.add('opening');
    }}
    if (canvasEngine) {{
      canvasEngine.addRipple(window.innerWidth * 0.4, window.innerHeight * 0.5, 400, 'rgba(194, 65, 12, 0.3)');
    }}

    setTimeout(() => {{
      if (bookCoverClosed) bookCoverClosed.style.display = 'none';
      if (bookOpened) bookOpened.style.display = 'flex';
      isBookClosed = false;
      renderSlide(0, 'none');
    }}, 650);
  }}

  function updatePageStackDepth(index) {{
    if (!stackLeft || !stackRight) return;
    const total = slides.length - 1;
    const ratio = Math.max(0, Math.min(1, index / total));
    stackLeft.style.transform = `scaleX(${{0.2 + ratio * 1.5}})`;
    stackRight.style.transform = `scaleX(${{0.2 + (1 - ratio) * 1.5}})`;
  }}

  // ==========================================================================
  // GESTO DE ARRASTRE DE PÁGINA (CLICK & DRAG TO FLIP)
  // ==========================================================================
  let isDragging = false;
  let startX = 0;
  let currentDx = 0;

  function initDragToFlip() {{
    if (!bookOpened || !turningSheet) return;

    const handlePointerDown = (e) => {{
      if (isBookClosed || isPackaging) return;
      if (e.target.closest('button, input, select, textarea, a, .tab-btn, .ipc-seg')) return;
      isDragging = true;
      startX = e.clientX;
      currentDx = 0;
      turningSheet.style.display = 'block';
    }};

    const handlePointerMove = (e) => {{
      if (!isDragging) return;
      currentDx = e.clientX - startX;
      const stageWidth = bookOpened.offsetWidth || 1000;

      if (currentDx < 0) {{
        // Arrastre a la izquierda ➔ Pasar página siguiente
        const angle = Math.max(-180, Math.min(0, (currentDx / (stageWidth * 0.45)) * 180));
        turningSheet.style.transform = `rotateY(${{angle}}deg)`;
        if (turningShadow) turningShadow.style.opacity = `${{Math.abs(angle / 180) * 0.45}}`;
      }} else if (currentDx > 0) {{
        // Arrastre a la derecha ➔ Volver página anterior
        const angle = Math.max(0, Math.min(180, (currentDx / (stageWidth * 0.45)) * 180));
        turningSheet.style.transform = `rotateY(${{angle - 180}}deg)`;
        if (turningShadow) turningShadow.style.opacity = `${{(1 - angle / 180) * 0.45}}`;
      }}
    }};

    const handlePointerUp = () => {{
      if (!isDragging) return;
      isDragging = false;

      if (currentDx < -75 && currentIndex < slides.length - 1) {{
        turningSheet.style.transform = 'rotateY(-180deg)';
        setTimeout(() => {{
          turningSheet.style.display = 'none';
          nextSlide();
        }}, 240);
      }} else if (currentDx > 75 && currentIndex > 0) {{
        turningSheet.style.transform = 'rotateY(0deg)';
        setTimeout(() => {{
          turningSheet.style.display = 'none';
          prevSlide();
        }}, 240);
      }} else {{
        turningSheet.style.transform = 'rotateY(0deg)';
        setTimeout(() => {{
          turningSheet.style.display = 'none';
        }}, 180);
      }}
    }};

    bookOpened.addEventListener('pointerdown', handlePointerDown);
    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);

    if (dragHandleRight) {{
      dragHandleRight.addEventListener('click', nextSlide);
    }}
    if (dragHandleLeft) {{
      dragHandleLeft.addEventListener('click', prevSlide);
    }}
  }}

  // ==========================================================================
  // RITUAL CINEMÁTICO DE EMPAQUETADO EN CAJA KRAFT
  // ==========================================================================
  function startPackagingRitual() {{
    if (isPackaging) return;
    isPackaging = true;

    if (packagingOverlay) {{
      packagingOverlay.style.display = 'flex';
    }}

    if (boxContainer && miniPackedBook) {{
      boxContainer.className = 'box-container';
      miniPackedBook.className = 'mini-packed-book';

      // 1. Descenso del manual dentro de la caja (400ms)
      setTimeout(() => {{
        miniPackedBook.classList.add('inserted');
      }}, 400);

      // 2. Plegado de solapas (1100ms)
      setTimeout(() => {{
        boxContainer.classList.add('closing-flaps');
      }}, 1100);

      // 3. Sellado del cuerpo exterior (1700ms)
      setTimeout(() => {{
        boxContainer.classList.add('sealed');
      }}, 1700);

      // 4. Encintado transversal con cinta adhesiva (2200ms)
      setTimeout(() => {{
        boxContainer.classList.add('taped');
        if (canvasEngine) {{
          canvasEngine.addRipple(window.innerWidth * 0.5, window.innerHeight * 0.5, 300, 'rgba(180, 83, 9, 0.35)');
        }}
      }}, 2200);

      // 5. Estampado de la etiqueta logística oficial (2800ms)
      setTimeout(() => {{
        boxContainer.classList.add('labeled');
      }}, 2800);
    }}
  }}

  function reopenManual() {{
    if (packagingOverlay) {{
      packagingOverlay.style.display = 'none';
    }}
    isPackaging = false;
    if (isBookClosed) {{
      openBook();
    }} else {{
      renderSlide(currentIndex, 'none');
    }}
  }}

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
    initDragToFlip();
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
      pill.title = s.tag || `Página ${{idx + 1}}`;
      pill.type = 'button';
      pill.setAttribute('aria-label', `Saltar a página ${{idx + 1}}: ${{s.title}}`);
      pill.addEventListener('click', () => {{
        if (isBookClosed) openBook();
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

    if (canvasEngine) {{
      canvasEngine.onSlideChange(currentIndex, direction);
    }}

    updatePageStackDepth(currentIndex);

    currentSlideCard.innerHTML = `
      <div class="slide-header">
        <span class="slide-tag">${{slide.tag || `Página ${{currentIndex + 1}}`}}</span>
        <h2 class="slide-title">${{slide.title}}</h2>
        ${{slide.subtitle ? `<p class="slide-subtitle">${{slide.subtitle}}</p>` : ''}}
      </div>
      <div class="slide-body">
        ${{slide.content_html}}
      </div>
    `;

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

    speakerText.textContent = slide.notes || "No hay notas adicionales para esta diapositiva.";

    initSlideInteractiveBehaviors(slide.id);
  }}

  // ==========================================================================
  // COMPORTAMIENTOS INTERACTIVOS DENTRO DE LAS DIAPOSITIVAS
  // ==========================================================================
  function initSlideInteractiveBehaviors(slideId) {{
    // 1. Pestañas (Tabs)
    const tabButtons = currentSlideCard.querySelectorAll('.tab-btn');
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

    // 2. Diapositiva 03: Inspección de Arquitectura Dual
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

    // 4. Diapositiva 05: Inspector Interactivo de Estructuras
    if (slideId === 5) {{
      const structCards = currentSlideCard.querySelectorAll('.struct-card');
      const detailBox = document.getElementById('struct-detail-box');
      const structData = {{
        'list': "<strong>list en Python:</strong> Arreglo contiguo de punteros en C (<code>PyListObject</code>). Acceso indexado <code>O(1)</code> directo pero búsqueda lineal secuencial <code>O(n)</code>.",
        'dict': "<strong>dict en Python:</strong> Tabla hash compacta indexada en tiempo constante <code>O(1)</code> con resolución cuadrática de colisiones y aceleración 260x.",
        'heap': "<strong>heapq (Min-Heap):</strong> Árbol binario implícito con memoria acotada a <code>k</code> elementos, inserción <code>O(log k)</code> y cero necesidad de ordenar todo el universo.",
        'set': "<strong>set en Python:</strong> Conjunto hash puro sin punteros a valores. Verificación de pertenencia e intersección multi-criterio en <code>O(1)</code>."
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

    // 5. Diapositiva 06: Demostración de Cache LRU
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
          feedback.innerHTML = "⚡ <strong>CACHE HIT (0.01 ms):</strong> 'laptop' recuperado instantáneamente desde la tabla LRU en RAM.";
        }});
      }}

      if (btnMiss && slot3 && feedback) {{
        btnMiss.addEventListener('click', () => {{
          slot3.textContent = 'Slot 3: "teclado" [Nuevo]';
          slot3.style.background = 'var(--stamp-blueprint-bg)';
          slot3.style.borderColor = 'var(--stamp-blueprint)';
          feedback.innerHTML = "📥 <strong>CACHE MISS (28 ms):</strong> Se computó la búsqueda y se guardó en el slot más antiguo desocupado (LRU).";
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
          feedback.innerHTML = "🛡️ <strong>INVALIDACIÓN REACTIVA ATÓMICA:</strong> Stock mutado por despacho de pedidos. Purgado atómico para prevenir lecturas obsoletas.";
        }});
      }}
    }}

    // 6. Diapositiva 07: Auditoría IPC
    if (slideId === 7) {{
      const ipcButtons = currentSlideCard.querySelectorAll('.ipc-seg');
      const ipcDetail = document.getElementById('ipc-detail-box');
      const explanations = {{
        'spawn': "<strong>Spawn en Windows (25% - ~210 ms):</strong> Creación pesada de nuevos ejecutables de Python con importación completa de DLLs.",
        'pickle': "<strong>Serialización Pickle (38% - ~320 ms):</strong> Conversión a bytes de 10.000 productos y 2.000 órdenes para cruzarlas entre procesos.",
        'pipe': "<strong>Tuberías IPC del OS (32% - ~270 ms):</strong> Transferencia por pipes y sincronización del kernel de Windows.",
        'calc': "<strong>Cómputo en RAM (5% - ~48 ms):</strong> Validación real en memoria, demostrando la Ley de Amdahl."
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

    // 7. Diapositiva 09: Barras Speedup
    if (slideId === 9) {{
      animateSpeedupBars();
    }}

    // 8. Diapositiva 10: Características de la App
    if (slideId === 10) {{
      const featureItems = currentSlideCard.querySelectorAll('.feature-item');
      featureItems.forEach(item => {{
        item.addEventListener('click', () => {{
          featureItems.forEach(i => i.classList.remove('active'));
          item.classList.add('active');
        }});
      }});
    }}

    // 9. Diapositiva 11: Botón de Empaquetado
    if (slideId === 11) {{
      const btnPackSlide = document.getElementById('btn-pack-from-slide');
      if (btnPackSlide) {{
        btnPackSlide.addEventListener('click', startPackagingRitual);
      }}
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

    if (optStatus) {{ optStatus.textContent = 'Cálculo Hash Directo O(1)'; optStatus.className = 'lane-status completed'; }}
    if (optProgress) optProgress.style.transform = 'scaleX(1)';
    if (optOps) optOps.textContent = '1 operación';
    if (optTime) optTime.textContent = '0.001 ms';

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

  function animateSpeedupBars() {{
    const fills = currentSlideCard.querySelectorAll('.bar-fill');
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
    if (isBookClosed) {{
      openBook();
      return;
    }}
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
  if (btnOpenBook) btnOpenBook.addEventListener('click', openBook);
  if (bookCoverClosed) bookCoverClosed.addEventListener('click', openBook);
  if (btnReopenBook) btnReopenBook.addEventListener('click', reopenManual);
  if (btnPackPresentation) btnPackPresentation.addEventListener('click', startPackagingRitual);

  btnNext.addEventListener('click', nextSlide);
  btnPrev.addEventListener('click', prevSlide);
  selectSlide.addEventListener('change', (e) => {{
    if (isBookClosed) openBook();
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

  // Atajos de Teclado
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
      case 'p':
      case 'P':
        e.preventDefault();
        startPackagingRitual();
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
        if (isPackaging) reopenManual();
        break;
      case 'Home':
        e.preventDefault();
        if (isBookClosed) openBook();
        renderSlide(0, 'left');
        break;
      case 'End':
        e.preventDefault();
        if (isBookClosed) openBook();
        renderSlide(slides.length - 1, 'right');
        break;
      default:
        if (e.key >= '1' && e.key <= '9') {{
          const targetIndex = parseInt(e.key, 10) - 1;
          if (targetIndex < slides.length) {{
            if (isBookClosed) openBook();
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

print("Successfully generated docs/presentation/app.js with 3D Book and Packaging ritual!")
