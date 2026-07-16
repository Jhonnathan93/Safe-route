from django.apps import AppConfig
from django.conf import settings


class RoutingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "routing"

    def ready(self) -> None:
        """Optionally warm the graph for long-lived application processes."""
        if not settings.EAGER_GRAPH_WARM_UP:
            return

        from routing.services.ServiceContainer import initialize_routing_service

        initialize_routing_service()
