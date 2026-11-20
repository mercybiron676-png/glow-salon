from rest_framework import serializers

from .models import Booking, Payment, Service


class ServiceSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source="image_src", read_only=True)

    class Meta:
        model = Service
        fields = ["id", "name", "description", "price", "duration_minutes", "image_url"]


class BookingSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    amount = serializers.IntegerField(source="service.price", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "customer_name", "phone", "service", "service_name", "amount",
            "date", "time", "notes", "status", "created_at",
        ]
        read_only_fields = ["status", "created_at"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id", "booking", "amount", "phone", "checkout_request_id",
            "mpesa_receipt", "result_desc", "status", "created_at",
        ]
        read_only_fields = fields


class STKPushRequestSerializer(serializers.Serializer):
    booking_id = serializers.IntegerField()
    phone = serializers.CharField(max_length=15, required=False)
