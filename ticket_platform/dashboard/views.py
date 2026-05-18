from typing import Any
from tickets.services import send_tickets_email
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from events.models import Event, TicketType
from orders.models import Order
from tickets.models import Ticket
from .forms import EventForm, TicketTypeForm


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/login/'

    def test_func(self):
        return self.request.user.is_staff


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_events'] = Event.objects.count()
        context['active_events'] = Event.objects.filter(active=True).count()
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(
            status=Order.STATUS_PENDING
        ).count()
        context['paid_orders'] = Order.objects.filter(
            status=Order.STATUS_PAID
        ).count()
        context['total_tickets'] = Ticket.objects.count()
        context['checked_in_tickets'] = Ticket.objects.filter(
            checked_in=True
        ).count()

        return context


class DashboardOrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = 'dashboard/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.select_related(
            'user'
        ).prefetch_related(
            'items',
            'items__ticket_type',
            'items__ticket_type__event',
            'tickets',
        ).order_by('-created_at')
        
class DashboardOrderDetailView(StaffRequiredMixin, DetailView):
    model = Order
    template_name = 'dashboard/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.select_related(
            'user'
        ).prefetch_related(
            'items',
            'items__ticket_type',
            'items__ticket_type__event',
            'tickets',
        )
class ConfirmPaymentView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.status == Order.STATUS_PAID:
            messages.info(request, 'Este pedido já está pago.')
            return redirect('dashboard:order_list')

        try:
            order.mark_as_paid()
            send_tickets_email(order)
            messages.success(
                request,
                f'Pagamento do pedido #{order.id} confirmado com sucesso. O e-mail com os ingressos foi enviado ao cliente.'
            )
        except Exception as error:
            messages.error(request, f'Erro ao confirmar pagamento: {error}')

        return redirect('dashboard:order_list')

class CancelOrderView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        
        if order.status == Order.STATUS_PAID:
            messages.error(
                request,
                'Não é possível cancelar um pedido que já foi pago.'
            )
            return redirect('dashboard:order_detail', pk=order.pk)
        
        if order.status == Order.STATUS_CANCELED:
            messages.info(request, 'Este pedido já está cancelado.')
            return redirect('dashboard:order_detail', pk=order.pk)
        
        order.status = Order.STATUS_CANCELED
        order.save(update_fields=['status'])
        
        messages.success(
            request,
            f'Pedido #{order.id} cancelado com sucesso.'
        )
        return redirect('dashboard:order_detail', pk=order.pk)
class DashboardLogoutView(LoginRequiredMixin, View):
    def post(self, request):
        logout(request)
        return redirect('events:event_list')


class DashboardEventListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = 'dashboard/event_list.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.select_related(
            'created_by'
        ).prefetch_related(
            'tickets'
        ).order_by('-created_at')


class DashboardEventCreateView(StaffRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'dashboard/event_form.html'
    success_url = reverse_lazy('dashboard:event_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Evento criado com sucesso.')
        return super().form_valid(form)


class DashboardEventUpdateView(StaffRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'dashboard/event_form.html'
    success_url = reverse_lazy('dashboard:event_list')

    def form_valid(self, form):
        messages.success(self.request, 'Evento atualizado com sucesso.')
        return super().form_valid(form)
    
class DashboardTicketTypeListView(StaffRequiredMixin, ListView):
    model = TicketType
    template_name = 'dashboard/ticket_list.html'
    context_object_name = 'ticket_types'
    
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs['event_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return TicketType.objects.filter(
            event=self.event
        ).order_by('price', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context
    
class DashboardTicketTypeCreateView(StaffRequiredMixin, CreateView):
    model = TicketType
    form_class = TicketTypeForm
    template_name = 'dashboard/ticket_type_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.event = get_object_or_404(Event, pk=kwargs['event_pk'])
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.event = self.event
        messages.success(self.request, 'Tipo de ingresso criado com sucesso.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard:ticket_type_list',
            kwargs={'event_pk': self.event.pk}
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.event
        return context
    
class DashboardTicketTypeUpdateView(StaffRequiredMixin, UpdateView):
    model = TicketType
    form_class = TicketTypeForm
    template_name = 'dashboard/ticket_type_form.html'
    context_object_name = 'ticket_type'
    
    def form_valid(self, form):
        messages.success(self.request, 'Tipo de ingresso atualizado.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy(
            'dashboard:ticket_type_list',
            kwargs={'event_pk': self.object.event.pk}
        )
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['event'] = self.object.event
        return context
    
class CheckinSearchView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/checkin_search.html'
    
class CheckinValidateView(StaffRequiredMixin, TemplateView):
    template_name = 'dashboard/checkin_result.html'
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        code = self.kwargs.get('code')    
        
        try:
            ticket = Ticket.objects.select_related(
                'order',
                'order__user'
            ).prefetch_related(
                'order__items',
                'order__items__ticket_type',
                'order__items__ticket_type__event'
            ).get(code=code)
        except Ticket.DoesNotExist:
            context['status'] = 'invalid'
            context['message'] = 'Ingresso inválido ou não encontrado.'
            context['ticket'] = None
            return context
        
        context['ticket'] = ticket
        context['item'] = ticket.order.items.first()
        
        if ticket.checked_in:
            context['status'] = 'used'
            context['message'] = 'Este ingresso já foi utilizado.'
            return context  
        
        ticket.checked_in = True
        ticket.save(update_fields=['checked_in'])
        
        context['status'] = 'success'
        context['message'] = 'Check-in realizado com sucesso. Entrada liberada'
        
        return context