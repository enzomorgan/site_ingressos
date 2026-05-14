from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView, View

from events.models import TicketType
from .models import Order, OrderItem


class CreateOrderView(LoginRequiredMixin, View):
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            messages.error(request, 'Administradores não podem comprar ingressos.')
            return redirect('events:event_list')
        
        ticket_type_id = request.POST.get('ticket_type_id')
        quantity = request.POST.get('quantity', 1)

        ticket_type = get_object_or_404(
            TicketType,
            id=ticket_type_id,
            event__active=True
        )

        try:
            quantity = int(quantity)
        except ValueError:
            messages.error(request, 'Quantidade inválida.')
            return redirect('events:event_detail', slug=ticket_type.event.slug)

        if quantity <= 0:
            messages.error(request, 'A quantidade deve ser maior que zero.')
            return redirect('events:event_detail', slug=ticket_type.event.slug)

        if quantity > ticket_type.available():
            messages.error(request, 'Quantidade indisponível para este ingresso.')
            return redirect('events:event_detail', slug=ticket_type.event.slug)

        order = Order.objects.create(
            user=request.user,
            status=Order.STATUS_PENDING,
            total=ticket_type.price * quantity
        )

        order_item = OrderItem(
            order=order,
            ticket_type=ticket_type,
            quantity=quantity,
            price=ticket_type.price
        )

        try:
            order_item.full_clean()
            order_item.save()
        except ValidationError as error:
            order.delete()
            messages.error(request, error.messages[0])
            return redirect('events:event_detail', slug=ticket_type.event.slug)

        messages.success(request, 'Pedido criado com sucesso.')
        return redirect('orders:order_success', pk=order.pk)


class OrderSuccessView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_success.html'
    context_object_name = 'order'
    login_url = '/login/'

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            'items',
            'items__ticket_type',
            'items__ticket_type__event'
        )
        
class MyOrderView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/my_orders.html'
    content_type_name = 'orders'
    login_url = '/login'
    
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            'items',
            'items__ticket_type',
            'items__ticket_type__event'
        ).order_by('-created_at')    