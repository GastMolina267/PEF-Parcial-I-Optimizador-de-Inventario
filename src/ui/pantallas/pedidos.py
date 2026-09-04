"""Pantalla de Preparación y Procesamiento de Pedidos con Despliegue Detallado."""

from __future__ import annotations
import flet as ft
from src.motor.motor_inventario import MotorInventario
from src.ui.tema import (
    COLOR_BORDE,
    COLOR_EXITO,
    COLOR_FONDO_ADVERTENCIA,
    COLOR_FONDO_EXITO,
    COLOR_FONDO_PELIGRO,
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
    crear_banner_explicativo,
    crear_badge_tiempo,
    crear_dropdown,
)


class PantallaPedidos(ft.Container):
    """Vista para procesar lotes de pedidos de forma secuencial o concurrente con despliegue línea por línea."""

    def __init__(self, motor: MotorInventario, on_actualizar_panel, notificar) -> None:
        super().__init__()
        self.motor = motor
        self.on_actualizar_panel = on_actualizar_panel
        self.notificar = notificar
        self.expand = True
        self.padding = padding_symmetric(horizontal=16, vertical=10)
        self.pedidos_actuales = []

        self.resultados_ultimo_proceso = None
        self.orden_ascendente = True

        # Controles
        self.switch_concurrente = ft.Switch(
            label="Procesamiento Concurrente (ProcessPoolExecutor)",
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

        # Controles de ordenamiento
        self.dropdown_orden = crear_dropdown(
            label="Ordenar pedidos por",
            options=[
                ft.dropdown.Option("id", "ID del Pedido"),
                ft.dropdown.Option("estado", "Estado de Cobertura"),
                ft.dropdown.Option("lineas", "Cantidad de Líneas"),
                ft.dropdown.Option("unidades", "Total Unidades Requeridas"),
            ],
            value="id",
            width=220,
            on_change_callback=lambda _: self._aplicar_ordenamiento(),
        )

        self.btn_sentido_orden = ft.IconButton(
            icon=ft.Icons.ARROW_UPWARD_ROUNDED,
            tooltip="Orden Ascendente (Clic para alternar a Descendente)",
            on_click=lambda _: self._alternar_sentido_orden(),
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
                                ft.Text("Preparación de Pedidos en Lote", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                                ft.Text("Evaluación de disponibilidad: Mono-hilo secuencial vs. ProcessPoolExecutor (CPU-bound)", size=12, color=COLOR_TEXTO_SECUNDARIO),
                            ],
                            spacing=1,
                        ),
                        ft.Container(expand=True),
                        self.btn_procesar,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=6, color=COLOR_BORDE),
                # Banner explicativo didáctico
                crear_banner_explicativo(
                    titulo="Preparación de Pedidos y Evaluación Concurrente",
                    descripcion="Evaluación de satisfacción de demanda: verificación mono-hilo secuencial frente a ProcessPoolExecutor con chunking para evadir el GIL.",
                    complejidad_base="Secuencial O(P·L)",
                    complejidad_opt="Paralelo O((P·L)/C + IPC)",
                    por_que_importa="Permite evidenciar el punto de equilibrio (break-even): en lotes masivos supera el GIL, mientras que en lotes pequeños el costo de IPC domina.",
                ),
                # Panel de configuración y ordenamiento
                ft.Container(
                    content=ft.Row(
                        controls=[
                            self.switch_concurrente,
                            ft.VerticalDivider(width=1, color=COLOR_BORDE),
                            self.check_descontar_stock,
                            ft.VerticalDivider(width=1, color=COLOR_BORDE),
                            self.dropdown_orden,
                            self.btn_sentido_orden,
                        ],
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=padding_symmetric(horizontal=10, vertical=5),
                    bgcolor=COLOR_TARJETA,
                    border_radius=8,
                    border=borde_all(1, COLOR_BORDE),
                ),
                self.fila_kpis,
                ft.Text("Listado de Pedidos (Clic en cada pedido para desplegar líneas y stock disponible)", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                self.col_pedidos,
            ],
            spacing=6,
            expand=True,
        )


    def al_recargar_dataset(self) -> None:
        """Callback al cargar un nuevo dataset desde la pantalla Inicio."""
        self.resultados_ultimo_proceso = None
        self._actualizar_kpis_iniciales()

    def al_cambiar_estrategia_global(self, nueva_estrategia: str) -> None:
        """Sincroniza el switch de concurrencia cuando cambia la estrategia global."""
        self.switch_concurrente.value = (nueva_estrategia == "optimizado")
        actualizar_control(self.switch_concurrente)

    def _alternar_sentido_orden(self):
        self.orden_ascendente = not self.orden_ascendente
        self.btn_sentido_orden.icon = ft.Icons.ARROW_UPWARD_ROUNDED if self.orden_ascendente else ft.Icons.ARROW_DOWNWARD_ROUNDED
        self.btn_sentido_orden.tooltip = "Orden Ascendente" if self.orden_ascendente else "Orden Descendente"
        actualizar_control(self.btn_sentido_orden)
        self._aplicar_ordenamiento()

    def _actualizar_kpis_iniciales(self):
        total_peds = len(self.motor.pedidos)
        self.fila_kpis.controls = [
            crear_tarjeta_kpi("Total Pedidos", f"{total_peds:,}", "En cola de preparación", ft.Icons.RECEIPT_LONG, COLOR_PRIMARIO),
            crear_tarjeta_kpi("Cubiertos", "--", "100% de stock disponible", ft.Icons.CHECK_CIRCLE, COLOR_EXITO),
            crear_tarjeta_kpi("Parciales", "--", "Stock parcial o faltantes", ft.Icons.WARNING, "#F59E0B"),
            crear_tarjeta_kpi("Imposibles", "--", "Sin stock disponible", ft.Icons.CANCEL, COLOR_PELIGRO),
        ]
        self.pedidos_actuales = list(self.motor.pedidos)
        self._aplicar_ordenamiento()

    def _aplicar_ordenamiento(self):
        criterio = self.dropdown_orden.value or "id"

        if self.resultados_ultimo_proceso:
            # Ordenar resultados procesados
            def clave_res(r):
                if criterio == "estado":
                    orden_estado = {"cubierto": 0, "parcial": 1, "imposible": 2}
                    return orden_estado.get(r.estado.value.lower(), 3)
                elif criterio == "lineas":
                    return len(r.lineas_cubiertas) + len(r.lineas_faltantes)
                elif criterio == "unidades":
                    p = next((ped for ped in self.motor.pedidos if ped.id == r.id_pedido), None)
                    return sum(lp.cantidad for lp in p.lineas) if p else 0
                return r.id_pedido

            self.resultados_ultimo_proceso.sort(key=clave_res, reverse=not self.orden_ascendente)
            self._renderizar_resultados_procesados()
        else:
            # Ordenar pedidos no procesados
            def clave_ped(p):
                if criterio == "lineas":
                    return len(p.lineas)
                elif criterio == "unidades":
                    return sum(lp.cantidad for lp in p.lineas)
                return p.id

            self.pedidos_actuales.sort(key=clave_ped, reverse=not self.orden_ascendente)
            self._renderizar_pedidos_sin_procesar()

    def _renderizar_pedidos_sin_procesar(self):
        items = []
        max_mostrar = 100
        for ped in self.pedidos_actuales[:max_mostrar]:
            total_unidades = sum(l.cantidad for l in ped.lineas)

            # Construir desglose de líneas desplegables
            filas_lineas = []
            precio_total_estimado = 0.0
            for l in ped.lineas:
                prod = self.motor.buscar_por_id(l.id_producto)
                nombre_p = prod.nombre if prod else f"Producto #{l.id_producto}"
                stock_p = prod.stock if prod else 0
                precio_p = prod.precio if prod else 0.0
                subtotal = precio_p * l.cantidad
                precio_total_estimado += subtotal

                if stock_p >= l.cantidad:
                    badge_linea = ft.Container(
                        content=ft.Text(f"Cubierta (Stock: {stock_p})", size=11, color=COLOR_EXITO, weight=ft.FontWeight.BOLD),
                        bgcolor=COLOR_FONDO_EXITO,
                        padding=padding_symmetric(horizontal=8, vertical=3),
                        border_radius=6,
                    )
                elif stock_p > 0:
                    badge_linea = ft.Container(
                        content=ft.Text(f"Parcial (Stock: {stock_p} / Falta: {l.cantidad - stock_p})", size=11, color="#F59E0B", weight=ft.FontWeight.BOLD),
                        bgcolor=COLOR_FONDO_ADVERTENCIA,
                        padding=padding_symmetric(horizontal=8, vertical=3),
                        border_radius=6,
                    )
                else:
                    badge_linea = ft.Container(
                        content=ft.Text("Sin Stock en Almacén", size=11, color=COLOR_PELIGRO, weight=ft.FontWeight.BOLD),
                        bgcolor=COLOR_FONDO_PELIGRO,
                        padding=padding_symmetric(horizontal=8, vertical=3),
                        border_radius=6,
                    )

                filas_lineas.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(f"#{l.id_producto}", size=12, color=COLOR_PRIMARIO, weight=ft.FontWeight.BOLD, width=50),
                                ft.Text(nombre_p, size=13, color=COLOR_TEXTO_PRIMARIO, expand=True),
                                ft.Text(f"Pedido: {l.cantidad} Unidades", size=12, color=COLOR_TEXTO_SECUNDARIO, width=140),
                                ft.Text(f"${subtotal:,.2f}", size=12, color=COLOR_TEXTO_PRIMARIO, weight=ft.FontWeight.W_600, width=90),
                                badge_linea,
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        padding=padding_symmetric(horizontal=8, vertical=4),
                    )
                )

            desglose = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Divider(height=1, color=COLOR_BORDE),
                        ft.Text("Auditoría de líneas requeridas vs. existencias:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_MUTED),
                        *filas_lineas,
                        ft.Divider(height=1, color=COLOR_BORDE),
                        ft.Row(
                            controls=[
                                ft.Text(f"Subtotal estimado: ${precio_total_estimado:,.2f}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    spacing=6,
                ),
                padding=padding_symmetric(horizontal=12, vertical=8),
                bgcolor=COLOR_TARJETA,
            )

            tile = ft.ExpansionTile(
                leading=ft.Icon(ft.Icons.RECEIPT_OUTLINED, color=COLOR_PRIMARIO, size=20),
                title=ft.Text(f"Pedido #{ped.id}", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                subtitle=ft.Text(f"{len(ped.lineas)} líneas demandadas | {total_unidades} Unidades en total", size=12, color=COLOR_TEXTO_MUTED),
                trailing=ft.Container(
                    content=ft.Text("Pendiente", size=11, color=COLOR_TEXTO_MUTED, weight=ft.FontWeight.BOLD),
                    padding=padding_symmetric(horizontal=8, vertical=3),
                    border=borde_all(1, COLOR_BORDE),
                    border_radius=6,
                ),
                controls=[desglose],
            )
            items.append(tile)

        self.col_pedidos.controls = items
        actualizar_control(self)

    def _renderizar_resultados_procesados(self):
        items = []
        max_mostrar = 100
        for r in self.resultados_ultimo_proceso[:max_mostrar]:
            total_lineas = len(r.lineas_cubiertas) + len(r.lineas_faltantes)
            porc_cobertura = (len(r.lineas_cubiertas) / total_lineas * 100.0) if total_lineas > 0 else 100.0

            filas_lineas = []
            for lf in r.lineas_faltantes:
                prod = self.motor.buscar_por_id(lf.id_producto)
                nombre_p = prod.nombre if prod else f"Producto #{lf.id_producto}"
                stock_p = prod.stock if prod else 0
                filas_lineas.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CANCEL_OUTLINED, size=14, color=COLOR_PELIGRO),
                                ft.Text(f"#{lf.id_producto} {nombre_p}", size=12, color=COLOR_PELIGRO, expand=True),
                                ft.Text(f"Pedido: {lf.cantidad_solicitada} Unidades", size=12, color=COLOR_TEXTO_SECUNDARIO, width=130),
                                ft.Text(f"Stock actual: {stock_p} Unidades", size=12, color=COLOR_TEXTO_MUTED, width=130),
                                ft.Text(f"Faltan: {lf.faltante} Unidades", size=12, color=COLOR_PELIGRO, weight=ft.FontWeight.BOLD, width=130),
                            ],
                        ),
                        padding=padding_symmetric(horizontal=8, vertical=3),
                    )
                )

            for lc in r.lineas_cubiertas:
                prod = self.motor.buscar_por_id(lc.id_producto)
                nombre_p = prod.nombre if prod else f"Producto #{lc.id_producto}"
                stock_p = prod.stock if prod else 0
                filas_lineas.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=14, color=COLOR_EXITO),
                                ft.Text(f"#{lc.id_producto} {nombre_p}", size=12, color=COLOR_EXITO, expand=True),
                                ft.Text(f"Pedido: {lc.cantidad_solicitada} Unidades", size=12, color=COLOR_TEXTO_SECUNDARIO, width=130),
                                ft.Text(f"Stock disponible: {stock_p} Unidades", size=12, color=COLOR_TEXTO_MUTED, width=130),
                                ft.Text("100% Satisfecho", size=12, color=COLOR_EXITO, weight=ft.FontWeight.BOLD, width=130),
                            ],
                        ),
                        padding=padding_symmetric(horizontal=8, vertical=3),
                    )
                )

            desglose = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Divider(height=1, color=COLOR_BORDE),
                        ft.Text(f"Auditoría de cumplimiento ({len(r.lineas_cubiertas)}/{total_lineas} líneas cubiertas - {porc_cobertura:.1f}%):", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_MUTED),
                        *filas_lineas,
                    ],
                    spacing=6,
                ),
                padding=padding_symmetric(horizontal=12, vertical=8),
                bgcolor=COLOR_TARJETA,
            )

            tile = ft.ExpansionTile(
                leading=ft.Icon(ft.Icons.RECEIPT_ROUNDED, color=COLOR_PRIMARIO, size=20),
                title=ft.Text(f"Pedido #{r.id_pedido}", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXTO_PRIMARIO),
                subtitle=ft.Text(f"{len(r.lineas_cubiertas)}/{total_lineas} líneas cubiertas ({porc_cobertura:.0f}%)", size=12, color=COLOR_TEXTO_SECUNDARIO),
                trailing=crear_badge_estado(r.estado.value),
                controls=[desglose],
            )
            items.append(tile)

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

            # Actualizar KPIs con badge de tiempo
            self.fila_kpis.controls = [
                crear_tarjeta_kpi("Total Procesados", f"{resumen.pedidos_procesados:,}", f"Tiempo: {resumen.tiempo_ejecucion_ms:.2f} ms", ft.Icons.RECEIPT_LONG, COLOR_PRIMARIO),
                crear_tarjeta_kpi("Cubiertos", f"{resumen.pedidos_cubiertos:,}", f"{resumen.porcentaje_cobertura:.1f}% del lote", ft.Icons.CHECK_CIRCLE, COLOR_EXITO),
                crear_tarjeta_kpi("Parciales", f"{resumen.pedidos_parciales:,}", "Faltante parcial", ft.Icons.WARNING, "#F59E0B"),
                crear_tarjeta_kpi("Imposibles", f"{resumen.pedidos_imposibles:,}", "Faltante total", ft.Icons.CANCEL, COLOR_PELIGRO),
            ]

            self.resultados_ultimo_proceso = list(resumen.resultados)
            self._aplicar_ordenamiento()

            modo_txt = "Concurrente (ProcessPoolExecutor)" if es_conc else "Secuencial"
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

    def al_cambiar_estrategia_global(self, nueva_estrategia: str) -> None:
        """Sincroniza el switch de procesamiento concurrente con la estrategia global."""
        es_opt = (nueva_estrategia == "optimizado")
        self.switch_concurrente.value = es_opt
        actualizar_control(self.switch_concurrente)

