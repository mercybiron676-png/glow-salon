from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BookingForm
from .models import Booking, Service


def home(request):
    services = Service.objects.filter(is_active=True)[:3]
    return render(request, "salon/home.html", {"services": services})


def services(request):
    return render(request, "salon/services.html", {"services": Service.objects.filter(is_active=True)})


def book(request):
    initial = {}
    if request.GET.get("service"):
        initial["service"] = request.GET["service"]
    form = BookingForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        booking = form.save()
        return redirect("pay", pk=booking.pk)
    return render(request, "salon/book.html", {"form": form})


def pay(request, pk):
    booking = get_object_or_404(Booking.objects.select_related("service"), pk=pk)
    return render(
        request,
        "salon/pay.html",
        {
            "booking": booking,
            "demo_mode": settings.DARAJA_DEMO_MODE,
            "payee_name": settings.PAYEE_NAME,
        },
    )
