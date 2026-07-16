"""Domain errors translated into safe HTTP responses by views."""


class DatasetUnavailableError(Exception):
    """The data source is unavailable or has an unusable structure."""


class RouteNotFoundError(Exception):
    """The requested nodes are not connected in the pedestrian network."""


class GeocodingUnavailableError(Exception):
    """The external geocoding provider did not respond correctly."""
