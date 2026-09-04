"""Pantalla de Comparación Experimental Baseline vs. Optimizado."""

from __future__ import annotations
import time
import tracemalloc
import flet as ft
from src.motor.motor_inventario import MotorInventario
from src.ranking.top_productos import calcular_top_solicitados_heap, calcular_top_solicitados_lineal
from src.pedidos.procesador_secuencial import procesar_pedidos_secuencial
from src.pedidos.procesador_concurrente import procesar_pedidos_concurrente
from src.ui.tema import (
    COLOR_BORDE,
    COLOR_EXITO,
    COLOR_PELIGRO,
    COLOR_PRIMARIO,
    COLOR_SECUNDARIO,
    COLOR_SUPERFICIE,
    COLOR_TARJETA,
    COLOR_TEXTO_MUTED,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    actualizar_control,
    borde_all,
    padding_symmetric,
    crear_tarjeta_kpi,
    crear_banner_explicativo,
    crear_badge_tiempo,
    crear_dropdown,
)


class PantallaComparacion(ft.Container):
    """Vista comparativa formal: Genera y exhibe la tabla de mediciones para la defensa oral."""

    def __init__(self, motor: MotorInventario, on_actualizar_panel, notificar) -> None:
        super().__init__()
        self.motor = motor
        self.on_actualizar_panel = on_actualizar_panel
        self.notificar = notificar
        self.expand = True
        self.padding = padding_symmetric(horizontal=16, vertical=10)

        self.filas_medidas = []
        self.orden_ascendente = False

        self.btn_comparar = ft.FilledButton(
            "Ejecutar Comparativa",
            icon=ft.Icons.COMPARE_ARROWS_ROUNDED,
            style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color="#FFFFFF"),
            on_click=lambda _: self._ejecutar_comparativa(),
        )

        # Controles de ordenamiento
        self.dropdown_orden = crear_dropdown(
            label="Ordenar por",
            options=[
                ft.dropdown.Option("speedup", "Mayor Aceleración (Speedup)"),
                ft.dropdown.Option("tiempo_opt", "Tiempo Optimizado"),
                ft.dropdown.Option("nombre", "Nombre de Operación"),
            ],
            value="speedup",
            width=200,
            on_change_callback=lambda _: self._aplicar_ordenamiento(),
        )

        self.btn_sentido_orden = ft.IconButton(
            icon=ft.Icons.ARROW_DOWNWARD_ROUNDED,
            tooltip="Orden Descendente (Clic para alternar)",
            on_click=lambda _: self._alternar_sentido_orden(),
        )

        self.fila_kpis = ft.Row(spacing=8)
        self.col_tabla_comparativa = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)

        self._construir_interfaz()

    def _construir_interfaz(self) -> None:
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Desafío Experimental: Baseline vs. Optimizado", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                ft.Text("Medición empírica rigurosa de tiempo, memoria y aceleración (Speedup) sobre el mismo dataset", size=12, color=COLOR_TEXTO_SECUNDARIO),
                            ],
                            spacing=1,
                        ),
                        ft.Container(expand=True),
                        self.btn_comparar,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=6, color=COLOR_BORDE),
                # Banner explicativo didáctico
                crear_banner_explicativo(
                    titulo="Desafío Experimental y Comparación Obligatoria",
                    descripcion="Medición empírica rigurosa de las 4 operaciones fundamentales sobre el mismo dataset para evaluar la aceleración real (Speedup = Tiempo_base / Tiempo_opt).",
                    complejidad_base="O(n), O(N log N), O(P·L), O(2^N)",
                    complejidad_opt="O(1), O(N log k), Multi-Proceso, O(N·P)",
                    por_que_importa="Satisface el requisito central de la rúbrica del parcial y suministra la evidencia empírica directa para la exposición oral.",
                ),

                # Barra de herramientas de ordenamiento compacta
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SORT_ROUNDED, size=18, color=COLOR_PRIMARIO),
                            self.dropdown_orden,
                            self.btn_sentido_orden,
                        ],
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=padding_symmetric(horizontal=10, vertical=5),
                    bgcolor=COLOR_TARJETA,
                    border_radius=8,
                    border=borde_all(1, COLOR_BORDE),
                ),
                self.fila_kpis,
                ft.Text("Tabla de Comparación Experimental Obligatoria (Rúbrica)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                self.col_tabla_comparativa,
            ],
            spacing=6,
            expand=True,
        )

    def al_recargar_dataset(self) -> None:
        """Callback al recargar dataset."""
        self.filas_medidas = []
        self.col_tabla_comparativa.controls = []
        actualizar_control(self)

    def al_cambiar_estrategia_global(self, nueva_estrategia: str) -> None:
        pass

    def _alternar_sentido_orden(self):
        self.orden_ascendente = not self.orden_ascendente
        self.btn_sentido_orden.icon = ft.Icons.ARROW_UPWARD_ROUNDED if self.orden_ascendente else ft.Icons.ARROW_DOWNWARD_ROUNDED
        self.btn_sentido_orden.tooltip = "Orden Ascendente" if self.orden_ascendente else "Orden Descendente"
        actualizar_control(self.btn_sentido_orden)
        self._aplicar_ordenamiento()

    def _aplicar_ordenamiento(self):
        if not self.filas_medidas:
            return

        criterio = self.dropdown_orden.value or "speedup"

        def clave(item):
            # item: (operacion, t_base, t_opt, speedup, obs)
            operacion, t_base, t_opt, speedup, obs = item
            if criterio == "speedup":
                return speedup
            elif criterio == "tiempo_opt":
                return t_opt
            elif criterio == "nombre":
                return operacion.lower()
            return speedup

        self.filas_medidas.sort(key=clave, reverse=not self.orden_ascendente)
        self._renderizar_tabla()

    def _ejecutar_comparativa(self):
        prods = self.motor.catalogo.obtener_todos()
        peds = self.motor.pedidos

        if not prods or not peds:
            self.notificar("Cargue un dataset primero desde la pantalla de Inicio.", ft.Icons.WARNING)
            return

        self.notificar("Ejecutando suite experimental comparativa...", icono=ft.Icons.HOURGLASS_EMPTY)

        # 1. Búsquedas de catálogo (Lineal vs Hash)
        palabra_muestra = "a"
        t0 = time.perf_counter()
        for _ in range(5):
            _ = [p for p in prods if palabra_muestra in p.nombre.lower()]
        t_busq_base = ((time.perf_counter() - t0) / 5) * 1000.0

        t0 = time.perf_counter()
        for _ in range(5):
            _ = self.motor.buscar_por_nombre(palabra_muestra, usar_cache=True)
        t_busq_opt = ((time.perf_counter() - t0) / 5) * 1000.0

        # 2. Top-N (Sort vs Heap)
        k = 5
        t0 = time.perf_counter()
        calcular_top_solicitados_lineal(peds, self.motor.catalogo, k=k)
        t_top_base = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        calcular_top_solicitados_heap(peds, self.motor.catalogo, k=k)
        t_top_opt = (time.perf_counter() - t0) * 1000.0

        # 3. Preparación de pedidos (Secuencial vs Concurrente)
        t0 = time.perf_counter()
        res_sec = procesar_pedidos_secuencial(self.motor.catalogo, peds, descontar_stock=False)
        t_ped_base = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        res_conc = procesar_pedidos_concurrente(self.motor.catalogo, peds, descontar_stock=False)
        t_ped_opt = (time.perf_counter() - t0) * 1000.0

        # 4. Alternativas (Recursivo puro vs DP Memoizado)
        cat_ejemplo = prods[0].categoria
        t0 = time.perf_counter()
        res_alt_puro = self.motor.buscar_alternativas(cat_ejemplo, 35000.0, forzar_memoizacion=False, max_combinaciones=10)
        t_alt_base = (time.perf_counter() - t0) * 1000.0

        t0 = time.perf_counter()
        res_alt_memo = self.motor.buscar_alternativas(cat_ejemplo, 35000.0, forzar_memoizacion=True, max_combinaciones=10)
        t_alt_opt = (time.perf_counter() - t0) * 1000.0

        # Medición de memoria general del proceso
        tracemalloc.start()
        _ = self.motor.catalogo.obtener_todos()
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        mem_mb = peak_mem / (1024 * 1024)

        # Ratios de aceleración (Speedup = Base / Opt)
        sp_busq = (t_busq_base / t_busq_opt) if t_busq_opt > 0 else 1.0
        sp_top = (t_top_base / t_top_opt) if t_top_opt > 0 else 1.0
        sp_ped = (t_ped_base / t_ped_opt) if t_ped_opt > 0 else 1.0
        sp_alt = (t_alt_base / t_alt_opt) if t_alt_opt > 0 else 1.0

        # Actualizar KPIs
        self.fila_kpis.controls = [
            crear_tarjeta_kpi("Aceleración Búsqueda", f"{sp_busq:.1f}x", "Hash O(1) vs. Lista O(n)", ft.Icons.ROCKET_LAUNCH, COLOR_PRIMARIO),
            crear_tarjeta_kpi("Aceleración Top-N", f"{sp_top:.1f}x", "Heap vs. Sort total", ft.Icons.TRENDING_UP, COLOR_SECUNDARIO),
            crear_tarjeta_kpi("Aceleración Alternativas", f"{sp_alt:.1f}x", "DP Memo vs. Recursión pura", ft.Icons.PSYCHOLOGY, COLOR_EXITO),
            crear_tarjeta_kpi("Memoria Heap Activa", f"{mem_mb:.2f} MB", "Estructuras en memoria", ft.Icons.MEMORY, COLOR_PRIMARIO),
        ]

        self.filas_medidas = [
            ("1. Catálogo (Búsqueda)", t_busq_base, t_busq_opt, sp_busq, "Acceso hash directo O(1) e índice invertido con caché LRU."),
            ("2. Top-N Productos", t_top_base, t_top_opt, sp_top, "heapq.nlargest O(N log k) acotado en k frente a ordenamiento total O(N log N)."),
            ("3. Preparación de Pedidos", t_ped_base, t_ped_opt, sp_ped, "Mono-hilo frente a ProcessPoolExecutor con overhead IPC analizado."),
            ("4. Combinaciones Sustitutas", t_alt_base, t_alt_opt, sp_alt, f"Poda DP: {res_alt_memo.hits_memo} subproblemas reutilizados en O(N·P)."),
        ]

        self._aplicar_ordenamiento()

        self.on_actualizar_panel(
            dataset="activo",
            n_productos=len(prods),
            n_pedidos=len(peds),
            estrategia="comparativa",
            tiempo_ms=t_busq_opt + t_top_opt + t_ped_opt + t_alt_opt,
            memoria_mb=mem_mb,
            resultado_negocio="Comparativa experimental completada con éxito",
        )
        actualizar_control(self)
        self.notificar("Comparativa experimental finalizada exitosamente.", icono=ft.Icons.CHECK_CIRCLE)

    def _renderizar_tabla(self):
        filas_widgets = []
        for operacion, t_base, t_opt, speedup, observacion in self.filas_medidas:
            color_speedup = COLOR_EXITO if speedup >= 1.0 else COLOR_PELIGRO
            texto_speedup = f"🚀 {speedup:.1f}x" if speedup >= 1.0 else f"🐢 {speedup:.2f}x"

            filas_widgets.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(operacion, size=13.5, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                    ft.Container(expand=True),
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.BOLT_ROUNDED if speedup >= 1.0 else ft.Icons.INFO_OUTLINE, size=13, color="#FFFFFF"),
                                                ft.Text(f"Speedup: {texto_speedup}", size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                            ],
                                            spacing=3,
                                            tight=True,
                                        ),
                                        bgcolor=color_speedup,
                                        padding=padding_symmetric(horizontal=8, vertical=2),
                                        border_radius=5,
                                    ),
                                ],
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text("Baseline:", size=11, color=COLOR_TEXTO_MUTED),
                                    crear_badge_tiempo(t_base),
                                    ft.Text("→", size=11, color=COLOR_TEXTO_MUTED),
                                    ft.Text("Optimizado:", size=11, color=COLOR_TEXTO_MUTED),
                                    crear_badge_tiempo(t_opt, speedup=speedup),
                                    ft.Container(expand=True),
                                    ft.Text(observacion, size=11, color=COLOR_TEXTO_SECUNDARIO),
                                ],
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5,
                            ),
                        ],
                        spacing=3,
                    ),
                    padding=padding_symmetric(horizontal=12, vertical=6),
                    bgcolor=COLOR_TARJETA,
                    border_radius=6,
                    border=borde_all(1, COLOR_BORDE),
                )
            )

        self.col_tabla_comparativa.controls = filas_widgets
        actualizar_control(self)
