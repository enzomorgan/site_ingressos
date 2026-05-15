from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_list_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView
from events.models import Event
from orders.models import Order
from tickets.models import Ticket
from .forms import EventForm
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
        context['pending_orders'] = Order.objects.filter(status=Order.STATUS_PENDING).count()
        context['paid_orders'] = Order.objects.filter(status=Order.STATUS_PAID).count()
        context['total_tickets'] = Ticket.objects.count()
        context['checked_in_tickets'] = Ticket.objects.filter(checked_in=True).count()
        
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
        
class ConfirmPaymentView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        
        if order.status == Order.STATUS_PAID:
            messages.info(request, 'Este pedido já está pago.')
            return redirect('dashboard:order_list')
        
        try:
            order.mark_as_paid()
            messages.success(request, f'Pagamento do pedido #{order.id} confirmado com sucesso')
        except Exception as error:
            messages.error(request, f'Erro ao confirmar pagamento: {error}')
            
        return redirect('dashboard:order_list')
    
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
        ).order_by('-created_by')
        
class DashboardEventCreateView(StaffRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'dashboard/event_form.html'
    success_url = reverse_lazy('dashboard:event_list')
    
    def form_valid(self, form):
        form.instance.create_by = self.request.user
        messages.success(self, self.request, 'Eventp criado com sucesso.')
        return super().form_valid(form)
    
class DashboardEventUpdateView(StaffRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'dashboard/event_form.html'
    success_url = reverse_lazy('dashboard:event_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Evento atualizado com sucesso.")
        return super().form_valid(form)