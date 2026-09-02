"""Fachada unificada del Motor de Inventario y Pedidos.

Provee la interfaz común de alto nivel que consumen tanto la interfaz gráfica Flet
como los scripts de benchmarking y los tests automatizados.
Permite alternar entre la estrategia baseline y la estrategia optimizada.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Sequence
from src.modelos.producto import Producto
from src.modelos.pedido import Pedido, ResumenProcesamiento
from src.inventario.catalogo_lineal import CatalogoLineal
from src.pedidos.procesador_secuencial import procesar_pedidos_secuencial
from src.ranking.top_productos import calcular_top_solicitados_lineal
from src.datos.cargador import cargar_dataset_json


class MotorInventario:
    """Controlador central del dominio de inventario y pedidos."""

    def __init__(
        self,
        productos: Sequence[Producto] | None = None,
        pedidos: Sequence[Pedido] | None = None,
        estrategia: str = "baseline",
    ) -> None:
        """Inicializa el motor con una estrategia ('baseline' u 'optimizado').

        En la Etapa 2, la estrategia disponible es 'baseline' (Catálogo Lineal O(n)).
        En la Etapa 3 se integrará la estrategia 'optimizado' (Catálogo Hash O(1), Heaps, etc.).
        """
        self._estrategia = estrategia.lower()
        self._pedidos: list[Pedido] = list(pedidos) if pedidos else []

        if self._estrategia == "baseline":
            self._catalogo = CatalogoLineal(productos)
        else:
            # Reservado para la Etapa 3
            self._catalogo = CatalogoLineal(productos)

    @property
    def estrategia(self) -> str:
        """Estrategia algorítmica actualmente activa en el motor."""
        return self._estrategia

    @property
    def catalogo(self) -> CatalogoLineal:
        """Acceso al catálogo de inventario activo."""
        return self._catalogo

    @property
    def pedidos(self) -> list[Pedido]:
        """Lista de pedidos cargados en el motor."""
        return self._pedidos

    def cargar_dataset(self, ruta: str | Path) -> None:
        """Carga un dataset JSON en el motor, reemplazando los productos y pedidos actuales."""
        productos, pedidos = cargar_dataset_json(ruta)
        self.cargar_desde_listas(productos, pedidos)

    def cargar_desde_listas(
        self, productos: Sequence[Producto], pedidos: Sequence[Pedido]
    ) -> None:
        """Inicializa el motor directamente desde secuencias en memoria."""
        self._pedidos = list(pedidos)
        if self._estrategia == "baseline":
            self._catalogo = CatalogoLineal(productos)
        else:
            self._catalogo = CatalogoLineal(productos)

    def buscar_por_id(self, id_producto: int) -> Producto | None:
        """Busca un producto por su identificador único."""
        return self._catalogo.buscar_por_id(id_producto)

    def buscar_por_nombre(self, texto: str) -> list[Producto]:
        """Busca productos por coincidencia parcial de texto en su denominación."""
        return self._catalogo.buscar_por_nombre(texto)

    def buscar_por_categoria(self, categoria: str) -> list[Producto]:
        """Busca productos pertenecientes a una categoría."""
        return self._catalogo.buscar_por_categoria(categoria)

    def procesar_pedidos(
        self,
        pedidos: Sequence[Pedido] | None = None,
        descontar_stock: bool = False,
        politica_descuento: str = "solo_cubiertos",
    ) -> ResumenProcesamiento:
        """Procesa un lote de pedidos frente al catálogo.

        Argumentos:
            pedidos: Lote de pedidos a preparar (si es None, usa los pedidos cargados en el motor).
            descontar_stock: Si True, muta el inventario reduciendo las unidades asignadas.
            politica_descuento: 'solo_cubiertos' (atómico) o 'todo_lo_posible'.
        """
        lote = pedidos if pedidos is not None else self._pedidos
        # En la Etapa 2 ejecutamos el procesador secuencial baseline
        return procesar_pedidos_secuencial(
            catalogo=self._catalogo,
            pedidos=lote,
            descontar_stock=descontar_stock,
            politica_descuento=politica_descuento,
        )

    def obtener_top_solicitados(
        self, k: int = 10, pedidos: Sequence[Pedido] | None = None
    ) -> list[tuple[Producto, int]]:
        """Determina los k productos con mayor demanda acumulada."""
        lote = pedidos if pedidos is not None else self._pedidos
        # En la Etapa 2 ejecutamos el algoritmo baseline (ordenamiento total)
        return calcular_top_solicitados_lineal(
            pedidos=lote, catalogo=self._catalogo, k=k
        )

    def obtener_estadisticas(self) -> dict[str, Any]:
        """Calcula métricas globales descriptivas del estado actual del almacén."""
        prods = self._catalogo.obtener_todos()
        stock_total = sum(p.stock for p in prods)
        categorias = sorted({p.categoria for p in prods})

        total_lineas_pedidos = sum(len(p.lineas) for p in self._pedidos)
        unidades_demandadas = sum(
            linea.cantidad for p in self._pedidos for linea in p.lineas
        )

        return {
            "estrategia": self._estrategia,
            "total_productos": len(prods),
            "stock_total_unidades": stock_total,
            "total_categorias": len(categorias),
            "categorias": categorias,
            "total_pedidos": len(self._pedidos),
            "total_lineas_pedidos": total_lineas_pedidos,
            "unidades_demandadas": unidades_demandadas,
        }
