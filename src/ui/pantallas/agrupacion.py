"""Pantalla de Agrupación de Pedidos y Picking Consolidado (Batch Picking)."""

from __future__ import annotations
import time
import flet as ft
from src.motor.motor_inventario import MotorInventario
from src.ui.tema import (
    COLOR_BORDE,
    COLOR_EXITO,
    COLOR_PELIGRO,
    COLOR_PRIMARIO,
    COLOR_SECUNDARIO,
    COLOR_TARJETA,
    COLOR_TEXTO_MUTED,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    actualizar_control,
    borde_all,
    padding_symmetric,
    crear_tarjeta_kpi,
)


class PantallaAgrupacion(ft.Container):
    """Vista de consolidación de pedidos en una única lista de picking en tiempo O(L)."""

    def __init__(self, motor: MotorInventario, on_actualizar_panel, notificar) -> None:
        super().__init__()
        self.motor = motor
        self.on_actualizar_panel = on_actualizar_panel
        self.notificar = notificar
        self.expand = True
        self.padding = 24

        self.btn_agrupar = ft.FilledButton(
            "Generar Picking Consolidado",
            icon=ft.Icons.ALL_INBOX_ROUNDED,
            style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color="#FFFFFF"),
            on_click=lambda _: self._ejecutar_agrupacion(),
        )

        self.fila_kpis = ft.Row(spacing=12)
        self.col_items_picking = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        self._construir_interfaz()
        self._ejecutar_agrupacion()

    def _construir_interfaz(self) -> None:
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Batch Picking Consolidado", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                ft.Text("Fusión de demandas en una sola pasada O(L) mediante acumulación en tablas Hash", size=13, color=COLOR_TEXTO_SECUNDARIO),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        self.btn_agrupar,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=16, color=COLOR_BORDE),
                self.fila_kpis,
                ft.Container(height=4),
                ft.Text("Lista Consolidada de Artículos a Recolectar en Almacén", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                self.col_items_picking,
            ],
            spacing=12,
            expand=True,
        )

    def _ejecutar_agrupacion(self):
        inicio = time.perf_counter()
        lote = self.motor.agrupar_pedidos()
        duracion_ms = (time.perf_counter() - inicio) * 1000.0

        # Actualizar KPIs
        self.fila_kpis.controls = [
            crear_tarjeta_kpi("Pedidos Consolidados", f"{lote.total_pedidos:,}", "Órdenes agrupadas", ft.Icons.LOCAL_SHIPPING, COLOR_PRIMARIO),
            crear_tarjeta_kpi("Productos Únicos", f"{lote.total_productos_distintos:,}", "Posiciones a visitar", ft.Icons.CATEGORY, COLOR_SECUNDARIO),
            crear_tarjeta_kpi("Unidades Totales", f"{lote.total_unidades:,}", "Cantidad agregada", ft.Icons.INVENTORY_2, COLOR_EXITO),
            crear_tarjeta_kpi("Tiempo de Consolidación", f"{duracion_ms:.2f} ms", "Cómputo en una pasada O(L)", ft.Icons.SPEED, COLOR_PRIMARIO),
        ]

        # Renderizar ítems consolidados
        items_visuales = []
        max_mostrar = 100
        for item in lote.items[:max_mostrar]:
            prod = item.producto
            stock_disp = prod.stock if prod else 0
            nombre = prod.nombre if prod else f"Producto #{item.id_producto}"
            categoria = prod.categoria if prod else "Sin categoría"

            # Badge de cobertura frente a la demanda total
            alcanza = stock_disp >= item.cantidad_total
            color_alcanza = COLOR_EXITO if alcanza else COLOR_PELIGRO
            texto_alcanza = f"Stock: {stock_disp} (Suficiente)" if alcanza else f"Stock: {stock_disp} (Faltante)"

            pedidos_str = ", ".join(f"#{d.id_pedido} ({d.cantidad}u)" for d in item.demandas_por_pedido)

            items_visuales.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(f"#{item.id_producto}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO),
                                    ft.Text(nombre, size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXTO_PRIMARIO),
                                    ft.Container(expand=True),
                                    ft.Text(f"Total a recolectar: {item.cantidad_total} uds", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                    ft.Container(
                                        content=ft.Text(texto_alcanza, size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                        bgcolor=color_alcanza,
                                        padding=padding_symmetric(horizontal=8, vertical=3),
                                        border_radius=6,
                                    ),
                                ],
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(f"Categoría: {categoria}", size=12, color=COLOR_TEXTO_MUTED),
                                    ft.Text(" • ", size=12, color=COLOR_TEXTO_MUTED),
                                    ft.Text(f"Requerido en {item.total_pedidos_solicitantes} pedidos: {pedidos_str}", size=12, color=COLOR_TEXTO_SECUNDARIO),
                                ],
                            ),
                        ],
                        spacing=4,
                    ),
                    padding=padding_symmetric(horizontal=14, vertical=10),
                    bgcolor=COLOR_TARJETA,
                    border_radius=8,
                    border=borde_all(1, COLOR_BORDE),
                )
            )

        if len(lote.items) > max_mostrar:
            items_visuales.append(
                ft.Text(f"Mostrando los primeros {max_mostrar} de {len(lote.items)} productos únicos...", size=12, color=COLOR_TEXTO_MUTED)
            )

        self.col_items_picking.controls = items_visuales
        self.on_actualizar_panel(
            dataset="activo",
            n_productos=len(self.motor.catalogo),
            n_pedidos=len(self.motor.pedidos),
            estrategia=self.motor.estrategia,
            tiempo_ms=duracion_ms,
            resultado_negocio=f"Picking: {lote.total_productos_distintos} prods únicos, {lote.total_unidades} uds totales",
        )
        actualizar_control(self)
