"""Pantalla de Inicio y Selección de Escenarios / Datasets."""

from __future__ import annotations
from pathlib import Path
import time
import flet as ft
from src.motor.motor_inventario import MotorInventario
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
    borde_all,
    crear_tarjeta_kpi,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATASETS_DIR = BASE_DIR / "data" / "datasets"


class PantallaInicio(ft.Container):
    """Vista principal de bienvenida, carga de datos y ejecución global de escenarios."""

    def __init__(self, motor: MotorInventario, on_actualizar_panel, notificar) -> None:
        super().__init__()
        self.motor = motor
        self.on_actualizar_panel = on_actualizar_panel
        self.notificar = notificar
        self.expand = True
        self.padding = 24

        # Dropdown de datasets estándar
        self.dropdown_datasets = ft.Dropdown(
            label="Dataset empaquetado",
            options=[
                ft.dropdown.Option("demo_oral.json", "demo_oral.json (30 productos, 8 pedidos - Oral)"),
                ft.dropdown.Option("pequeno.json", "pequeno.json (100 productos, 20 pedidos - Rápido)"),
                ft.dropdown.Option("mediano.json", "mediano.json (1.000 productos, 200 pedidos - Medio)"),
                ft.dropdown.Option("grande.json", "grande.json (10.000 productos, 2.000 pedidos - Grande)"),
            ],
            value="demo_oral.json",
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_PRIMARIO,
            color=COLOR_TEXTO_PRIMARIO,
            width=450,
            on_select=self._al_seleccionar_dataset,
        )

        self.btn_cargar = ft.FilledButton(
            "Recargar Dataset",
            icon=ft.Icons.REFRESH,
            style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color="#FFFFFF"),
            on_click=lambda _: self._cargar_dataset_actual(),
        )

        self.btn_ejecutar_escenario = ft.FilledButton(
            "Ejecutar Escenario Completo",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            style=ft.ButtonStyle(bgcolor=COLOR_SECUNDARIO, color="#FFFFFF"),
            on_click=lambda _: self._ejecutar_escenario_completo(),
        )

        # Contenedores de KPIs dinámicos
        self.fila_kpis = ft.Row(spacing=12)
        # Contenedor de resultados del escenario completo
        self.col_resultado_escenario = ft.Column(spacing=8)

        self._construir_interfaz()
        self._actualizar_metricas_visuales()

    def _construir_interfaz(self) -> None:
        self.content = ft.ListView(
            controls=[
                ft.Text(
                    "Optimizador de Inventario y Pedidos",
                    size=26,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_TEXTO_PRIMARIO,
                ),
                ft.Text(
                    "Primer Parcial – Programación Eficiente (Opción 6) | Universidad Blas Pascal",
                    size=14,
                    color=COLOR_TEXTO_SECUNDARIO,
                ),
                ft.Divider(height=24, color=COLOR_BORDE),
                # Selector y controles
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.dropdown_datasets,
                            self.btn_cargar,
                            self.btn_ejecutar_escenario,
                        ],
                        spacing=12,
                        wrap=True,
                    ),
                    padding=16,
                    bgcolor=COLOR_TARJETA,
                    border_radius=10,
                    border=borde_all(1, COLOR_BORDE),
                ),
                ft.Container(height=12),
                # Métricas del dataset
                self.fila_kpis,
                ft.Container(height=16),
                # Panel de ejecución del escenario
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.INSIGHTS_ROUNDED, color=COLOR_PRIMARIO, size=20),
                                    ft.Text(
                                        "Diagnóstico y Ejecución Global del Escenario",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_TEXTO_PRIMARIO,
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.Text(
                                "Al presionar 'Ejecutar Escenario Completo', el motor ejecuta secuencialmente la preparación de pedidos, el picking consolidado, el ranking Top-N y el cálculo de alternativas sustitutas para los faltantes.",
                                size=13,
                                color=COLOR_TEXTO_MUTED,
                            ),
                            ft.Divider(height=12, color=COLOR_BORDE),
                            self.col_resultado_escenario,
                        ],
                        spacing=8,
                    ),
                    padding=20,
                    bgcolor=COLOR_TARJETA,
                    border_radius=10,
                    border=borde_all(1, COLOR_BORDE),
                ),
            ],
            spacing=16,
        )

    def _al_seleccionar_dataset(self, e):
        self._cargar_dataset_actual()

    def _cargar_dataset_actual(self):
        nombre = self.dropdown_datasets.value
        ruta = DATASETS_DIR / nombre
        try:
            inicio = time.perf_counter()
            self.motor.cargar_dataset(ruta)
            duracion_ms = (time.perf_counter() - inicio) * 1000.0

            self._actualizar_metricas_visuales()
            stats = self.motor.obtener_estadisticas()
            self.on_actualizar_panel(
                dataset=nombre,
                n_productos=stats["total_productos"],
                n_pedidos=stats["total_pedidos"],
                estrategia=self.motor.estrategia,
                tiempo_ms=duracion_ms,
                resultado_negocio=f"Dataset {nombre} cargado en {duracion_ms:.1f} ms",
            )
            self.notificar(f"Dataset '{nombre}' cargado con éxito.", ft.Icons.CHECK)
        except Exception as err:
            self.notificar(f"Error al cargar dataset: {err}", ft.Icons.ERROR, color=COLOR_EXITO)

    def _actualizar_metricas_visuales(self):
        stats = self.motor.obtener_estadisticas()
        self.fila_kpis.controls = [
            crear_tarjeta_kpi(
                "Catálogo de Productos",
                f"{stats['total_productos']:,}",
                f"{stats['total_categorias']} categorías registradas",
                ft.Icons.INVENTORY_2,
                COLOR_PRIMARIO,
            ),
            crear_tarjeta_kpi(
                "Lote de Pedidos",
                f"{stats['total_pedidos']:,}",
                f"{stats['total_lineas_pedidos']} líneas de demanda",
                ft.Icons.SHOPPING_BAG,
                COLOR_SECUNDARIO,
            ),
            crear_tarjeta_kpi(
                "Unidades en Stock",
                f"{stats['stock_total_unidades']:,}",
                "Disponibilidad total en almacén",
                ft.Icons.WAREHOUSE,
                COLOR_EXITO,
            ),
            crear_tarjeta_kpi(
                "Demanda Total",
                f"{stats['unidades_demandadas']:,}",
                f"Estrategia: {self.motor.estrategia.upper()}",
                ft.Icons.TRENDING_UP,
                COLOR_PRIMARIO,
            ),
        ]
        actualizar_control(self)

    def _ejecutar_escenario_completo(self):
        try:
            inicio_total = time.perf_counter()

            # 1. Preparar pedidos
            res_pedidos = self.motor.procesar_pedidos(descontar_stock=False)
            # 2. Batch picking
            picking = self.motor.agrupar_pedidos()
            # 3. Top-N
            top_5 = self.motor.obtener_top_solicitados(k=5)

            # 4. Alternativas para el primer pedido con faltantes (si existe)
            pedido_faltante = next((r for r in res_pedidos.resultados if not r.es_exitoso), None)
            res_alternativas = None
            if pedido_faltante and pedido_faltante.lineas_faltantes:
                linea_f = pedido_faltante.lineas_faltantes[0]
                prod_f = self.motor.buscar_por_id(linea_f.id_producto)
                if prod_f:
                    presupuesto = prod_f.precio * linea_f.cantidad_solicitada
                    res_alternativas = self.motor.buscar_alternativas(
                        categoria=prod_f.categoria,
                        presupuesto_maximo=max(presupuesto, 10000.0),
                        producto_original=prod_f,
                        max_combinaciones=3,
                    )

            duracion_total_ms = (time.perf_counter() - inicio_total) * 1000.0

            # Renderizar resumen
            items_resumen = [
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SHOPPING_CART_CHECKOUT, color=COLOR_PRIMARIO),
                    title=ft.Text(f"Preparación de Pedidos: {res_pedidos.pedidos_procesados} pedidos analizados", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(
                        f"Cubiertos: {res_pedidos.pedidos_cubiertos} | Parciales: {res_pedidos.pedidos_parciales} | "
                        f"Imposibles: {res_pedidos.pedidos_imposibles} (Tiempo: {res_pedidos.tiempo_ejecucion_ms:.2f} ms)",
                        color=COLOR_TEXTO_SECUNDARIO,
                    ),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.ALL_INBOX, color=COLOR_SECUNDARIO),
                    title=ft.Text(f"Batch Picking Consolidado: {picking.total_productos_distintos} productos únicos", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(
                        f"Total unidades a recolectar: {picking.total_unidades} entre {picking.total_pedidos} pedidos.",
                        color=COLOR_TEXTO_SECUNDARIO,
                    ),
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.LEADERBOARD, color=COLOR_EXITO),
                    title=ft.Text("Productos Top-3 más solicitados", weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(
                        ", ".join(f"{p.nombre} ({c} uds)" for p, c in top_5[:3]) if top_5 else "Sin demanda",
                        color=COLOR_TEXTO_SECUNDARIO,
                    ),
                ),
            ]

            if res_alternativas and res_alternativas.total_combinaciones > 0:
                items_resumen.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.SWAP_HORIZ, color="#F59E0B"),
                        title=ft.Text(f"Alternativas sugeridas para Pedido #{pedido_faltante.id_pedido}", weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(
                            f"Encontradas {res_alternativas.total_combinaciones} combinaciones sustitutas en {res_alternativas.categoria} (Tiempo: {res_alternativas.tiempo_ejecucion_ms:.2f} ms).",
                            color=COLOR_TEXTO_SECUNDARIO,
                        ),
                    )
                )

            self.col_resultado_escenario.controls = items_resumen
            self.on_actualizar_panel(
                dataset=self.dropdown_datasets.value,
                n_productos=len(self.motor.catalogo),
                n_pedidos=len(self.motor.pedidos),
                estrategia=self.motor.estrategia,
                tiempo_ms=duracion_total_ms,
                resultado_negocio=f"Escenario ejecutado: {res_pedidos.pedidos_cubiertos}/{res_pedidos.pedidos_procesados} cubiertos",
            )
            actualizar_control(self)
            self.notificar(f"Escenario completo ejecutado en {duracion_total_ms:.2f} ms.", ft.Icons.DONE_ALL)
        except Exception as err:
            self.notificar(f"Error en ejecución de escenario: {err}", ft.Icons.ERROR)
