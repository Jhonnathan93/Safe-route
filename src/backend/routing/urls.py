from django.urls import path
from routing.views import GeocodeAPIView, RouteAPIView

app_name = "routing"

urlpatterns = [
    path("geocode/", GeocodeAPIView.as_view(), name="routing.geocode"),
    path("routes/", RouteAPIView.as_view(), name="routing.routes"),
]
