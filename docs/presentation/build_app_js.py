import json
import os

with open('docs/presentation/slides.json', 'r', encoding='utf-8') as f:
    slides_data = json.load(f)

fallback_slides_json = json.dumps(slides_data['slides'], ensure_ascii=False, indent=2)

js_template = f"""/**
 * ==========================================================================
 * APLICACIÓN DE PRESENTACIÓN INTERACTIVA
 * Programación Eficiente — Primer Parcial (Opción 6) | Universidad Blas Pascal
 * ==========================================================================
 */

(function () {{
  'use strict';

  // Fallback de datos embebido sincronizado con slides.json (para ejecucion offline y file://)
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

  // Carga de diapositivas asincrona con fallback robusto
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

  // Renderizado de Diapositiva con Soporte de Direccion y Animaciones
  function renderSlide(index, direction) {{
    if (index < 0 || index >= slides.length) return;
    const prevIndex = currentIndex;
    currentIndex = index;
    const slide = slides[currentIndex];

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

    // Actualizar Controles de Navegacion
    slideCounter.textContent = `${{currentIndex + 1}} / ${{slides.length}}`;
    selectSlide.value = currentIndex;
    const progressPercent = ((currentIndex + 1) / slides.length) * 100;
    progressBar.style.width = `${{progressPercent}}%`;

    btnPrev.disabled = (currentIndex === 0);
    btnNext.disabled = (currentIndex === slides.length - 1);

    // Actualizar Notas del Orador
    speakerText.textContent = slide.notes || "No hay notas adicionales para esta diapositiva.";

    // Inicializar comportamientos interactivos especificos de la diapositiva
    initSlideInteractiveBehaviors(slide.id);
  }}

  // Comportamientos Interactivos por Diapositiva
  function initSlideInteractiveBehaviors(slideId) {{
    // 1. Manejo generico de Pestañas (Tabs)
    const tabButtons = slideContainer.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {{
      btn.addEventListener('click', (e) => {{
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

    // 2. Diapositiva 04: Simulador Interactivo O(n) vs O(1)
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

    // 3. Diapositiva 09: Animación de Barras de Rendimiento
    if (slideId === 9) {{
      animateSpeedupBars();
    }}

    // 4. Diapositiva 10: Interaccion con Caracteristicas
    if (slideId === 10) {{
      const featureItems = slideContainer.querySelectorAll('.feature-item');
      featureItems.forEach(item => {{
        item.addEventListener('click', () => {{
          featureItems.forEach(i => i.style.borderColor = 'var(--border-color)');
          item.style.borderColor = 'var(--accent-cyan)';
          item.style.boxShadow = '0 0 20px rgba(56, 189, 248, 0.3)';
        }});
      }});
    }}
  }}

  // Motor del Simulador de Busqueda (Slide 4)
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

    if (baseProgress) baseProgress.style.width = '0%';
    if (optProgress) optProgress.style.width = '0%';
    if (baseOps) baseOps.textContent = '0';
    if (optOps) optOps.textContent = '0';
    if (baseTime) baseTime.textContent = '0.00 ms';
    if (optTime) optTime.textContent = '0.00 ms';
    if (baseStatus) {{ baseStatus.textContent = 'Listo'; baseStatus.style.color = 'var(--text-muted)'; }}
    if (optStatus) {{ optStatus.textContent = 'Listo'; optStatus.style.color = 'var(--text-muted)'; }}
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
    if (optStatus) {{ optStatus.textContent = 'Cálculo Hash Directo O(1)...'; optStatus.style.color = 'var(--accent-emerald)'; }}
    if (optProgress) optProgress.style.width = '100%';
    if (optOps) optOps.textContent = '1 operación';
    if (optTime) optTime.textContent = '0.001 ms';
    if (optStatus) {{ optStatus.textContent = 'Encontrado (1 acceso)'; optStatus.style.color = 'var(--accent-emerald)'; }}

    // 2. Baseline O(n): Simulación Animada de Escaneo
    if (baseStatus) {{ baseStatus.textContent = 'Escaneando lista secuencialmente...'; baseStatus.style.color = 'var(--accent-rose)'; }}
    let currentStep = 0;
    const totalSteps = 40;
    const stepIncrement = Math.floor(targetIdx / totalSteps);
    const intervalMs = 25;

    const scanInterval = setInterval(() => {{
      currentStep++;
      const currentOps = Math.min(targetIdx, currentStep * stepIncrement);
      const percent = (currentOps / n) * 100;

      if (baseProgress) baseProgress.style.width = `${{percent}}%`;
      if (baseOps) baseOps.textContent = `${{currentOps.toLocaleString('es-AR')}} ops`;
      const simulatedMs = (currentOps * 0.00005).toFixed(2);
      if (baseTime) baseTime.textContent = `${{simulatedMs}} ms`;

      if (currentStep >= totalSteps) {{
        clearInterval(scanInterval);
        if (baseOps) baseOps.textContent = `${{targetIdx.toLocaleString('es-AR')}} ops`;
        if (baseTime) baseTime.textContent = `${{(targetIdx * 0.00005).toFixed(2)}} ms`;
        if (baseStatus) {{ baseStatus.textContent = `Encontrado en posición ${{targetIdx.toLocaleString('es-AR')}}`; baseStatus.style.color = 'var(--accent-amber)'; }}

        const speedup = Math.round(targetIdx / 1);
        if (summaryBox) {{
          summaryBox.innerHTML = `<strong>Resultado Demostrado:</strong> El escaneo lineal Baseline recorrió secuencialmente <strong>${{targetIdx.toLocaleString('es-AR')}} elementos</strong> en memoria, mientras que la tabla Hash Optimizada saltó al registro en <strong>1 sola operación indexada</strong> (aceleración teórica de <strong>${{speedup.toLocaleString('es-AR')}}x</strong> en esta búsqueda).`;
        }}

        simRunning = false;
        if (btnRun) btnRun.disabled = false;
      }}
    }}, intervalMs);
  }}

  // Animación de Barras en Diapositiva 09
  function animateSpeedupBars() {{
    const fills = slideContainer.querySelectorAll('.bar-fill');
    fills.forEach(fill => {{
      const targetWidth = fill.style.width;
      fill.style.width = '0%';
      setTimeout(() => {{
        fill.style.width = targetWidth;
      }}, 50);
    }});
  }}

  // Navegación
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
      btnTimer.title = "Iniciar cronómetro (Atajo: T)";
    }} else {{
      timerRunning = true;
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
    // Ignorar si el usuario está interactuando con un input
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
        // Teclas numéricas 1 a 9 para saltar a diapositivas directamente
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
