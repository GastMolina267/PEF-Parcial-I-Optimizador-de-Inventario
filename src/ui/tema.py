"""Definición del sistema de diseño, paleta de colores y estilos accesibles para Flet."""

from __future__ import annotations
import flet as ft

# Paleta de colores Dark Slate & Cyan (Alto contraste y estética moderna)
COLOR_FONDO_APP = "#0B0F19"         # Fondo general profundo
COLOR_SUPERFICIE = "#111827"        # Contenedores principales y rails
COLOR_TARJETA = "#1F2937"           # Cards y paneles elevados
COLOR_TARJETA_HOVER = "#2D3748"     # Hover sobre tarjetas
COLOR_BORDE = "#374151"             # Bordes sutiles con contraste
COLOR_BORDE_ENFOQUE = "#38BDF8"     # Foco activo (Cyan)

COLOR_TEXTO_PRIMARIO = "#F9FAFB"    # Blanco puro de alto contraste (WCAG AAA)
COLOR_TEXTO_SECUNDARIO = "#9CA3AF"  # Gris claro legible
COLOR_TEXTO_MUTED = "#6B7280"       # Gris medio para metadatos

COLOR_PRIMARIO = "#0EA5E9"          # Cyan 500 (Acciones principales)
COLOR_PRIMARIO_VARIANTE = "#0284C7" # Cyan 600
COLOR_SECUNDARIO = "#6366F1"        # Indigo 500 (Acentos analíticos)
COLOR_SECUNDARIO_VARIANTE = "#4F46E5"

# Colores de estado accesibles (Icono + Color + Texto)
COLOR_EXITO = "#10B981"             # Esmeralda (Cubierto)
COLOR_FONDO_EXITO = "#064E3B"
COLOR_ADVERTENCIA = "#F59E0B"       # Ámbar (Parcial)
COLOR_FONDO_ADVERTENCIA = "#78350F"
COLOR_PELIGRO = "#EF4444"           # Carmesí (Imposible / Error)
COLOR_FONDO_PELIGRO = "#7F1D1D"


def borde_all(ancho: float = 1, color: str = COLOR_BORDE) -> ft.border.Border:
    """Crea un borde completo compatible con todas las versiones de Flet."""
    if hasattr(ft.border, "all"):
        return ft.border.all(ancho, color)
    return ft.border.Border.all(ancho, color)


def borde_only(
    bottom: ft.border.BorderSide | None = None,
    top: ft.border.BorderSide | None = None,
    left: ft.border.BorderSide | None = None,
    right: ft.border.BorderSide | None = None,
) -> ft.border.Border:
    """Crea un borde parcial compatible con todas las versiones de Flet."""
    if hasattr(ft.border, "only"):
        return ft.border.only(bottom=bottom, top=top, left=left, right=right)
    return ft.border.Border.only(bottom=bottom, top=top, left=left, right=right)


def padding_symmetric(horizontal: float = 0, vertical: float = 0) -> ft.padding.Padding:
    """Crea un padding simétrico compatible con todas las versiones de Flet."""
    if hasattr(ft.padding, "symmetric"):
        return ft.padding.symmetric(horizontal=horizontal, vertical=vertical)
    return ft.padding.Padding.symmetric(horizontal=horizontal, vertical=vertical)


def padding_all(valor: float) -> ft.padding.Padding:
    """Crea un padding uniforme compatible con todas las versiones de Flet."""
    if hasattr(ft.padding, "all"):
        return ft.padding.all(valor)
    return ft.padding.Padding.all(valor)


def alineacion_center() -> ft.alignment.Alignment:
    """Retorna alineación central compatible con versiones antiguas y nuevas de Flet."""
    if hasattr(ft.alignment, "center"):
        return ft.alignment.center
    return ft.alignment.Alignment.CENTER


def actualizar_control(control) -> None:
    """Invoca update() de forma segura capturando excepciones si el control aún no está montado."""
    try:
        control.update()
    except Exception:
        pass


def crear_badge_estado(estado: str) -> ft.Container:
    """Crea un indicador visual accesible con icono y texto explícito."""
    estado_norm = estado.lower().strip()
    if estado_norm in ("cubierto", "exito", "ok"):
        icono = ft.Icons.CHECK_CIRCLE
        color_texto = COLOR_EXITO
        color_fondo = COLOR_FONDO_EXITO
        texto = "Cubierto"
    elif estado_norm in ("parcial", "warning", "advertencia"):
        icono = ft.Icons.WARNING_AMBER_ROUNDED
        color_texto = COLOR_ADVERTENCIA
        color_fondo = COLOR_FONDO_ADVERTENCIA
        texto = "Parcial"
    else:
        icono = ft.Icons.CANCEL_ROUNDED
        color_texto = COLOR_PELIGRO
        color_fondo = COLOR_FONDO_PELIGRO
        texto = "Imposible"

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icono, size=16, color=color_texto),
                ft.Text(value=texto, size=12, weight=ft.FontWeight.W_600, color=color_texto),
            ],
            spacing=4,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=padding_symmetric(horizontal=8, vertical=4),
        bgcolor=color_fondo,
        border_radius=12,
        border=borde_all(1, color_texto),
    )


def crear_tarjeta_kpi(
    titulo: str,
    valor: str,
    subtitulo: str | None = None,
    icono: str = ft.Icons.INFO_OUTLINE,
    color_icono: str = COLOR_PRIMARIO,
) -> ft.Container:
    """Construye una tarjeta métrica estandarizada con jerarquía tipográfica clara."""
    controles = [
        ft.Row(
            controls=[
                ft.Icon(icono, size=20, color=color_icono),
                ft.Text(
                    value=titulo,
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=COLOR_TEXTO_SECUNDARIO,
                ),
            ],
            spacing=6,
        ),
        ft.Text(
            value=valor,
            size=24,
            weight=ft.FontWeight.BOLD,
            color=COLOR_TEXTO_PRIMARIO,
        ),
    ]
    if subtitulo:
        controles.append(
            ft.Text(
                value=subtitulo,
                size=12,
                color=COLOR_TEXTO_MUTED,
            )
        )

    return ft.Container(
        content=ft.Column(controls=controles, spacing=4),
        padding=16,
        bgcolor=COLOR_TARJETA,
        border_radius=10,
        border=borde_all(1, COLOR_BORDE),
        expand=True,
    )
