from django.http import JsonResponse
from django.urls import include, path


def health(request):
    return JsonResponse({"service": "property_service", "status": "ok"})


urlpatterns = [
    path("health", health),
    path("", include("properties.urls")),
]
