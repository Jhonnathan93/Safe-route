from unittest.mock import patch

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


def test_geocode_returns_envelope_for_invalid_query(api_client):
    response = api_client.get("/api/routing/geocode/", {"q": "x"})

    assert response.status_code == 400
    assert response.data["success"] is False
    assert response.data["data"]["q"]


@patch("routing.views.RoutingAPIViews.routing_service.get_route")
def test_route_returns_envelope_for_valid_payload(get_route, api_client):
    get_route.return_value = {"coordinates": [], "distance_m": 0, "risk_score": 0}

    response = api_client.post(
        "/api/routing/routes/",
        {"origin": {"lat": 6.2, "lng": -75.5}, "destination": {"lat": 6.3, "lng": -75.6}},
        format="json",
    )

    assert response.status_code == 200
    assert response.data == {
        "success": True,
        "message": "Route calculated successfully.",
        "data": {"coordinates": [], "distance_m": 0, "risk_score": 0},
    }
