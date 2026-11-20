from django.core.management.base import BaseCommand

from salon.models import Service

# (name, description, price in KES, duration in minutes)
# Sample prices: change them in /admin > Services (existing rows are never overwritten).
SERVICES = [
    # Hairstyles
    ("Knotless Braids", "Lightweight, neat knotless braids that are gentle on your edges.", 2500, 300),
    ("Box Braids", "Classic box braids in your preferred length and size.", 2000, 240),
    ("Cornrows", "Straight-back or creative cornrow patterns.", 800, 90),
    ("Senegalese Twists", "Smooth, long-lasting rope twists.", 1800, 240),
    ("Fulani Braids", "Stylish Fulani braids with a centre braid and side cornrows.", 2200, 210),
    ("Ghana Weaving", "Neat Ghana weaving for a clean, bold look.", 1500, 150),
    ("Crochet Braids", "Quick crochet install with natural-looking hair.", 1500, 120),
    ("Weave Installation", "Sew-in weave with professional finishing.", 1800, 120),
    ("Silk Press", "Wash, blow-dry and silk press for sleek straight hair.", 1500, 120),
    ("Dreadlocks Retwist", "Retwist and tidy-up for your locs.", 1200, 90),
    ("Haircut & Style", "Wash, cut and blow-dry by our stylists.", 500, 45),
    ("Hair Treatment", "Deep conditioning and scalp therapy.", 1000, 60),
    # Beauty
    ("Manicure", "Nail shaping, cuticle care and polish.", 600, 40),
    ("Pedicure", "Relaxing foot soak, scrub and polish.", 800, 50),
    ("Facial Treatment", "Deep cleansing facial for glowing skin.", 1200, 60),
]


class Command(BaseCommand):
    help = "Add sample salon services (safe to run more than once)."

    def handle(self, *args, **options):
        created = 0
        for name, desc, price, mins in SERVICES:
            _, was_created = Service.objects.get_or_create(
                name=name,
                defaults={"description": desc, "price": price, "duration_minutes": mins},
            )
            created += was_created
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} new services."))
