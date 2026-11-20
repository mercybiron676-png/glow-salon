"""Small Daraja (Safaricom M-Pesa) client for STK Push (Lipa na M-Pesa Online)."""
import base64
import re
from datetime import datetime

import requests
from django.conf import settings

BASE_URLS = {
    "sandbox": "https://sandbox.safaricom.co.ke",
    "production": "https://api.safaricom.co.ke",
}


class DarajaError(Exception):
    pass


def normalize_phone(phone: str) -> str:
    """Convert 07XXXXXXXX / +2547XXXXXXXX / 7XXXXXXXX to 2547XXXXXXXX."""
    digits = re.sub(r"\D", "", phone or "")
    if digits.startswith("0") and len(digits) == 10:
        digits = "254" + digits[1:]
    elif len(digits) == 9 and digits[0] in "71":
        digits = "254" + digits
    if not re.fullmatch(r"254[71]\d{8}", digits):
        raise DarajaError("Enter a valid Safaricom number e.g. 0712345678")
    return digits


def _base_url():
    return BASE_URLS.get(settings.DARAJA_ENV, BASE_URLS["sandbox"])


def get_access_token() -> str:
    url = f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials"
    try:
        resp = requests.get(
            url,
            auth=(settings.DARAJA_CONSUMER_KEY, settings.DARAJA_CONSUMER_SECRET),
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()["access_token"]
    except (requests.RequestException, KeyError, ValueError) as exc:
        raise DarajaError(f"Could not get Daraja access token: {exc}")


def stk_push(phone: str, amount: int, account_ref: str, description: str) -> dict:
    """Send the payment prompt to the customer's phone. Returns Daraja's JSON."""
    phone = normalize_phone(phone)

    if settings.DARAJA_DEMO_MODE:
        # No keys configured: simulate a successful prompt so the app is demoable.
        return {
            "MerchantRequestID": f"demo-merchant-{datetime.now():%H%M%S}",
            "CheckoutRequestID": f"demo-checkout-{datetime.now():%Y%m%d%H%M%S}",
            "ResponseCode": "0",
            "ResponseDescription": "Demo mode: success. Request accepted for processing",
            "CustomerMessage": "Demo mode: no real prompt sent",
        }

    if not settings.DARAJA_CALLBACK_URL:
        raise DarajaError("DARAJA_CALLBACK_URL is not set")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        f"{settings.DARAJA_SHORTCODE}{settings.DARAJA_PASSKEY}{timestamp}".encode()
    ).decode()

    payload = {
        "BusinessShortCode": settings.DARAJA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone,
        "PartyB": settings.DARAJA_SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": settings.DARAJA_CALLBACK_URL,
        "AccountReference": account_ref[:12],
        "TransactionDesc": description[:13],
    }
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    try:
        resp = requests.post(
            f"{_base_url()}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers=headers,
            timeout=30,
        )
        data = resp.json()
    except (requests.RequestException, ValueError) as exc:
        raise DarajaError(f"STK push failed: {exc}")

    if data.get("ResponseCode") != "0":
        raise DarajaError(data.get("errorMessage") or data.get("ResponseDescription") or "STK push rejected")
    return data
