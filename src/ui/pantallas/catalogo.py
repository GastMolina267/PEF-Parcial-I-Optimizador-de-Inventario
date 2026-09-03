"""Pantalla de Exploración y Búsqueda del Catálogo de Productos."""

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
)


class PantallaCatalogo(ft.Container):
    """Vista de catálogo con búsquedas comparativas entre catálogo lineal y hash."""

    def __init__(self, motor: MotorInventario, on_actualizar_panel, notificar) -> None:
        super().__init__()
        self.motor = motor
        self.on_actualizar_panel = on_actualizar_panel
        self.notificar = notificar
        self.expand = True
        self.padding = 24

        # Campo de búsqueda por texto o ID
        self.input_busqueda = ft.TextField(
            label="Buscar por nombre o descripción",
            hint_text="Ej: 'taladro', 'foco', 'pvc'...",
            prefix_icon=ft.Icons.SEARCH,
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_PRIMARIO,
            color=COLOR_TEXTO_PRIMARIO,
            expand=True,
            on_submit=lambda _: self._ejecutar_busqueda(),
        )

        self.input_id = ft.TextField(
            label="ID numérico",
            hint_text="Ej: 1",
            width=130,
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_PRIMARIO,
            color=COLOR_TEXTO_PRIMARIO,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_submit=lambda _: self._ejecutar_busqueda_id(),
        )

        self.switch_estrategia_local = ft.Switch(
            label="Modo Optimizado (Hash O(1))",
            value=self.motor.es_optimizado,
            active_color=COLOR_PRIMARIO,
            on_change=self._al_cambiar_switch,
        )

        self.btn_buscar = ft.FilledButton(
            "Buscar",
            icon=ft.Icons.SEARCH,
            style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color="#FFFFFF"),
            on_click=lambda _: self._ejecutar_busqueda(),
        )

        self.btn_limpiar = ft.OutlinedButton(
            "Ver Todos",
            icon=ft.Icons.CLEAR_ALL,
            on_click=lambda _: self._mostrar_todos(),
        )

        # Diagnóstico de la consulta
        self.txt_tiempo_busqueda = ft.Text("Tiempo: -- ms", size=13, color=COLOR_PRIMARIO, weight=ft.FontWeight.BOLD)
        self.txt_estado_cache = ft.Text("Caché: --", size=13, color=COLOR_TEXTO_MUTED)
        self.txt_resultados_count = ft.Text("Total: -- productos", size=13, color=COLOR_TEXTO_SECUNDARIO)

        # Tabla o lista de productos
        self.col_productos = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)

        self._construir_interfaz()
        self._mostrar_todos()

    def _construir_interfaz(self) -> None:
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Catálogo de Productos", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                ft.Text("Comparación en tiempo real: Búsqueda Lineal O(n) vs. Búsqueda Hash O(1) con LRU", size=13, color=COLOR_TEXTO_SECUNDARIO),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        self.switch_estrategia_local,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=16, color=COLOR_BORDE),
                # Barra de herramientas de búsqueda
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.input_busqueda,
                            self.input_id,
                            self.btn_buscar,
                            self.btn_limpiar,
                        ],
                        spacing=10,
                    ),
                    padding=12,
                    bgcolor=COLOR_TARJETA,
                    border_radius=8,
                    border=borde_all(1, COLOR_BORDE),
                ),
                # Barra de métricas de la búsqueda
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.txt_resultados_count,
                            ft.VerticalDivider(width=1, color=COLOR_BORDE),
                            self.txt_tiempo_busqueda,
                            ft.VerticalDivider(width=1, color=COLOR_BORDE),
                            self.txt_estado_cache,
                        ],
                        spacing=12,
                    ),
                    padding=padding_symmetric(horizontal=12, vertical=6),
                ),
                # Listado de productos
                self.col_productos,
            ],
            spacing=12,
            expand=True,
        )

    def _al_cambiar_switch(self, e):
        nueva = "optimizado" if self.switch_estrategia_local.value else "baseline"
        self.motor.cambiar_estrategia(nueva)
        self.switch_estrategia_local.label = (
            "Modo Optimizado (Hash O(1))" if self.switch_estrategia_local.value else "Modo Baseline (Lineal O(n))"
        )
        self.on_actualizar_panel(
            dataset=self.motor.obtener_estadisticas()["categorias"][0] if self.motor.catalogo else "dataset",
            n_productos=len(self.motor.catalogo),
            n_pedidos=len(self.motor.pedidos),
            estrategia=nueva,
            resultado_negocio=f"Estrategia conmutada a {nueva.upper()}",
        )
        self._ejecutar_busqueda()

    def _ejecutar_busqueda(self):
        texto = self.input_busqueda.value or ""
        if not texto.strip():
            self._mostrar_todos()
            return

        inicio = time.perf_counter()
        hits_antes = self.motor.cache.metricas.hits if self.motor.es_optimizado else 0

        prods = self.motor.buscar_por_nombre(texto, usar_cache=True)
        duracion_ms = (time.perf_counter() - inicio) * 1000.0

        hits_despues = self.motor.cache.metricas.hits if self.motor.es_optimizado else 0
        fue_hit = (hits_despues > hits_antes)

        self.txt_tiempo_busqueda.value = f"Tiempo: {duracion_ms:.3f} ms"
        if self.motor.es_optimizado:
            self.txt_estado_cache.value = "Caché: HIT" if fue_hit else "Caché: MISS (Guardado)"
            self.txt_estado_cache.color = COLOR_EXITO if fue_hit else COLOR_SECUNDARIO
        else:
            self.txt_estado_cache.value = "Caché: DESHABILITADA (Baseline)"
            self.txt_estado_cache.color = COLOR_TEXTO_MUTED

        self.txt_resultados_count.value = f"Total: {len(prods)} productos encontrados"
        self._renderizar_lista(prods)

    def _ejecutar_busqueda_id(self):
        txt_id = self.input_id.value or ""
        if not txt_id.isdigit():
            self.notificar("Ingrese un identificador numérico válido.", ft.Icons.WARNING)
            return

        id_num = int(txt_id)
        inicio = time.perf_counter()
        prod = self.motor.buscar_por_id(id_num)
        duracion_ms = (time.perf_counter() - inicio) * 1000.0

        self.txt_tiempo_busqueda.value = f"Tiempo: {duracion_ms:.3f} ms"
        self.txt_estado_cache.value = "Búsqueda directa por ID"
        self.txt_estado_cache.color = COLOR_PRIMARIO

        prods = [prod] if prod else []
        self.txt_resultados_count.value = f"Total: {len(prods)} producto encontrado"
        self._renderizar_lista(prods)

    def _mostrar_todos(self):
        self.input_busqueda.value = ""
        self.input_id.value = ""
        prods = self.motor.catalogo.obtener_todos()
        self.txt_resultados_count.value = f"Total: {len(prods)} productos en catálogo"
        self.txt_tiempo_busqueda.value = "Tiempo: 0.00 ms"
        self.txt_estado_cache.value = "Vista completa"
        self.txt_estado_cache.color = COLOR_TEXTO_MUTED
        self._renderizar_lista(prods)

    def _renderizar_lista(self, productos):
        items = []
        # Limitar vista a 150 elementos para rendimiento visual fluido
        max_mostrar = 150
        for p in productos[:max_mostrar]:
            stock_color = COLOR_EXITO if p.stock > 10 else ("#F59E0B" if p.stock > 0 else COLOR_PELIGRO)
            stock_texto = f"{p.stock} uds" if p.stock > 0 else "SIN STOCK"

            items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(f"#{p.id}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO),
                                width=50,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(p.nombre, size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXTO_PRIMARIO),
                                    ft.Text(p.categoria, size=12, color=COLOR_TEXTO_MUTED),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.Text(f"${p.precio:,.2f}", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                            ft.Container(
                                content=ft.Text(stock_texto, size=11, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
                                bgcolor=stock_color,
                                padding=padding_symmetric(horizontal=8, vertical=3),
                                border_radius=6,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=padding_symmetric(horizontal=12, vertical=8),
                    bgcolor=COLOR_TARJETA,
                    border_radius=6,
                    border=borde_all(1, COLOR_BORDE),
                )
            )

        if len(productos) > max_mostrar:
            items.append(
                ft.Text(
                    f"Mostrando los primeros {max_mostrar} de {len(productos)} productos...",
                    size=12,
                    color=COLOR_TEXTO_MUTED,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        self.col_productos.controls = items
        actualizar_control(self)
