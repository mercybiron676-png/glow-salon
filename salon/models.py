from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField(help_text="Price in KES")
    duration_minutes = models.PositiveIntegerField(default=60)
    image = models.CharField(
        max_length=300,
        blank=True,
        help_text="Either a full image link (https://...) or a file name inside "
        "salon/static/salon/images/, e.g. braids.jpg",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (KES {self.price})"

    @property
    def image_src(self):
        """URL to show in templates, or '' if no image is set."""
        if not self.image:
            return ""
        if self.image.startswith(("http://", "https://")):
            return self.image
        from django.templatetags.static import static
        return static(f"salon/images/{self.image}")


class Booking(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending payment"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ]

    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, help_text="Format 2547XXXXXXXX")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="bookings")
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer_name} - {self.service.name} on {self.date}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ("initiated", "Initiated"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    amount = models.PositiveIntegerField()
    phone = models.CharField(max_length=15)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, db_index=True)
    mpesa_receipt = models.CharField(max_length=30, blank=True)
    result_desc = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="initiated")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment {self.id} for booking {self.booking_id}: {self.status}"
