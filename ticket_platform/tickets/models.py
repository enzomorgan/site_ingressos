import uuid

from django.core.files import File
from django.db import models

from orders.models import Order
from .utils import generate_qr_code, generate_ticket_pdf


class Ticket(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    qr_code = models.ImageField(upload_to="tickets/qrcodes/", blank=True, null=True)

    pdf_file = models.FileField(upload_to="tickets/pdfs/", blank=True, null=True)

    checked_in = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr_data = f'/painel/checkin/{self.code}/'
            qr_buffer = generate_qr_code(qr_data)
            self.qr_code.save(f"{self.code}.png", File(qr_buffer), save=False)

        super().save(*args, **kwargs)

        if not self.pdf_file:
            pdf_path = generate_ticket_pdf(self)

            with open(pdf_path, "rb") as pdf:
                self.pdf_file.save(f"{self.code}.pdf", File(pdf), save=False)

            super().save(update_fields=["pdf_file"])

    def __str__(self):
        return str(self.code)
