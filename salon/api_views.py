from django.db import transaction
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import daraja
from .models import Booking, Payment, Service
from .serializers import (
    BookingSerializer,
    PaymentSerializer,
    STKPushRequestSerializer,
    ServiceSerializer,
)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/services/ and /api/services/<id>/"""
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer


class BookingViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """POST /api/bookings/ to create, GET /api/bookings/<id>/ to check status."""
    queryset = Booking.objects.select_related("service")
    serializer_class = BookingSerializer


@api_view(["POST"])
def stk_push_view(request):
    """POST /api/mpesa/stk-push/  {"booking_id": 1, "phone": "0712345678"}"""
    ser = STKPushRequestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    try:
        booking = Booking.objects.select_related("service").get(pk=ser.validated_data["booking_id"])
    except Booking.DoesNotExist:
        return Response({"detail": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)
    if booking.status == "paid":
        return Response({"detail": "Booking already paid"}, status=status.HTTP_400_BAD_REQUEST)

    phone = ser.validated_data.get("phone") or booking.phone
    try:
        data = daraja.stk_push(
            phone=phone,
            amount=booking.service.price,
            account_ref=f"SALON{booking.id}",
            description="Salon",
        )
    except daraja.DarajaError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    payment = Payment.objects.create(
        booking=booking,
        amount=booking.service.price,
        phone=daraja.normalize_phone(phone),
        merchant_request_id=data.get("MerchantRequestID", ""),
        checkout_request_id=data.get("CheckoutRequestID", ""),
    )
    return Response(
        {
            "message": (
                f"Check your phone and enter your M-Pesa PIN to pay "
                f"KES {booking.service.price} to {daraja.settings.PAYEE_NAME}"
            ),
            "payment_id": payment.id,
            "demo_mode": daraja.settings.DARAJA_DEMO_MODE,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def mpesa_callback(request):
    """Daraja posts the payment result here (must be public HTTPS)."""
    try:
        cb = request.data["Body"]["stkCallback"]
        checkout_id = cb["CheckoutRequestID"]
        code = cb["ResultCode"]
    except (KeyError, TypeError):
        return Response({"ResultCode": 1, "ResultDesc": "Bad payload"}, status=400)

    with transaction.atomic():
        try:
            payment = Payment.objects.select_for_update().get(checkout_request_id=checkout_id)
        except Payment.DoesNotExist:
            return Response({"ResultCode": 0, "ResultDesc": "Accepted"})
        payment.result_desc = str(cb.get("ResultDesc", ""))[:255]
        if code == 0:
            items = {i["Name"]: i.get("Value") for i in cb.get("CallbackMetadata", {}).get("Item", [])}
            payment.mpesa_receipt = str(items.get("MpesaReceiptNumber", ""))
            payment.status = "success"
            payment.booking.status = "paid"
            payment.booking.save(update_fields=["status"])
        else:
            payment.status = "failed"
        payment.save()
    return Response({"ResultCode": 0, "ResultDesc": "Accepted"})


@api_view(["GET"])
def payment_status(request, pk):
    """GET /api/payments/<id>/ - polled by the page after the prompt is sent."""
    try:
        payment = Payment.objects.select_related("booking").get(pk=pk)
    except Payment.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)
    return Response(PaymentSerializer(payment).data)


@api_view(["POST"])
def demo_confirm(request, pk):
    """Demo mode only: simulate the customer entering their PIN."""
    if not daraja.settings.DARAJA_DEMO_MODE:
        return Response({"detail": "Not available"}, status=404)
    try:
        payment = Payment.objects.select_related("booking").get(pk=pk)
    except Payment.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)
    payment.status = "success"
    payment.mpesa_receipt = f"DEMO{payment.id:06d}"
    payment.result_desc = "Demo payment confirmed"
    payment.save()
    payment.booking.status = "paid"
    payment.booking.save(update_fields=["status"])
    return Response(PaymentSerializer(payment).data)
