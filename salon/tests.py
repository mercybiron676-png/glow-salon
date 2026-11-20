from datetime import date, timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .daraja import DarajaError, normalize_phone
from .models import Booking, Payment, Service


class PhoneTests(TestCase):
    def test_normalize(self):
        self.assertEqual(normalize_phone("0712345678"), "254712345678")
        self.assertEqual(normalize_phone("+254 712 345 678"), "254712345678")
        self.assertEqual(normalize_phone("112345678"), "254112345678")

    def test_invalid(self):
        with self.assertRaises(DarajaError):
            normalize_phone("12345")


@override_settings(DARAJA_DEMO_MODE=True)
class FlowTests(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.service = Service.objects.create(name="Braids", price=1500, duration_minutes=120)

    def test_pages_load(self):
        for name in ("home", "services", "book"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_book_form_redirects_to_pay(self):
        resp = self.client.post(reverse("book"), {
            "customer_name": "Mercy", "phone": "0712345678", "service": self.service.id,
            "date": (date.today() + timedelta(days=1)).isoformat(), "time": "10:00",
        })
        booking = Booking.objects.get()
        self.assertRedirects(resp, reverse("pay", args=[booking.id]))

    def test_api_lists_services(self):
        resp = self.client_api.get("/api/services/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["results"][0]["name"] if "results" in resp.json() else resp.json()[0]["name"], "Braids")

    def test_stk_push_and_demo_confirm(self):
        booking = Booking.objects.create(
            customer_name="Mercy", phone="0712345678", service=self.service,
            date=date.today(), time="10:00",
        )
        resp = self.client_api.post("/api/mpesa/stk-push/", {"booking_id": booking.id}, format="json")
        self.assertEqual(resp.status_code, 201)
        pid = resp.json()["payment_id"]
        self.client_api.post(f"/api/payments/{pid}/demo-confirm/")
        booking.refresh_from_db()
        self.assertEqual(booking.status, "paid")

    def test_callback_success_marks_paid(self):
        booking = Booking.objects.create(
            customer_name="Mercy", phone="0712345678", service=self.service,
            date=date.today(), time="10:00",
        )
        Payment.objects.create(booking=booking, amount=1500, phone="254712345678", checkout_request_id="ws_CO_1")
        body = {"Body": {"stkCallback": {
            "MerchantRequestID": "m1", "CheckoutRequestID": "ws_CO_1", "ResultCode": 0,
            "ResultDesc": "The service request is processed successfully.",
            "CallbackMetadata": {"Item": [{"Name": "MpesaReceiptNumber", "Value": "ABC123XYZ"}]},
        }}}
        resp = self.client_api.post("/api/mpesa/callback/", body, format="json")
        self.assertEqual(resp.status_code, 200)
        booking.refresh_from_db()
        self.assertEqual(booking.status, "paid")
        self.assertEqual(Payment.objects.get().mpesa_receipt, "ABC123XYZ")

    def test_callback_cancelled_marks_failed(self):
        booking = Booking.objects.create(
            customer_name="Mercy", phone="0712345678", service=self.service,
            date=date.today(), time="10:00",
        )
        Payment.objects.create(booking=booking, amount=1500, phone="254712345678", checkout_request_id="ws_CO_2")
        body = {"Body": {"stkCallback": {
            "CheckoutRequestID": "ws_CO_2", "ResultCode": 1032, "ResultDesc": "Request cancelled by user",
        }}}
        self.client_api.post("/api/mpesa/callback/", body, format="json")
        self.assertEqual(Payment.objects.get().status, "failed")
        booking.refresh_from_db()
        self.assertEqual(booking.status, "pending")
