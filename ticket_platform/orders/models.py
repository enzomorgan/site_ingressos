from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction

from events.models import TicketType


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELED, "Canceled"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )

    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        total = sum(item.quantity * item.price for item in self.items.all())
        return total

    def mark_as_paid(self):
        if self.status == self.STATUS_PAID:
            return
        
        if self.status == self.STATUS_CANCELED:
            raise ValidationError('Não é possível pagar um pedido cancelado.')

        with transaction.atomic():
            self.status = self.STATUS_PAID
            self.total = self.calculate_total()
            self.save(update_fields=["status", "total"])
            self.generate_tickets()

    def generate_tickets(self):
        from tickets.models import Ticket
        
        if self.tickets.exists():
            return

        for item in self.items.select_related("ticket_type"):
            ticket_type = item.ticket_type

            if item.quantity > ticket_type.available():
                raise ValidationError(
                    f"Ingressos insuficientes para {ticket_type.name}."
                )

            for _ in range(item.quantity):
                Ticket.objects.create(order=self)

            ticket_type.sold += item.quantity
            ticket_type.save(update_fields=["sold"])

    def save(self, *args, **kwargs):
        if self.pk:
            old_order = Order.objects.filter(pk=self.pk).first()

            if (
                old_order
                and old_order.status != self.STATUS_PAID
                and self.status == self.STATUS_PAID
            ):
                self.total = self.calculate_total()
                super().save(*args, **kwargs)
                self.generate_tickets()
                return

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Pedido #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(max_digits=8, decimal_places=2)

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("A quantidade deve ser maior que zero.")

        if self.ticket_type and self.quantity > self.ticket_type.available():
            raise ValidationError(
                f"Ingressos insuficientes para {self.ticket_type.name}."
            )

    def save(self, *args, **kwargs):
        if not self.price and self.ticket_type:
            self.price = self.ticket_type.price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_type.name} x {self.quantity}"
