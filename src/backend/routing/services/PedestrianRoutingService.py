"""Service that owns the controlled pedestrian-network cache."""
from __future__ import annotations

from collections.abc import Mapping
from threading import Lock
from typing import Any
from types import MappingProxyType

from routing.utils.DatasetFileManager import DatasetFileManager
from routing.utils.DatasetValidator import DatasetValidator
from routing.utils.GraphCalculator import Coordinate, Edge, GraphCalculator


class PedestrianRoutingService:
    """Loads a configured source once and exposes immutable route queries."""

    def __init__(self, dataset_path: str):
        self._dataset_path = dataset_path
        self._adjacency: Mapping[Coordinate, tuple[Edge, ...]] | None = None
        self._lock = Lock()

    def get_closest_node(self, point: Coordinate) -> tuple[Coordinate, float]:
        adjacency = self._get_adjacency()
        return GraphCalculator.find_closest_node(tuple(adjacency), point)

    def get_route(
        self,
        origin: Coordinate,
        destination: Coordinate,
        risk_weight: float,
    ) -> dict[str, Any]:
        adjacency = self._get_adjacency()
        path, edges, start, start_offset, goal, goal_offset = GraphCalculator.find_shortest_path(
            adjacency,
            origin,
            destination,
            risk_weight,
        )
        length_m = sum(edge.length_m for edge in edges)
        exposure = sum(edge.length_m * edge.risk for edge in edges)
        return {
            "coordinates": [{"lat": latitude, "lng": longitude} for longitude, latitude in path],
            "distance_m": round(length_m, 1),
            "risk_score": round(exposure / length_m, 1) if length_m else 0,
            "origin_node": self._format_node(start, start_offset),
            "destination_node": self._format_node(goal, goal_offset),
        }

    def refresh(self) -> None:
        """Reloads the source and atomically replaces its derived representation."""
        new_adjacency = self._load_adjacency()
        with self._lock:
            self._adjacency = new_adjacency

    def warm_up(self) -> int:
        """Build the read-only graph during startup when the runtime allows it.

        Calling this is optional: route requests use the same synchronized lazy
        initialization path when a serverless instance starts cold.
        """
        return len(self._get_adjacency())

    def _get_adjacency(self) -> Mapping[Coordinate, tuple[Edge, ...]]:
        """Return the cached graph or initialize it once for this process."""
        if self._adjacency is None:
            with self._lock:
                if self._adjacency is None:
                    self._adjacency = self._load_adjacency()
        return self._adjacency

    def _load_adjacency(self) -> Mapping[Coordinate, tuple[Edge, ...]]:
        rows = DatasetFileManager.read_rows(self._dataset_path)
        DatasetValidator.validate_or_raise(rows)
        return MappingProxyType(GraphCalculator.build_graph(rows))

    @staticmethod
    def _format_node(node: Coordinate, offset_m: float) -> dict[str, float]:
        return {"lat": node[1], "lng": node[0], "offset_m": round(offset_m, 1)}
