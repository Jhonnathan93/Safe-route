"""Reusable request-data validation independent from views."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rest_framework import serializers


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    data: dict[str, Any] | None
    errors: dict[str, Any] | None


class _CoordinateSerializer(serializers.Serializer):
    lat = serializers.FloatField(min_value=-90, max_value=90)
    lng = serializers.FloatField(min_value=-180, max_value=180)


class _RouteRequestSerializer(serializers.Serializer):
    origin = _CoordinateSerializer()
    destination = _CoordinateSerializer()
    risk_weight = serializers.FloatField(min_value=0, max_value=10, default=5)


class _GeocodeQuerySerializer(serializers.Serializer):
    q = serializers.CharField(min_length=3, max_length=200, trim_whitespace=True)


class RequestValidator:
    """Validates both public payloads and returns a uniform result shape."""

    @staticmethod
    def validate_route(payload: Any) -> ValidationResult:
        return RequestValidator._validate(_RouteRequestSerializer, payload)

    @staticmethod
    def validate_geocode(query_params: Any) -> ValidationResult:
        return RequestValidator._validate(_GeocodeQuerySerializer, query_params)

    @staticmethod
    def _validate(serializer_class: type[serializers.Serializer], payload: Any) -> ValidationResult:
        serializer = serializer_class(data=payload)
        if serializer.is_valid():
            return ValidationResult(is_valid=True, data=dict(serializer.validated_data), errors=None)
        return ValidationResult(is_valid=False, data=None, errors=dict(serializer.errors))
