"""Stateless client for the geocoding provider."""
from __future__ import annotations

import requests

from routing.exceptions import GeocodingUnavailableError

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"


class GeocodingManager:
    """Namespace for translating places into coordinates."""

    @staticmethod
    def locate(query: str, user_agent: str, timeout_seconds: float) -> dict[str, float | str] | None:
        try:
            response = requests.get(
                NOMINATIM_SEARCH_URL,
                params={"q": f"{query}, Medellín, Colombia", "format": "jsonv2", "limit": 1},
                headers={"User-Agent": user_agent},
                timeout=timeout_seconds,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise GeocodingUnavailableError("The geocoding service is unavailable.") from error
        results = response.json()
        if not results:
            return None
        result = results[0]
        return {"label": result["display_name"], "lat": float(result["lat"]), "lng": float(result["lon"])}
