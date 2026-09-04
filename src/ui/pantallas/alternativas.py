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
    crear_tarjeta_kpi,
    crear_banner_explicativo,
    crear_badge_tiempo,
    crear_dropdown,
)


class PantallaAlternativas(ft.Container):
    """Vista para encontrar combinaciones de sustitutos con y sin memoización."""

    def __init__(self, motor: MotorInventario, on_actualizar_panel, notificar) -> None:
        super().__init__()
        self.motor = motor
        self.on_actualizar_panel = on_actualizar_panel
        self.notificar = notificar
        self.expand = True
        self.padding = padding_symmetric(horizontal=16, vertical=10)

        self.combinaciones_actuales = []
        self.orden_ascendente = True

        categorias_disponibles = sorted({p.categoria for p in self.motor.catalogo.obtener_todos()})
        cat_inicial = categorias_disponibles[0] if categorias_disponibles else "Ferretería y Herramientas"

        self.dropdown_categoria = crear_dropdown(
            label="Categoría del sustituto",
            options=[ft.dropdown.Option(cat, cat) for cat in categorias_disponibles],
            value=cat_inicial,
            width=280,
        )

        self.input_presupuesto = ft.TextField(
            label="Presupuesto máx ($)",
            value="45000",
            border_color=COLOR_BORDE,
            focused_border_color=COLOR_PRIMARIO,
            color=COLOR_TEXTO_PRIMARIO,
            width=160,
            dense=True,
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        self.switch_memo = ft.Switch(
            label="Memoización (DP)",
            value=True,
            active_color=COLOR_PRIMARIO,
        )

        self.btn_buscar = ft.FilledButton(
            "Calcular",
            icon=ft.Icons.AUTO_AWESOME_ROUNDED,
            style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color="#FFFFFF"),
            on_click=lambda _: self._ejecutar_busqueda(),
        )

        # Controles de ordenamiento
        self.dropdown_orden = crear_dropdown(
            label="Ordenar por",
            options=[
                ft.dropdown.Option("precio", "Precio Total ($)"),
                ft.dropdown.Option("ajuste", "Ajuste al Presupuesto"),
                ft.dropdown.Option("items", "Cantidad de Artículos"),
            ],
            value="precio",
            width=190,
            on_change_callback=lambda _: self._aplicar_ordenamiento(),
        )

        self.btn_sentido_orden = ft.IconButton(
            icon=ft.Icons.ARROW_UPWARD_ROUNDED,
            tooltip="Orden Ascendente (Clic para alternar)",
            on_click=lambda _: self._alternar_sentido_orden(),
        )

        self.fila_kpis = ft.Row(spacing=8)
        self.col_combinaciones = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, expand=True)

        self._construir_interfaz()
        try:
            self._ejecutar_busqueda()
        except Exception:
            pass

    def _construir_interfaz(self) -> None:
        self.content = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("Cálculo de Alternativas y Combinaciones Sustitutas", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                ft.Text("Demostración experimental de Memoización: Árbol recursivo exhaustivo O(2^N) vs. Programación Dinámica O(N * P)", size=12, color=COLOR_TEXTO_SECUNDARIO),
                            ],
                            spacing=1,
                        ),
                        ft.Container(expand=True),
                        self.btn_buscar,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=6, color=COLOR_BORDE),
                # Banner explicativo didáctico
                crear_banner_explicativo(
                    titulo="Sustitutos y Programación Dinámica",
                    descripcion="Explora combinaciones de productos dentro de una categoría para suplir faltantes de stock respetando un presupuesto máximo.",
                    complejidad_base="Árbol Recursivo Exhaustivo O(2^N)",
                    complejidad_opt="Programación Dinámica Memoizada O(N·P)",
                    por_que_importa="La memoización de subproblemas previene la explosión exponencial O(2^N), permitiendo encontrar combinaciones óptimas en menos de 1 milisegundo.",
                ),
                # Barra de configuración y parámetros compacta
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.dropdown_categoria,
                            self.input_presupuesto,
                            self.switch_memo,
                            ft.VerticalDivider(width=1, color=COLOR_BORDE),
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
                ft.Text("Combinaciones Sustitutas Encontradas (Clic para desplegar productos)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                self.col_combinaciones,
            ],
            spacing=6,
            expand=True,
        )

    def al_recargar_dataset(self) -> None:
        """Callback al recargar dataset."""
        categorias_disponibles = sorted({p.categoria for p in self.motor.catalogo.obtener_todos()})
        cat_inicial = categorias_disponibles[0] if categorias_disponibles else "Ferretería y Herramientas"
        self.dropdown_categoria.options = [ft.dropdown.Option(cat, cat) for cat in categorias_disponibles]
        self.dropdown_categoria.value = cat_inicial
        actualizar_control(self.dropdown_categoria)
        self._ejecutar_busqueda()

    def al_cambiar_estrategia_global(self, nueva_estrategia: str) -> None:
        """Sincroniza el switch de memoización con la estrategia global."""
        self.switch_memo.value = (nueva_estrategia == "optimizado")
        actualizar_control(self.switch_memo)
        self._ejecutar_busqueda()

    def _alternar_sentido_orden(self):
        self.orden_ascendente = not self.orden_ascendente
        self.btn_sentido_orden.icon = ft.Icons.ARROW_UPWARD_ROUNDED if self.orden_ascendente else ft.Icons.ARROW_DOWNWARD_ROUNDED
        self.btn_sentido_orden.tooltip = "Orden Ascendente" if self.orden_ascendente else "Orden Descendente"
        actualizar_control(self.btn_sentido_orden)
        self._aplicar_ordenamiento()

    def _aplicar_ordenamiento(self):
        criterio = self.dropdown_orden.value or "precio"

        def clave(comb):
            precio_total = comb.costo_total
            if criterio == "precio":
                return precio_total
            elif criterio == "ajuste":
                try:
                    presupuesto = float(self.input_presupuesto.value or "45000")
                except ValueError:
                    presupuesto = 45000.0
                return abs(presupuesto - precio_total)
            elif criterio == "items":
                return len(comb.productos)
            return precio_total

        self.combinaciones_actuales.sort(key=clave, reverse=not self.orden_ascendente)
        self._renderizar_combinaciones()

    def _ejecutar_busqueda(self):
        categoria = self.dropdown_categoria.value or "Ferretería y Herramientas"
        try:
            presupuesto = float(self.input_presupuesto.value or "45000")
        except ValueError:
            presupuesto = 45000.0
            self.input_presupuesto.value = "45000"

        usar_memo = self.switch_memo.value

        try:
            resultado = self.motor.buscar_alternativas(
                categoria=categoria,
                presupuesto_maximo=presupuesto,
                forzar_memoizacion=usar_memo,
                max_combinaciones=20,
                max_candidatos=35,
            )
        except Exception as err:
            self.notificar(f"Error al calcular combinaciones: {err}", ft.Icons.ERROR_OUTLINE, COLOR_PELIGRO)
            return


        # Actualizar KPIs
        self.fila_kpis.controls = [
            crear_tarjeta_kpi("Combinaciones Halladas", f"{resultado.total_combinaciones:,}", f"Presupuesto: ${presupuesto:,.0f}", ft.Icons.AUTO_AWESOME, COLOR_PRIMARIO),
            crear_tarjeta_kpi("Tiempo de Exploración", f"{resultado.tiempo_ejecucion_ms:.3f} ms", f"{'DP con Memo' if usar_memo else 'Árbol Recursivo'}", ft.Icons.SPEED, COLOR_EXITO),
            crear_tarjeta_kpi("Llamadas Reutilizadas", f"{resultado.hits_memo:,}", "Subproblemas cacheados", ft.Icons.SAVED_SEARCH, COLOR_SECUNDARIO),
            crear_tarjeta_kpi("Complejidad Teórica", "O(N * P)" if usar_memo else "O(2^N)", "Pseudo-polinomial" if usar_memo else "Exponencial", ft.Icons.FUNCTIONS, COLOR_PRIMARIO),
        ]

        self.combinaciones_actuales = list(resultado.combinaciones)
        self._aplicar_ordenamiento()

        self.on_actualizar_panel(
            dataset="activo",
            n_productos=len(self.motor.catalogo),
            n_pedidos=len(self.motor.pedidos),
            estrategia=self.motor.estrategia,
            tiempo_ms=resultado.tiempo_ejecucion_ms,
            resultado_negocio=f"{resultado.total_combinaciones} combinaciones en {categoria}",
        )
        actualizar_control(self)

    def _renderizar_combinaciones(self):
        try:
            presupuesto = float(self.input_presupuesto.value or "45000")
        except ValueError:
            presupuesto = 45000.0

        items = []
        for i, comb in enumerate(self.combinaciones_actuales, 1):
            costo_total = comb.costo_total
            diferencia = presupuesto - costo_total
            porc_uso = (costo_total / presupuesto * 100.0) if presupuesto > 0 else 0.0

            # Desglose de cada producto en la combinación
            filas_prods = []
            for p in comb.productos:
                filas_prods.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(f"#{p.id}", size=12, color=COLOR_PRIMARIO, weight=ft.FontWeight.BOLD, width=50),
                                ft.Text(p.nombre, size=13, color=COLOR_TEXTO_PRIMARIO, expand=True),
                                ft.Text(f"Stock: {p.stock} Unidades", size=12, color=COLOR_TEXTO_SECUNDARIO, width=130),
                                ft.Text(f"${p.precio:,.2f}", size=13, color=COLOR_EXITO, weight=ft.FontWeight.BOLD, width=90),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=padding_symmetric(horizontal=8, vertical=3),
                    )
                )

            desglose = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Divider(height=1, color=COLOR_BORDE),
                        ft.Text("Artículos sustitutos que integran la combinación:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_MUTED),
                        *filas_prods,
                    ],
                    spacing=4,
                ),
                padding=padding_symmetric(horizontal=12, vertical=6),
                bgcolor=COLOR_TARJETA,
            )

            tile = ft.ExpansionTile(
                leading=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=COLOR_EXITO, size=20),
                title=ft.Text(f"Alternativa #{i}: {len(comb.productos)} productos sustitutos", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                subtitle=ft.Text(f"Total: ${costo_total:,.2f} ({porc_uso:.1f}% del presupuesto) | Remanente: ${diferencia:,.2f}", size=12, color=COLOR_TEXTO_SECUNDARIO),
                trailing=ft.Container(
                    content=ft.Text(f"${costo_total:,.2f}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_EXITO),
                    padding=padding_symmetric(horizontal=8, vertical=4),
                    bgcolor=COLOR_TARJETA,
                    border_radius=6,
                    border=borde_all(1, COLOR_BORDE),
                ),
                controls=[desglose],
            )
            items.append(tile)

        if not items:
            items.append(
                ft.Container(
                    content=ft.Text(
                        "No se hallaron combinaciones viables dentro del presupuesto en esta categoría.",
                        size=13,
                        color=COLOR_TEXTO_MUTED,
                    ),
                    padding=20,
                )
            )

        self.col_combinaciones.controls = items
        actualizar_control(self)

