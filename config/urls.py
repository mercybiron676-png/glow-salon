from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("salon.api_urls")),
    path("", include("salon.urls")),
]
