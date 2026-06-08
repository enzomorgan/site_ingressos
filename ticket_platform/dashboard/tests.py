from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from events.models import Event, TicketType
from orders.models import Order, OrderItem
from tickets.models import Ticket

User = get_user_model()


class DashboardViewsTestCase(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='cliente',
            email='cliente@example.com',
            password='senha123456'
        )
        
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
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
        
        self.order = Order.objects.create(
            user=self.customer,
            status=Order.STATUS_PENDING,
            total=100.00
        )
        
        self.order_item = OrderItem.objects.create(
            order=self.order,
            ticket_type=self.ticket_type,
            quantity=1,
            price=self.ticket_type.price
        )
        
    def test_customer_cannot_access_dashboard(self):
        self.client.login(username='cliente', password='senha123456')
        
        response = self.client.get(reverse('dashboard:home'))
        
        self.assertEqual(response.status_code, 403)
        
    def test_admin_can_access_order_list(self):
        self.client.login(username='admin', password='senha123456')
        
        response = self.client.get(reverse('dashboard:order_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pedidos')
        
    @patch('dashboard.views.send_tickets_email')
    def test_admin_can_confirm_payment(self, mock_send_tickets_email):
        self.client.login(username='admin', password='senha123456')

        response = self.client.post(
            reverse('dashboard:confirm_payment', kwargs={'pk': self.order.pk})
        )

        self.order.refresh_from_db()
        self.ticket_type.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.order.status, Order.STATUS_PAID)
        self.assertEqual(self.order.tickets.count(), 1)
        self.assertEqual(self.ticket_type.sold, 1)
        mock_send_tickets_email.assert_called_once_with(self.order)
        
    def test_admin_can_cancel_pending_order(self):
        self.client.login(username='admin', password='senha123456')
        
        response = self.client.post(
            reverse('dashboard:cancel_order', kwargs={'pk': self.order.pk})
        )
        
        self.order.refresh_from_db()
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.order.status, Order.STATUS_CANCELED)
        
    def test_export_orders_csv_requires_admin_and_returns_csv(self):
        self.client.login(username='admin', password='senha123456')
        
        response = self.client.get(reverse('dashboard:export_orders_csv'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment; filename="pedidos.csv"', response['Content-Disposition'])
    
    def test_export_orders_xlsx_requires_admin_and_returns_xlsx(self):
        self.client.login(username='admin', password='senha123456')

        response = self.client.get(reverse('dashboard:export_orders_xlsx'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertIn('attachment; filename="pedidos.xlsx"', response['Content-Disposition'])