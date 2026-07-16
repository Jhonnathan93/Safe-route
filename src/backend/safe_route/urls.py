from django.urls import include, path

urlpatterns = [path("api/routing/", include("routing.urls"))]
