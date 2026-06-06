from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, TicketType
from orders.models import Order, OrderItem
from tickets.models import Ticket

User = get_user_model()

class OrderFlowTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='cliente',
            email='cliente@email.com',
            password='senha123456'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@email.com',
            password='senha123456',
            is_staff=True
        )
        
        self.event = Event.objects.create(
            title='Evento Teste',
            description='Descrição do evento teste',
            date=timezone.now() + timezone.timedelta(days=10),
            location='Local Teste',
            created_by=self.admin,
            active=True
        )
        
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name='Ingresso Inteira',
            price=50,
            quantity=10,
            sold=0
        )
        
    def test_customer_can_create_pending_order(self):
        self.client.login(username='cliente', password='senha123456')
        
        response = self.client.post(reverse('orders:create_order'), {
            'ticket_type_id': self.ticket_type.id,
            'quantity': 2,
        })
        
        self.assertEqual(response.status_code, 302)
        
        order = Order.objects.get(user=self.customer)
        
        self.assertEqual(order.status, Order.STATUS_PENDING)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)
        self.assertEqual(Ticket.objects.count(), 0)
        
    def test_mark_as_paid_generates_tickets(self):
        order = Order.objects.create(
            user=self.customer,
            status=Order.STATUS_PENDING,
            total=100
        )
        
        OrderItem.objects.create(
            order=order,
            ticket_type=self.ticket_type,
            quantity=2,
            price=self.ticket_type.price
        )
        
        order.mark_as_paid()
        
        order.refresh_from_db()
        self.ticket_type.refresh_from_db()
        
        self.assertEqual(order.status, Order.STATUS_PAID)
        self.assertEqual(order.tickets.count(), 2)
        self.assertEqual(self.ticket_type.sold, 2)
        
    def test_paid_order_does_not_generate_duplicate_tickets(self):
        order = Order.objects.create(
            user=self.customer,
            status=Order.STATUS_PENDING,
            total=100
        )
        
        OrderItem.objects.create(
            order=order,
            ticket_type=self.ticket_type,
            quantity=2,
            price=self.ticket_type.price
        )
        
        order.mark_as_paid()
        order.mark_as_paid()
        
        order.refresh_from_db()
        self.ticket_type.refresh_from_db()
        
        self.assertEqual(order.tickets.count(), 2)
        self.assertEqual(order.tickets.count(), 2)
        
    def test_canceled_order_cannot_be_paid(self):
        order = Order.objects.create(
            user=self.customer,
            status=Order.STATUS_CANCELED,
            total=100
        )
        
        OrderItem.objects.create(
            order=order,
            ticket_type=self.ticket_type,
            quantity=1,
            price=self.ticket_type.price
        )
        
        with self.assertRaises(ValidationError):
            order.mark_as_paid()
            
        order.refresh_from_db()
        
        self.assertEqual(order.status, Order.STATUS_CANCELED)
        self.assertEqual(order.tickets.count(), 0)