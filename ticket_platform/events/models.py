from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Event(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField()

    date = models.DateTimeField()

    location = models.CharField(max_length=255)

    banner = models.ImageField(upload_to='events/banners/', blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
class TicketType(models.Model):

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    name = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=8, decimal_places=2)

    quantity = models.PositiveIntegerField()

    sold = models.PositiveIntegerField(default=0)

    def available(self):
        return self.quantity - self.sold

    def __str__(self):
        return f"{self.event.title} - {self.name}"