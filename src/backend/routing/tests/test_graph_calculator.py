import csv

import pytest

from routing.utils.GraphCalculator import GraphCalculator


@pytest.fixture
def graph_rows() -> list[dict[str, str]]:
    content = (
        "name;origin;destination;length;oneway;harassmentRisk;geometry\n"
        "A;(0, 0);(0.001, 0);100;False;0;LINESTRING EMPTY\n"
        "B;(0.001, 0);(0.002, 0);100;True;1;LINESTRING EMPTY\n"
    )
    return list(csv.DictReader(content.splitlines(), delimiter=";"))


def test_find_shortest_path_walks_both_directions(graph_rows):
    adjacency = GraphCalculator.build_graph(graph_rows)

    path, _, _, _, _, _ = GraphCalculator.find_shortest_path(adjacency, (0.002, 0), (0, 0), risk_weight=0)

    assert path == [(0.002, 0.0), (0.001, 0.0), (0.0, 0.0)]


def test_find_shortest_path_returns_length_weighted_edges(graph_rows):
    adjacency = GraphCalculator.build_graph(graph_rows)

    _, edges, _, _, _, _ = GraphCalculator.find_shortest_path(adjacency, (0, 0), (0.002, 0), risk_weight=1)

    assert sum(edge.length_m for edge in edges) == 200.0
    assert sum(edge.length_m * edge.risk for edge in edges) / 200 == 50.0
