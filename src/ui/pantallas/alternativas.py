"""Pantalla de Sugerencia de Alternativas y Combinaciones (Programación Dinámica / Memoización)."""

from __future__ import annotations
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
    padding_symmetric,
    crear_tarjeta_kpi,
)


class PantallaAlternativas(ft.Container):
    """Vista para encontrar combinaciones de sustitutos con y sin memoización."""

    def __init__(self, motor: MotorInventario, on_actualizar_panel, notificar) -> None:
        super().__init__()
        self.motor = motor
        self.on_actualizar_panel = on_actualizar_panel
        self.notificar = notificar
        self.expand = True
        self.padding = 24

        categorias_disponibles = sorted({p.categoria for p in self.motor.catalogo.obtener_todos()})
        cat_inicial = categorias_disponibles[0] if categorias_disponibles else "Ferretería y Herramientas"

        self.dropdown_categoria = ft.Dropdown(
            label="Categoría del sustituto",
            options=[ft.dropdown.Option(cat, cat) for cat in categorias_disponibles],
            value=cat_inicial,
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_PRIMARIO,
            color=COLOR_TEXTO_PRIMARIO,
            width=320,
        )

        self.input_presupuesto = ft.TextField(
            label="Presupuesto máximo ($)",
            value="45000",
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_PRIMARIO,
            color=COLOR_TEXTO_PRIMARIO,
            width=180,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.switch_memo = ft.Switch(
            label="Memoización (Programación Dinámica)",
            value=True,
            active_color=COLOR_PRIMARIO,
        )

        self.btn_buscar = ft.FilledButton(
            "Calcular Combinaciones",
            icon=ft.Icons.AUTO_AWESOME_ROUNDED,
            style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color="#FFFFFF"),
            on_click=lambda _: self._ejecutar_busqueda(),
        )

        self.fila_kpis = ft.Row(spacing=12)
        self.col_combinaciones = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        self._construir_interfaz()
        self._ejecutar_busqueda()

    def _construir_interfaz(self) -> None:
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Cálculo de Alternativas y Combinaciones Sustitutas", size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                ft.Text("Demostración experimental de Memoización: Árbol recursivo exhaustivo O(2^N) vs. Programación Dinámica O(N * P)", size=13, color=COLOR_TEXTO_SECUNDARIO),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        self.btn_buscar,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=16, color=COLOR_BORDE),
                # Barra de configuración
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.dropdown_categoria,
                            self.input_presupuesto,
                            self.switch_memo,
                        ],
                        spacing=16,
                        wrap=True,
                    ),
                    padding=12,
                    bgcolor=COLOR_TARJETA,
                    border_radius=8,
                    border=borde_all(1, COLOR_BORDE),
                ),
                self.fila_kpis,
                ft.Container(height=4),
                ft.Text("Opciones de Sustitución Encontradas", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                self.col_combinaciones,
            ],
            spacing=12,
            expand=True,
        )

    def _ejecutar_busqueda(self):
        cat = self.dropdown_categoria.value or "Ferretería y Herramientas"
        try:
            presupuesto = float(self.input_presupuesto.value or "45000")
        except ValueError:
            self.notificar("Ingrese un presupuesto numérico válido.", ft.Icons.WARNING)
            return

        usar_memo = self.switch_memo.value

        res = self.motor.buscar_alternativas(
            categoria=cat,
            presupuesto_maximo=presupuesto,
            max_combinaciones=15,
            forzar_memoizacion=usar_memo,
        )

        estrategia_nombre = "DP Memoizada" if usar_memo else "Recursión Pura"

        # Actualizar KPIs
        self.fila_kpis.controls = [
            crear_tarjeta_kpi("Estrategia", estrategia_nombre, f"Categoría: {cat}", ft.Icons.PSYCHOLOGY, COLOR_PRIMARIO),
            crear_tarjeta_kpi("Tiempo", f"{res.tiempo_ejecucion_ms:.2f} ms", f"{res.total_combinaciones} combos hallados", ft.Icons.SPEED, COLOR_EXITO),
            crear_tarjeta_kpi("Llamadas Recursivas", f"{res.total_llamadas_recursivas:,}", "Nodos del árbol explorados", ft.Icons.HUB, COLOR_SECUNDARIO),
            crear_tarjeta_kpi("Aciertos de Memo (Hits)", f"{res.hits_memo:,}", "Subproblemas no recomputados", ft.Icons.SAVED_SEARCH, COLOR_PRIMARIO),
        ]

        # Renderizar combinaciones
        items = []
        for idx, combo in enumerate(res.combinaciones, start=1):
            nombres_prods = " + ".join(f"{p.nombre} (${p.precio:,.2f})" for p in combo.productos)

            items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(f"Opción #{idx}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO),
                                width=80,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(nombres_prods, size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXTO_PRIMARIO),
                                    ft.Text(f"{combo.cantidad_items} artículos sugeridos con stock", size=12, color=COLOR_TEXTO_MUTED),
                                ],
                                expand=True,
                                spacing=2,
                            ),
                            ft.Text(f"Costo Total: ${combo.costo_total:,.2f}", size=14, weight=ft.FontWeight.BOLD, color=COLOR_EXITO),
                        ],
                    ),
                    padding=padding_symmetric(horizontal=16, vertical=12),
                    bgcolor=COLOR_TARJETA,
                    border_radius=8,
                    border=borde_all(1, COLOR_BORDE),
                )
            )

        if not res.combinaciones:
            items.append(
                ft.Text(
                    f"No se encontraron productos disponibles en '{cat}' con precio <= ${presupuesto:,.2f}",
                    size=13,
                    color=COLOR_TEXTO_MUTED,
                )
            )

        self.col_combinaciones.controls = items
        self.on_actualizar_panel(
            dataset="activo",
            n_productos=len(self.motor.catalogo),
            n_pedidos=len(self.motor.pedidos),
            estrategia=self.motor.estrategia,
            tiempo_ms=res.tiempo_ejecucion_ms,
            resultado_negocio=f"Alternativas ({estrategia_nombre}): {res.total_combinaciones} combinaciones para ${presupuesto:,.0f}",
        )
        actualizar_control(self)
