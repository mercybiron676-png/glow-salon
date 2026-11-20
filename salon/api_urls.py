from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register("services", api_views.ServiceViewSet, basename="service")
router.register("bookings", api_views.BookingViewSet, basename="booking")

urlpatterns = [
    path("", include(router.urls)),
    path("mpesa/stk-push/", api_views.stk_push_view, name="stk-push"),
    path("mpesa/callback/", api_views.mpesa_callback, name="mpesa-callback"),
    path("payments/<int:pk>/", api_views.payment_status, name="payment-status"),
    path("payments/<int:pk>/demo-confirm/", api_views.demo_confirm, name="demo-confirm"),
]
