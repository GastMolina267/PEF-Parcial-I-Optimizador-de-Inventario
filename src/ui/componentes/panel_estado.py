"""Componente de panel de estado persistente e informativo.

Muestra en tiempo real en la parte superior de la aplicación:
- Dataset actualmente cargado.
- N productos y N pedidos del escenario.
- Estrategia activa (Baseline vs Optimizado) con toggle rápido.
- Tiempo y memoria estimada de la última corrida.
- Resumen del resultado de negocio.
"""

from __future__ import annotations
import flet as ft
from src.ui.tema import (
    COLOR_BORDE,
    COLOR_EXITO,
    COLOR_PRIMARIO,
    COLOR_SECUNDARIO,
    COLOR_SUPERFICIE,
    COLOR_TARJETA,
    COLOR_TEXTO_MUTED,
    COLOR_TEXTO_PRIMARIO,
    COLOR_TEXTO_SECUNDARIO,
    borde_all,
    borde_only,
    padding_symmetric,
    actualizar_control,
)


class PanelEstado(ft.Container):
    """Barra superior persistente de métricas y control de estrategia."""

    def __init__(self, on_cambiar_estrategia) -> None:
        super().__init__()
        self.on_cambiar_estrategia = on_cambiar_estrategia

        self.txt_dataset = ft.Text(
            value="demo_oral.json",
            size=13,
            weight=ft.FontWeight.BOLD,
            color=COLOR_TEXTO_PRIMARIO,
        )
        self.txt_volumen = ft.Text(
            value="30 prods | 8 pedidos",
            size=12,
            color=COLOR_TEXTO_SECUNDARIO,
        )
        self.txt_ultima_corrida = ft.Text(
            value="Última corrida: -- ms | -- MB",
            size=12,
            color=COLOR_TEXTO_MUTED,
        )
        self.txt_resultado_negocio = ft.Text(
            value="Listo para operar",
            size=12,
            weight=ft.FontWeight.W_500,
            color=COLOR_EXITO,
        )

        self.switch_estrategia = ft.Switch(
            label="Modo Optimizado",
            value=False,
            active_color=COLOR_PRIMARIO,
            on_change=self._al_cambiar_switch,
        )

        self.padding = padding_symmetric(horizontal=16, vertical=10)
        self.bgcolor = COLOR_SUPERFICIE
        self.border = borde_only(bottom=ft.border.BorderSide(1, COLOR_BORDE))

        self.content = ft.Row(
            controls=[
                # Columna 1: Dataset y tamaño
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.STORAGE_ROUNDED, size=20, color=COLOR_PRIMARIO),
                        ft.Column(
                            controls=[self.txt_dataset, self.txt_volumen],
                            spacing=1,
                            tight=True,
                        ),
                    ],
                    spacing=8,
                ),
                ft.VerticalDivider(width=1, color=COLOR_BORDE),
                # Columna 2: Métricas de última corrida
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SPEED_ROUNDED, size=20, color=COLOR_SECUNDARIO),
                        ft.Column(
                            controls=[self.txt_ultima_corrida, self.txt_resultado_negocio],
                            spacing=1,
                            tight=True,
                        ),
                    ],
                    spacing=8,
                ),
                # Espaciador central
                ft.Container(expand=True),
                # Columna 3: Control de estrategia
                ft.Container(
                    content=self.switch_estrategia,
                    bgcolor=COLOR_TARJETA,
                    padding=padding_symmetric(horizontal=12, vertical=4),
                    border_radius=8,
                    border=borde_all(1, COLOR_BORDE),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _al_cambiar_switch(self, e):
        nueva = "optimizado" if self.switch_estrategia.value else "baseline"
        self.on_cambiar_estrategia(nueva)

    def actualizar_estado(
        self,
        dataset: str,
        n_productos: int,
        n_pedidos: int,
        estrategia: str,
        tiempo_ms: float | None = None,
        memoria_mb: float | None = None,
        resultado_negocio: str | None = None,
    ) -> None:
        """Actualiza la información visible en el panel."""
        self.txt_dataset.value = dataset
        self.txt_volumen.value = f"{n_productos:,} prods | {n_pedidos:,} pedidos"
        self.switch_estrategia.value = (estrategia == "optimizado")
        self.switch_estrategia.label = (
            "Modo Optimizado (O(1))" if self.switch_estrategia.value else "Modo Baseline (O(n))"
        )

        if tiempo_ms is not None:
            mem_str = f"{memoria_mb:.2f} MB" if memoria_mb is not None else "-- MB"
            self.txt_ultima_corrida.value = f"Última corrida: {tiempo_ms:.2f} ms | {mem_str}"

        if resultado_negocio is not None:
            self.txt_resultado_negocio.value = resultado_negocio

        actualizar_control(self)
