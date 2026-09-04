"""Definición del sistema de diseño, paleta de colores y estilos accesibles para Flet."""

from __future__ import annotations
import flet as ft

# Paleta de colores Dark Obsidian & Electric Cyan (Ultra contraste, estética moderna SaaS)
COLOR_FONDO_APP = "#090D16"         # Fondo general obsidian profundo
COLOR_SUPERFICIE = "#111A2E"        # Contenedores principales y rails (Dark Sapphire)
COLOR_TARJETA = "#182238"           # Cards y paneles elevados con contraste neto
COLOR_TARJETA_HOVER = "#222F4D"     # Hover sobre tarjetas
COLOR_BORDE = "#2D3A58"             # Bordes nítidos y definidos
COLOR_BORDE_ENFOQUE = "#38BDF8"     # Foco activo (Electric Cyan)

COLOR_TEXTO_PRIMARIO = "#FFFFFF"    # Blanco puro brillante (Máxima visibilidad)
COLOR_TEXTO_SECUNDARIO = "#E2E8F0"  # Plata Slate 200 de alta legibilidad
COLOR_TEXTO_MUTED = "#94A3B8"       # Slate 400 nítido (nunca gris oscuro borroso)

COLOR_PRIMARIO = "#0284C7"          # Sky 600 (Acciones principales)
COLOR_PRIMARIO_VARIANTE = "#0369A1" # Sky 700
COLOR_SECUNDARIO = "#818CF8"        # Indigo 400 (Acentos analíticos modernos)
COLOR_SECUNDARIO_VARIANTE = "#6366F1"

# Colores de estado accesibles (Icono + Color + Texto de alto contraste)
COLOR_EXITO = "#34D399"             # Esmeralda 400 brillante
COLOR_FONDO_EXITO = "#064E3B"       # Fondo esmeralda profundo
COLOR_ADVERTENCIA = "#FBBF24"       # Ámbar 400 luminoso
COLOR_FONDO_ADVERTENCIA = "#451A03" # Fondo ámbar oscuro
COLOR_PELIGRO = "#F87171"           # Carmesí 400 de alta visibilidad
COLOR_FONDO_PELIGRO = "#450A0A"     # Fondo carmesí oscuro



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


def crear_dropdown(
    label: str,
    options: list[ft.dropdown.Option],
    value: str,
    on_change_callback=None,
    width: float | None = None,
    **kwargs,
) -> ft.Dropdown:
    """Crea un Dropdown compatible con versiones antiguas (on_change) y nuevas (on_select) de Flet."""
    params = {
        "label": label,
        "options": options,
        "value": value,
        "border_color": COLOR_BORDE,
        "focused_border_color": COLOR_PRIMARIO,
        "color": COLOR_TEXTO_PRIMARIO,
        **kwargs,
    }
    if width is not None:
        params["width"] = width

    if on_change_callback is not None:
        try:
            return ft.Dropdown(**params, on_select=on_change_callback)
        except TypeError:
            return ft.Dropdown(**params, on_change=on_change_callback)
    return ft.Dropdown(**params)


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
    """Construye una tarjeta métrica estandarizada con jerarquía tipográfica clara y diseño compacto."""
    controles = [
        ft.Row(
            controls=[
                ft.Icon(icono, size=15, color=color_icono),
                ft.Text(
                    value=titulo,
                    size=11,
                    weight=ft.FontWeight.W_600,
                    color=COLOR_TEXTO_SECUNDARIO,
                    no_wrap=True,
                ),
            ],
            spacing=5,
            tight=True,
        ),
        ft.Text(
            value=valor,
            size=18,
            weight=ft.FontWeight.BOLD,
            color=COLOR_TEXTO_PRIMARIO,
            no_wrap=True,
        ),
    ]
    if subtitulo:
        controles.append(
            ft.Text(
                value=subtitulo,
                size=10,
                color=COLOR_TEXTO_MUTED,
                no_wrap=True,
            )
        )

    return ft.Container(
        content=ft.Column(controls=controles, spacing=2, tight=True),
        padding=padding_symmetric(horizontal=12, vertical=8),
        bgcolor=COLOR_TARJETA,
        border_radius=8,
        border=borde_all(1, COLOR_BORDE),
        expand=True,
    )



def crear_badge_tiempo(tiempo_ms: float, speedup: float | None = None) -> ft.Container:
    """Construye un badge visual llamativo para tiempos de ejecución con formato inteligente."""
    if tiempo_ms < 0.1:
        tiempo_texto = f"{tiempo_ms * 1000.0:.1f} µs"
    elif tiempo_ms < 10.0:
        tiempo_texto = f"{tiempo_ms:.3f} ms"
    else:
        tiempo_texto = f"{tiempo_ms:.2f} ms"

    color_tiempo = COLOR_EXITO if tiempo_ms < 1.0 else (COLOR_ADVERTENCIA if tiempo_ms < 20.0 else COLOR_PRIMARIO)

    controles = [
        ft.Icon(ft.Icons.BOLT_ROUNDED if tiempo_ms < 5.0 else ft.Icons.TIMER_OUTLINED, size=15, color=color_tiempo),
        ft.Text(value=tiempo_texto, size=12, weight=ft.FontWeight.BOLD, color=color_tiempo),
    ]

    if speedup is not None and speedup > 0:
        texto_speedup = f"🚀 {speedup:.1f}x" if speedup >= 1.0 else f"🐢 {speedup:.2f}x"
        color_speedup = COLOR_EXITO if speedup >= 1.0 else COLOR_PELIGRO
        controles.extend([
            ft.Text("|", size=11, color=COLOR_TEXTO_MUTED),
            ft.Text(texto_speedup, size=11, weight=ft.FontWeight.BOLD, color=color_speedup),
        ])

    return ft.Container(
        content=ft.Row(
            controls=controles,
            spacing=5,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=padding_symmetric(horizontal=8, vertical=4),
        bgcolor=COLOR_SUPERFICIE,
        border_radius=12,
        border=borde_all(1, color_tiempo),
    )


def crear_banner_explicativo(
    titulo: str,
    descripcion: str,
    complejidad_base: str,
    complejidad_opt: str,
    por_que_importa: str,
) -> ft.Container:
    """Crea una tarjeta didáctica moderna para explicar el trasfondo teórico de cada pantalla de forma compacta."""
    chip_base = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.STOP_CIRCLE_ROUNDED, size=12, color=COLOR_ADVERTENCIA),
                ft.Text(f"Baseline: {complejidad_base}", size=10, weight=ft.FontWeight.W_600, color="#FDE68A"),
            ],
            spacing=3,
            tight=True,
        ),
        padding=padding_symmetric(horizontal=8, vertical=2),
        bgcolor=COLOR_FONDO_ADVERTENCIA,
        border_radius=6,
        border=borde_all(1, "#D97706"),
    )

    chip_opt = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=12, color=COLOR_EXITO),
                ft.Text(f"Optimizado: {complejidad_opt}", size=10, weight=ft.FontWeight.W_600, color="#A7F3D0"),
            ],
            spacing=3,
            tight=True,
        ),
        padding=padding_symmetric(horizontal=8, vertical=2),
        bgcolor=COLOR_FONDO_EXITO,
        border_radius=6,
        border=borde_all(1, "#059669"),
    )

    fila_chips = ft.Row(
        controls=[
            chip_base,
            ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, size=12, color=COLOR_TEXTO_MUTED),
            chip_opt,
        ],
        spacing=6,
        wrap=True,
        tight=True,
    )

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.SCHOOL_ROUNDED, size=16, color=COLOR_PRIMARIO),
                        ft.Text(
                            value=f"Fundamento Algorítmico: {titulo}",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_TEXTO_PRIMARIO,
                            expand=True,
                        ),
                    ],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    tight=True,
                ),
                fila_chips,
                ft.Text(
                    value=descripcion,
                    size=11,
                    color=COLOR_TEXTO_SECUNDARIO,
                    weight=ft.FontWeight.W_400,
                ),
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.LIGHTBULB_ROUNDED, size=13, color=COLOR_SECUNDARIO),
                        ft.Text(
                            value=f"Relevancia oral: {por_que_importa}",
                            size=10.5,
                            color=COLOR_TEXTO_MUTED,
                            weight=ft.FontWeight.W_500,
                            expand=True,
                        ),
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    tight=True,
                ),
            ],
            spacing=4,
            tight=True,
        ),
        padding=padding_symmetric(horizontal=12, vertical=8),
        bgcolor=COLOR_TARJETA,
        border_radius=8,
        border=borde_all(1, COLOR_BORDE),
    )




def crear_dialogo_explicativo_modos(page: ft.Page) -> ft.AlertDialog:
    """Genera un modal interactivo completo con la comparativa conceptual entre Modo Baseline y Optimizado."""
    filas_tabla = [
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Búsqueda de Productos", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO, size=12)),
                ft.DataCell(ft.Text("Lineal O(n)\nRecorrido secuencial de lista", color=COLOR_ADVERTENCIA, size=11)),
                ft.DataCell(ft.Text("Hash O(1) amort.\nDict + Índice Invertido + LRU", color=COLOR_EXITO, size=11)),
                ft.DataCell(ft.Text("Acceso inmediato sin importar tamaño de catálogo.", color=COLOR_TEXTO_SECUNDARIO, size=11)),
            ]
        ),
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Batch Picking (Agrupación)", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO, size=12)),
                ft.DataCell(ft.Text("Anidada O(P·L·n)\nBúsqueda por línea y pedido", color=COLOR_ADVERTENCIA, size=11)),
                ft.DataCell(ft.Text("Consolidada O(L)\n1 pasada con acumulación hash", color=COLOR_EXITO, size=11)),
                ft.DataCell(ft.Text("Elimina el producto cartesiano en almacén.", color=COLOR_TEXTO_SECUNDARIO, size=11)),
            ]
        ),
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Ranking Top-N", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO, size=12)),
                ft.DataCell(ft.Text("Sort Global O(N log N)\nOrdena todo el catálogo", color=COLOR_ADVERTENCIA, size=11)),
                ft.DataCell(ft.Text("Heap O(N log k)\nMin-Heap acotado a k nodos", color=COLOR_EXITO, size=11)),
                ft.DataCell(ft.Text("Memoria O(k) constante sin ordenar N completo.", color=COLOR_TEXTO_SECUNDARIO, size=11)),
            ]
        ),
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Alternativas Sustitutas", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO, size=12)),
                ft.DataCell(ft.Text("Recursión O(2^N)\nExplosión combinatorial", color=COLOR_ADVERTENCIA, size=11)),
                ft.DataCell(ft.Text("DP Memoizada O(N·P)\nReutilización de subproblemas", color=COLOR_EXITO, size=11)),
                ft.DataCell(ft.Text("Explora miles de opciones en milisegundos.", color=COLOR_TEXTO_SECUNDARIO, size=11)),
            ]
        ),
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Caché de Consultas", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO, size=12)),
                ft.DataCell(ft.Text("Sin Caché\nRecálculo repetido", color=COLOR_ADVERTENCIA, size=11)),
                ft.DataCell(ft.Text("LRU Reactiva O(1)\nInvalidación por mutación de stock", color=COLOR_EXITO, size=11)),
                ft.DataCell(ft.Text("Evita consultas redundantes sin datos obsoletos.", color=COLOR_TEXTO_SECUNDARIO, size=11)),
            ]
        ),
        ft.DataRow(
            cells=[
                ft.DataCell(ft.Text("Procesamiento de Pedidos", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO, size=12)),
                ft.DataCell(ft.Text("Secuencial O(P·L)\nMono-hilo atado al GIL", color=COLOR_ADVERTENCIA, size=11)),
                ft.DataCell(ft.Text("Concurrente O((P·L)/C + IPC)\nProcessPoolExecutor", color=COLOR_EXITO, size=11)),
                ft.DataCell(ft.Text("Paralelismo real multivariado en lotes masivos.", color=COLOR_TEXTO_SECUNDARIO, size=11)),
            ]
        ),
    ]

    tabla_comparativa = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Operación", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO, size=12)),
            ft.DataColumn(ft.Text("Modo Baseline", weight=ft.FontWeight.BOLD, color=COLOR_ADVERTENCIA, size=12)),
            ft.DataColumn(ft.Text("Modo Optimizado O(1)", weight=ft.FontWeight.BOLD, color=COLOR_EXITO, size=12)),
            ft.DataColumn(ft.Text("Justificación Técnica", weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_SECUNDARIO, size=12)),
        ],
        rows=filas_tabla,
        heading_row_color=COLOR_SUPERFICIE,
        border=borde_all(1, COLOR_BORDE),
        border_radius=8,
    )

    def cerrar_dialogo(_):
        if hasattr(page, "pop_dialog") and callable(page.pop_dialog):
            page.pop_dialog()
        elif hasattr(page, "close") and callable(page.close):
            page.close(dlg)
        else:
            dlg.open = False
            actualizar_control(page)


    dlg = ft.AlertDialog(
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.COMPARE_ARROWS_ROUNDED, size=24, color=COLOR_PRIMARIO),
                ft.Text("Diferencias Arquitecturales: Baseline vs. Optimizado", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
            ],
            spacing=8,
        ),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "El sistema implementa dos versiones simultáneas para cada operación fundamental del almacén. "
                        "Esto permite contrastar empíricamente en la defensa oral cómo la elección de algoritmos y estructuras de datos "
                        "transforma la escalabilidad y el consumo de recursos:",
                        size=13,
                        color=COLOR_TEXTO_SECUNDARIO,
                    ),
                    ft.Container(height=8),
                    tabla_comparativa,
                ],
                spacing=8,
                scroll=ft.ScrollMode.AUTO,
                tight=True,
            ),
            width=850,
        ),
        actions=[
            ft.FilledButton(
                "Entendido",
                style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color="#FFFFFF"),
                on_click=cerrar_dialogo,
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        bgcolor=COLOR_TARJETA,
    )
    return dlg
