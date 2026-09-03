"""Pantalla de Productos Más Solicitados (Top-N)."""

from __future__ import annotations
import time
import flet as ft
from src.motor.motor_inventario import MotorInventario
from src.ranking.top_productos import calcular_top_solicitados_heap, calcular_top_solicitados_lineal
from src.ui.tema import (
    COLOR_BORDE,
    COLOR_EXITO,
    COLOR_PRIMARIO,
    COLOR_SECUNDARIO,
    COLOR_TARJETA,
    COLOR_TEXTO_MUTED,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    actualizar_control,
    alineacion_center,
    borde_all,
    padding_symmetric,
    crear_tarjeta_kpi,
)


class PantallaTopProductos(ft.Container):
    """Vista comparativa de Top-N: Min-Heap O(N log k) vs Ordenamiento Total O(N log N)."""

    def __init__(self, motor: MotorInventario, on_actualizar_panel, notificar) -> None:
        super().__init__()
        self.motor = motor
        self.on_actualizar_panel = on_actualizar_panel
        self.notificar = notificar
        self.expand = True
        self.padding = 24

        # Selector de método
        self.dropdown_metodo = ft.Dropdown(
            label="Algoritmo de selección",
            options=[
                ft.dropdown.Option("heap", "Min-Heap con heapq.nlargest (O(N log k))"),
                ft.dropdown.Option("sort", "Ordenamiento Completo con sort (O(N log N))"),
            ],
            value="heap" if self.motor.es_optimizado else "sort",
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_PRIMARIO,
            color=COLOR_TEXTO_PRIMARIO,
            width=380,
            on_select=lambda _: self._ejecutar_calculo(),
        )

        # Selector de k
        self.dropdown_k = ft.Dropdown(
            label="Valor de k",
            options=[
                ft.dropdown.Option("3", "Top 3"),
                ft.dropdown.Option("5", "Top 5"),
                ft.dropdown.Option("10", "Top 10"),
                ft.dropdown.Option("20", "Top 20"),
            ],
            value="5",
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_PRIMARIO,
            color=COLOR_TEXTO_PRIMARIO,
            width=120,
            on_select=lambda _: self._ejecutar_calculo(),
        )

        self.btn_calcular = ft.FilledButton(
            "Recalcular Top-N",
            icon=ft.Icons.LEADERBOARD_ROUNDED,
            style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color="#FFFFFF"),
            on_click=lambda _: self._ejecutar_calculo(),
        )

        self.fila_kpis = ft.Row(spacing=12)
        self.col_ranking = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        self._construir_interfaz()
        self._ejecutar_calculo()

    def _construir_interfaz(self) -> None:
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Ranking de Productos Más Solicitados (Top-N)", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                ft.Text("Comparación algorítmica: Heap O(N log k) acotado en memoria vs. Ordenamiento global O(N log N)", size=13, color=COLOR_TEXTO_SECUNDARIO),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        self.btn_calcular,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=16, color=COLOR_BORDE),
                # Panel de control de parámetros
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.dropdown_metodo,
                            self.dropdown_k,
                        ],
                        spacing=16,
                    ),
                    padding=12,
                    bgcolor=COLOR_TARJETA,
                    border_radius=8,
                    border=borde_all(1, COLOR_BORDE),
                ),
                self.fila_kpis,
                ft.Container(height=4),
                ft.Text("Productos con Mayor Demanda Acumulada", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                self.col_ranking,
            ],
            spacing=12,
            expand=True,
        )

    def _ejecutar_calculo(self):
        k = int(self.dropdown_k.value or "5")
        metodo = self.dropdown_metodo.value or "heap"

        inicio = time.perf_counter()
        if metodo == "heap":
            top = calcular_top_solicitados_heap(self.motor.pedidos, self.motor.catalogo, k=k)
        else:
            top = calcular_top_solicitados_lineal(self.motor.pedidos, self.motor.catalogo, k=k)
        duracion_ms = (time.perf_counter() - inicio) * 1000.0

        total_uds_lote = sum(l.cantidad for p in self.motor.pedidos for l in p.lineas)

        # Actualizar KPIs
        self.fila_kpis.controls = [
            crear_tarjeta_kpi("Algoritmo Activo", "Min-Heap" if metodo == "heap" else "Sort Completo", f"Complejidad: O(N log {'k' if metodo == 'heap' else 'N'})", ft.Icons.ACCOUNT_TREE, COLOR_PRIMARY if metodo == "heap" else COLOR_SECONDARY),
            crear_tarjeta_kpi("Posiciones (k)", str(k), "Artículos seleccionados", ft.Icons.FORMAT_LIST_NUMBERED, COLOR_PRIMARY),
            crear_tarjeta_kpi("Tiempo de Cómputo", f"{duracion_ms:.3f} ms", f"{len(self.motor.pedidos)} pedidos evaluados", ft.Icons.SPEED, COLOR_EXITO),
        ]

        # Renderizar ranking
        items = []
        for pos, (prod, cantidad) in enumerate(top, start=1):
            pct = (cantidad / total_uds_lote * 100.0) if total_uds_lote > 0 else 0.0
            color_pos = COLOR_PRIMARIO if pos == 1 else (COLOR_SECUNDARIO if pos <= 3 else COLOR_TEXTO_SECUNDARIO)

            items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(f"#{pos}", size=18, weight=ft.FontWeight.BOLD, color=color_pos),
                                width=45,
                                alignment=alineacion_center(),
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(prod.nombre, size=15, weight=ft.FontWeight.W_600, color=COLOR_TEXTO_PRIMARIO),
                                    ft.Text(f"Categoría: {prod.categoria} | Stock disponible: {prod.stock} uds", size=12, color=COLOR_TEXTO_MUTED),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(f"{cantidad} uds demandadas", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                    ft.Text(f"{pct:.1f}% de la demanda total", size=12, color=COLOR_EXITO),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                                spacing=2,
                            ),
                        ],
                    ),
                    padding=padding_symmetric(horizontal=16, vertical=12),
                    bgcolor=COLOR_TARJETA,
                    border_radius=8,
                    border=borde_all(1, COLOR_BORDE),
                )
            )

        if not top:
            items.append(
                ft.Text("No hay pedidos registrados para calcular la demanda.", size=13, color=COLOR_TEXTO_MUTED)
            )

        self.col_ranking.controls = items
        self.on_actualizar_panel(
            dataset="activo",
            n_productos=len(self.motor.catalogo),
            n_pedidos=len(self.motor.pedidos),
            estrategia=self.motor.estrategia,
            tiempo_ms=duracion_ms,
            resultado_negocio=f"Top-{k} calculado con {metodo.upper()} en {duracion_ms:.3f} ms",
        )
        actualizar_control(self)


COLOR_PRIMARY = COLOR_PRIMARIO
COLOR_SECONDARY = COLOR_SECUNDARIO
