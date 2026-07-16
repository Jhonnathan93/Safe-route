from django.apps import AppConfig


class RoutingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "routing"

    def ready(self) -> None:
        from routing.services.ServiceContainer import initialize_routing_service

        initialize_routing_service()
