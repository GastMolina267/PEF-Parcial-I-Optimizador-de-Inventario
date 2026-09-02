"""Pantalla de Preparación y Procesamiento de Pedidos."""

from __future__ import annotations
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
    crear_badge_estado,
    crear_tarjeta_kpi,
)


class PantallaPedidos(ft.Container):
    """Vista para procesar lotes de pedidos de forma secuencial o concurrente."""

    def __init__(self, motor: MotorInventario, on_actualizar_panel, notificar) -> None:
        super().__init__()
        self.motor = motor
        self.on_actualizar_panel = on_actualizar_panel
        self.notificar = notificar
        self.expand = True
        self.padding = 24

        # Controles
        self.switch_concurrente = ft.Switch(
            label="Procesamiento Concurrente (Multiproceso)",
            value=self.motor.es_optimizado,
            active_color=COLOR_SECUNDARIO,
        )

        self.check_descontar_stock = ft.Checkbox(
            label="Descontar stock del almacén",
            value=False,
            active_color=COLOR_PRIMARIO,
        )

        self.btn_procesar = ft.FilledButton(
            "Procesar Lote de Pedidos",
            icon=ft.Icons.PLAY_CIRCLE_FILLED_ROUNDED,
            style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color="#FFFFFF"),
            on_click=lambda _: self._ejecutar_procesamiento(),
        )

        # Fila de KPIs
        self.fila_kpis = ft.Row(spacing=12)
        # Lista scrolleable de resultados
        self.col_pedidos = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        self._construir_interfaz()
        self._actualizar_kpis_iniciales()

    def _construir_interfaz(self) -> None:
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Preparación de Pedidos en Lote", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                ft.Text("Evaluación de disponibilidad: Mono-hilo secuencial vs. ProcessPoolExecutor (CPU-bound)", size=13, color=COLOR_TEXTO_SECUNDARIO),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        self.btn_procesar,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=16, color=COLOR_BORDE),
                # Panel de configuración de ejecución
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.switch_concurrente,
                            ft.VerticalDivider(width=1, color=COLOR_BORDE),
                            self.check_descontar_stock,
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
                ft.Text("Listado de Pedidos y Estado de Cobertura", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                self.col_pedidos,
            ],
            spacing=12,
            expand=True,
        )

    def _actualizar_kpis_iniciales(self):
        total_peds = len(self.motor.pedidos)
        self.fila_kpis.controls = [
            crear_tarjeta_kpi("Total Pedidos", f"{total_peds:,}", "En cola de preparación", ft.Icons.RECEIPT_LONG, COLOR_PRIMARIO),
            crear_tarjeta_kpi("Cubiertos", "--", "100% de stock disponible", ft.Icons.CHECK_CIRCLE, COLOR_EXITO),
            crear_tarjeta_kpi("Parciales", "--", "Stock parcial o faltantes", ft.Icons.WARNING, "#F59E0B"),
            crear_tarjeta_kpi("Imposibles", "--", "Sin stock disponible", ft.Icons.CANCEL, COLOR_PELIGRO),
        ]
        self._renderizar_pedidos_sin_procesar()

    def _renderizar_pedidos_sin_procesar(self):
        items = []
        max_mostrar = 100
        for ped in self.motor.pedidos[:max_mostrar]:
            items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"Pedido #{ped.id}", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                            ft.Text(f"{len(ped.lineas)} líneas demandadas", size=13, color=COLOR_TEXTO_MUTED),
                            ft.Container(expand=True),
                            ft.Text("Pendiente de procesar", size=12, color=COLOR_TEXTO_MUTED),
                        ],
                    ),
                    padding=padding_symmetric(horizontal=14, vertical=10),
                    bgcolor=COLOR_TARJETA,
                    border_radius=6,
                    border=borde_all(1, COLOR_BORDE),
                )
            )
        self.col_pedidos.controls = items
        actualizar_control(self)

    def _ejecutar_procesamiento(self):
        es_conc = self.switch_concurrente.value
        descontar = self.check_descontar_stock.value

        try:
            resumen = self.motor.procesar_pedidos(
                concurrente=es_conc,
                descontar_stock=descontar,
            )

            # Actualizar KPIs
            self.fila_kpis.controls = [
                crear_tarjeta_kpi("Total Procesados", f"{resumen.pedidos_procesados:,}", f"Tiempo: {resumen.tiempo_ejecucion_ms:.2f} ms", ft.Icons.RECEIPT_LONG, COLOR_PRIMARIO),
                crear_tarjeta_kpi("Cubiertos", f"{resumen.pedidos_cubiertos:,}", f"{resumen.porcentaje_cobertura:.1f}% del lote", ft.Icons.CHECK_CIRCLE, COLOR_EXITO),
                crear_tarjeta_kpi("Parciales", f"{resumen.pedidos_parciales:,}", "Faltante parcial", ft.Icons.WARNING, "#F59E0B"),
                crear_tarjeta_kpi("Imposibles", f"{resumen.pedidos_imposibles:,}", "Faltante total", ft.Icons.CANCEL, COLOR_PELIGRO),
            ]

            # Renderizar lista de resultados
            items = []
            max_mostrar = 100
            for r in resumen.resultados[:max_mostrar]:
                total_lineas = len(r.lineas_cubiertas) + len(r.lineas_faltantes)
                desc_lineas = f"{len(r.lineas_cubiertas)}/{total_lineas} líneas cubiertas"

                items.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(f"Pedido #{r.id_pedido}", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                ft.Text(desc_lineas, size=13, color=COLOR_TEXTO_SECUNDARIO),
                                ft.Container(expand=True),
                                crear_badge_estado(r.estado.value),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=padding_symmetric(horizontal=14, vertical=10),
                        bgcolor=COLOR_TARJETA,
                        border_radius=6,
                        border=borde_all(1, COLOR_BORDE),
                    )
                )

            if len(resumen.resultados) > max_mostrar:
                items.append(
                    ft.Text(f"Mostrando los primeros {max_mostrar} de {len(resumen.resultados)} pedidos...", size=12, color=COLOR_TEXTO_MUTED)
                )

            self.col_pedidos.controls = items
            modo_txt = "Concurrente" if es_conc else "Secuencial"
            self.on_actualizar_panel(
                dataset="activo",
                n_productos=len(self.motor.catalogo),
                n_pedidos=len(self.motor.pedidos),
                estrategia=self.motor.estrategia,
                tiempo_ms=resumen.tiempo_ejecucion_ms,
                resultado_negocio=f"Lote ({modo_txt}): {resumen.pedidos_cubiertos} cubiertos, {resumen.pedidos_parciales} parciales",
            )
            actualizar_control(self)
            self.notificar(f"Lote de pedidos procesado ({modo_txt}) en {resumen.tiempo_ejecucion_ms:.2f} ms.", ft.Icons.CHECK)
        except Exception as err:
            self.notificar(f"Error al procesar pedidos: {err}", ft.Icons.ERROR)
