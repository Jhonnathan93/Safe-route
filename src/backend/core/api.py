"""Shared HTTP contract and error handling for applications."""
from __future__ import annotations

import logging
from typing import Any

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

LOGGER = logging.getLogger(__name__)


class BaseAPIView(APIView):
    """Base class that preserves the JSON envelope and hides internal errors."""

    def send_response(
        self,
        data: Any = None,
        message: str = "Operation completed successfully.",
        status_code: int = status.HTTP_200_OK,
    ) -> Response:
        return Response(
            {"success": True, "message": message, "data": data},
            status=status_code,
        )

    def send_error_response(
        self,
        message: str,
        data: Any = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> Response:
        return Response(
            {"success": False, "message": message, "data": data},
            status=status_code,
        )

    def handle_exception(self, exc: Exception) -> Response:
        response = super().handle_exception(exc)
        if response is not None:
            detail = response.data.get("detail", "The request could not be processed.")
            return self.send_error_response(str(detail), status_code=response.status_code)

        LOGGER.exception("Unexpected error while processing an API request.", exc_info=exc)
        return self.send_error_response(
            "An internal error occurred. Please try again later.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
