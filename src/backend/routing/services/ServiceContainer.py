"""Centralized initialization for services with process-level state."""
import logging

from django.conf import settings

from routing.services.PedestrianRoutingService import PedestrianRoutingService

routing_service = PedestrianRoutingService(settings.DATASET_PATH)
LOGGER = logging.getLogger(__name__)


def initialize_routing_service() -> None:
    """Eagerly builds the read-only graph once for the current application process."""
    node_count = routing_service.warm_up()
    LOGGER.info("Pedestrian graph initialized with %s nodes.", node_count)
