from datetime import date

from django import forms

from .models import Booking, Service


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["customer_name", "phone", "service", "date", "time", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "phone": forms.TextInput(attrs={"placeholder": "0712345678"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)
        self.fields["date"].widget.attrs["min"] = date.today().isoformat()

    def clean_date(self):
        d = self.cleaned_data["date"]
        if d < date.today():
            raise forms.ValidationError("Pick today or a future date.")
        return d
