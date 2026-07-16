"""Public endpoints for place lookup and route calculation."""
from __future__ import annotations

from typing import Any

from django.conf import settings
from rest_framework import status

from core.api import BaseAPIView
from routing.exceptions import (
    DatasetUnavailableError,
    GeocodingUnavailableError,
    RouteNotFoundError,
)
from routing.services.ServiceContainer import routing_service
from routing.utils.GeocodingManager import GeocodingManager
from routing.utils.RequestValidator import RequestValidator


class GeocodeAPIView(BaseAPIView):
    """Converts a place query into a point and its nearest pedestrian node."""

    def get(self, request):
        validation_result = RequestValidator.validate_geocode(request.query_params)
        if not validation_result.is_valid:
            return self.send_error_response(
                "The location query is invalid.",
                data=validation_result.errors,
            )
        try:
            result = GeocodingManager.locate(
                validation_result.data["q"],
                settings.GEOCODER_USER_AGENT,
                settings.GEOCODER_TIMEOUT_SECONDS,
            )
            if result is None:
                return self.send_response(
                    data={
                        "found": False,
                        "label": "Location not found. Select a point on the map.",
                        "location": None,
                        "nearest_node": None,
                    },
                    message="Location was not found.",
                )
            location = self._resolve_location(result)
            node, distance_m = routing_service.get_closest_node(location)
        except GeocodingUnavailableError:
            return self.send_error_response(
                "Location search is currently unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except DatasetUnavailableError:
            return self.send_error_response(
                "The pedestrian network is currently unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return self.send_response(
            data={
                "found": True,
                "label": result["label"],
                "location": {"lat": location[1], "lng": location[0]},
                "nearest_node": {"lat": node[1], "lng": node[0], "distance_m": round(distance_m, 1)},
            },
            message="Location processed successfully.",
        )

    @staticmethod
    def _resolve_location(result: dict[str, float | str] | None) -> tuple[float, float]:
        if result is None:
            raise ValueError("A geocoded result is required.")
        return float(result["lng"]), float(result["lat"])


class RouteAPIView(BaseAPIView):
    """Calculates a route using a cost that combines distance and risk."""

    def post(self, request):
        validation_result = RequestValidator.validate_route(request.data)
        if not validation_result.is_valid:
            return self.send_error_response(
                "The route data is invalid.",
                data=validation_result.errors,
            )
        try:
            route = self._calculate_route(validation_result.data)
        except RouteNotFoundError:
            return self.send_error_response(
                "No connected route exists between the selected points.",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        except DatasetUnavailableError:
            return self.send_error_response(
                "The pedestrian network is currently unavailable.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return self.send_response(data=route, message="Route calculated successfully.")

    @staticmethod
    def _calculate_route(payload: dict[str, Any]) -> dict[str, Any]:
        origin = payload["origin"]
        destination = payload["destination"]
        return routing_service.get_route(
            origin=(origin["lng"], origin["lat"]),
            destination=(destination["lng"], destination["lat"]),
            risk_weight=payload["risk_weight"],
        )
