from django.contrib import admin

from .models import Booking, Payment, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "duration_minutes", "image", "is_active")
    list_editable = ("price", "image", "is_active")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer_name", "phone", "service", "date", "time", "status")
    list_filter = ("status", "date", "service")
    search_fields = ("customer_name", "phone")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "amount", "phone", "mpesa_receipt", "status", "created_at")
    list_filter = ("status",)
