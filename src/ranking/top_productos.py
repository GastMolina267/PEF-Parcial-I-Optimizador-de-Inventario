"""Módulo para el cálculo de productos más solicitados (Top-N).

Incluye la implementación baseline basada en ordenamiento completo O(N log N)
que se comparará con la versión optimizada con heaps (O(N log k)) en la Etapa 3.
"""

from __future__ import annotations
from typing import Sequence
from src.modelos.pedido import Pedido
from src.modelos.producto import Producto
from src.inventario.catalogo_lineal import CatalogoLineal


def calcular_top_solicitados_lineal(
    pedidos: Sequence[Pedido],
    catalogo: CatalogoLineal,
    k: int = 10,
) -> list[tuple[Producto, int]]:
    """Calcula los k productos más solicitados utilizando ordenamiento total (Baseline).

    Estrategia algorítmica:
    1. Agrega las cantidades demandadas de cada producto a través de todos los pedidos.
    2. Ordena la totalidad de la lista de frecuencias acumuladas de mayor a menor (O(N log N)).
    3. Corta los primeros k elementos ([:k]).
    4. Resuelve cada id contra el catálogo lineal (O(k * N)).

    Complejidad temporal total: O(L + N log N + k * N),
    donde L es el total de líneas de pedido y N la cantidad de productos distintos.
    """
    if k <= 0:
        return []

    # 1. Agregación de frecuencias acumuladas
    # Usamos una lista de tuplas / diccionario temporal para contabilizar
    frecuencias: dict[int, int] = {}
    for pedido in pedidos:
        for linea in pedido.lineas:
            frecuencias[linea.id_producto] = frecuencias.get(linea.id_producto, 0) + linea.cantidad

    if not frecuencias:
        return []

    # 2. Ordenamiento completo de TODAS las frecuencias (O(N log N))
    items_ordenados = sorted(frecuencias.items(), key=lambda item: item[1], reverse=True)

    # 3. Selección de los primeros k
    top_k_items = items_ordenados[:k]

    # 4. Resolución de objetos Producto en el catálogo lineal (O(k * N_cat))
    resultado: list[tuple[Producto, int]] = []
    for id_prod, total_solicitado in top_k_items:
        producto = catalogo.buscar_por_id(id_prod)
        if producto is not None:
            resultado.append((producto, total_solicitado))

    return resultado
