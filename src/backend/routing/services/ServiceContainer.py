"""Centralized initialization for services with process-level state."""
from django.conf import settings

from routing.services.PedestrianRoutingService import PedestrianRoutingService

routing_service = PedestrianRoutingService(settings.DATASET_PATH)
