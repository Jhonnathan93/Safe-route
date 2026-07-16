"""Centralized initialization for services with process-level state."""
import logging

from django.conf import settings

from routing.services.PedestrianRoutingService import PedestrianRoutingService

routing_service = PedestrianRoutingService(settings.DATASET_PATH)
LOGGER = logging.getLogger(__name__)


def initialize_routing_service() -> bool:
    """Try to pre-load the graph without preventing a serverless startup.

    A serverless function can be started before its dataset is available or can
    be interrupted while it is warming up. The service keeps the graph empty in
    that case; its thread-safe lazy loader will retry the initialization on the
    first route or nearest-node request.
    """
    try:
        node_count = routing_service.warm_up()
    except Exception:
        LOGGER.exception(
            "Pedestrian graph pre-load failed; it will be retried on the first request."
        )
        return False

    LOGGER.info("Pedestrian graph initialized with %s nodes.", node_count)
    return True
