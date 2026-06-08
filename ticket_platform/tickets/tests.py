from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from events.models import Event, TicketType
from orders.models import Order, OrderItem
from tickets.models import Ticket

User = get_user_model()

class CustomerSecurityTestCase(TestCase):
    def setUp(self):
        self.customer_a = User.objects.create_user(
            username='cliente_a',
            email='cliente_a@email.com',
            password='senha123456'
        )
        
        self.customer_b = User.objects.create_user(
            username='cliente_b',
            email='cliente_b@email.com',
            password='senha123456'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@email.com',
            password='senha123456',
            is_staff=True
        )
        
        self.event = Event.objects.create(
            title='Evento de Teste',
            description='Descrição do evento de teste',
            date=timezone.now() + timezone.timedelta(days=10),
            location='Local de Teste',
            created_by=self.admin,
            active=True
        )
        
        self.ticket_type = TicketType.objects.create(
            event=self.event,
            name='Ingresso Inteira',
            price=100.00,
            quantity=50,
            sold=0
        )
        
        self.order_a = Order.objects.create(
            user=self.customer_a,
            status=Order.STATUS_PAID,
            total=100.00
        )
        
        OrderItem.objects.create(
            order=self.order_a,
            ticket_type=self.ticket_type,
            quantity=1,
            price=self.ticket_type.price
        )
        
        self.ticket_a = Ticket.objects.create(
            order=self.order_a
        )
        
        self.order_b = Order.objects.create(
            user=self.customer_b,
            status=Order.STATUS_PAID,
            total=100.00
        )
        
        OrderItem.objects.create(
            order=self.order_b,
            ticket_type=self.ticket_type,
            quantity=1,
            price=self.ticket_type.price
        )
        
        self.ticket_b = Ticket.objects.create(
            order=self.order_b
        )
        
    def test_customer_only_sees_own_orders(self):
        self.client.login(username='cliente_a', password='senha123456')
        
        response = self.client.get(reverse('orders:my_orders'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'Pedido #{self.order_a.id}')
        self.assertNotContains(response, f'Pedido #{self.order_b.id}')
        
    def test_customer_cannot_access_other_customer_order_detail(self):
        self.client.login(username='cliente_a', password='senha123456')
        
        response = self.client.get(
            reverse('orders:my_order_detail', kwargs={'pk': self.order_b.pk})
        )
        
        self.assertEqual(response.status_code, 404)
        
    def test_customer_only_sees_own_tickets(self):
        self.client.login(username='cliente_a', password='senha123456')
        
        response = self.client.get(reverse('tickets:my_tickets'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(self.ticket_a.code))
        self.assertNotContains(response, str(self.ticket_b.code))
        
    def test_customer_cannot_access_other_customer_ticket_detail(self):
        self.client.login(username='cliente_a', password='senha123456')
        
        response = self.client.get(
            reverse('tickets:ticket_detail', kwargs={'pk': self.ticket_b.pk})
        )
        
        self.assertEqual(response.status_code, 404)