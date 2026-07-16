"""Pure calculations for building and traversing the pedestrian network."""
from __future__ import annotations

import heapq
import math
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from routing.exceptions import DatasetUnavailableError, RouteNotFoundError

Coordinate = tuple[float, float]


@dataclass(frozen=True)
class Edge:
    target: Coordinate
    length_m: float
    risk: float


class GraphCalculator:
    """Agrupa operaciones deterministas que no mantienen estado de solicitud."""

    @staticmethod
    def build_graph(rows: list[dict[str, str]]) -> dict[Coordinate, tuple[Edge, ...]]:
        adjacency: dict[Coordinate, list[Edge]] = defaultdict(list)
        raw_risks = [
            numeric_risk
            for row in rows
            if (numeric_risk := GraphCalculator._parse_optional_risk(row.get("harassmentRisk"))) is not None
        ]
        fallback_risk = sum(raw_risks) / len(raw_risks) if raw_risks else 0.0
        max_risk = max(*raw_risks, fallback_risk, 1.0)
        for row in rows:
            try:
                origin = GraphCalculator.parse_coordinate(row["origin"])
                destination = GraphCalculator.parse_coordinate(row["destination"])
                length_m = max(float(row["length"]), 0.1)
                raw_risk = GraphCalculator._parse_optional_risk(row.get("harassmentRisk"))
                raw_risk = fallback_risk if raw_risk is None else raw_risk
            except (KeyError, TypeError, ValueError):
                continue
            risk = min(100.0, max(0.0, raw_risk / max_risk * 100.0))
            adjacency[origin].append(Edge(destination, length_m, risk))
            adjacency[destination].append(Edge(origin, length_m, risk))
        if not adjacency:
            raise DatasetUnavailableError("The source contains no valid pedestrian segments.")
        return {node: tuple(edges) for node, edges in adjacency.items()}

    @staticmethod
    def find_closest_node(
        nodes: tuple[Coordinate, ...],
        point: Coordinate,
    ) -> tuple[Coordinate, float]:
        node = min(nodes, key=lambda candidate: GraphCalculator.calculate_distance_m(point, candidate))
        return node, GraphCalculator.calculate_distance_m(point, node)

    @staticmethod
    def find_shortest_path(
        adjacency: Mapping[Coordinate, tuple[Edge, ...]],
        origin: Coordinate,
        destination: Coordinate,
        risk_weight: float,
    ) -> tuple[list[Coordinate], list[Edge], Coordinate, float, Coordinate, float]:
        nodes = tuple(adjacency)
        start, start_offset = GraphCalculator.find_closest_node(nodes, origin)
        goal, goal_offset = GraphCalculator.find_closest_node(nodes, destination)
        queue: list[tuple[float, Coordinate]] = [(0.0, start)]
        costs = {start: 0.0}
        previous: dict[Coordinate, tuple[Coordinate, Edge]] = {}
        while queue:
            cost, node = heapq.heappop(queue)
            if cost != costs.get(node):
                continue
            if node == goal:
                break
            for edge in adjacency[node]:
                next_cost = cost + edge.length_m * (1 + risk_weight * edge.risk / 100)
                if next_cost < costs.get(edge.target, math.inf):
                    costs[edge.target] = next_cost
                    previous[edge.target] = (node, edge)
                    heapq.heappush(queue, (next_cost, edge.target))
        if goal not in previous and start != goal:
            raise RouteNotFoundError("No existe una ruta conectada entre los puntos seleccionados.")
        path, edges = GraphCalculator.build_path(start, goal, previous)
        return path, edges, start, start_offset, goal, goal_offset

    @staticmethod
    def build_path(
        start: Coordinate,
        goal: Coordinate,
        previous: dict[Coordinate, tuple[Coordinate, Edge]],
    ) -> tuple[list[Coordinate], list[Edge]]:
        path, edges = [goal], []
        current = goal
        while current != start:
            current, edge = previous[current]
            path.append(current)
            edges.append(edge)
        return list(reversed(path)), list(reversed(edges))

    @staticmethod
    def parse_coordinate(value: str) -> Coordinate:
        longitude, latitude = value.strip().strip("()").split(",")
        return float(longitude), float(latitude)

    @staticmethod
    def _parse_optional_risk(value: str | None) -> float | None:
        if value is None or not value.strip():
            return None
        return float(value)

    @staticmethod
    def calculate_distance_m(first: Coordinate, second: Coordinate) -> float:
        lon1, lat1, lon2, lat2 = map(math.radians, (*first, *second))
        a = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
        return 6_371_000 * 2 * math.asin(math.sqrt(a))
