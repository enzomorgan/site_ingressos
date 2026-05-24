from typing import Any

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView

from events.models import Event, TicketType
from orders.models import Order
from tickets.models import Ticket
from tickets.services import send_ticket_email
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
        context['active_events'] = Event.objects.filter(is_active=True).count()
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
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Order.objects.select_related(
            'user'
        ).prefetch_related(
            'items',
            'items__ticket_type',
            'items__ticket_type__event'
            'tickets',
        ).order_by('-created_at')
        
        status = self.request.GET.get('status')
        search = self.request.GET.get('q')
        
        if status in [
            Order.STATUS_PENDING,
            Order.STATUS_PAID,
            Order.STATUS_CANCELLED
        ]:
            queryset = queryset.filter(status=status)
        
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(items__ticket_type__name__icontains=search) |
                Q(items__ticket_type__event__name__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        context['total_orders_count'] = Order.objects.count()
        context['pending_orders_count'] = Order.objects.filter(
            status=Order.STATUS_PENDING
        ).count()
        context['paid_orders_count'] = Order.objects.filter(
            status=Order.STATUS_PAID
        ).count()
        context['cancelled_orders_count'] = Order.objects.filter(
            status=Order.STATUS_CANCELLED
        ).count()
        
        return context
    
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
            'tickets'
        )
        
class ConfirmPaymentView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        
        if order.status == Order.STATUS_PAID:
            messages.error(
                request,
                'Não é possível cancelar um pedido que já foi pago.'
            )
            return redirect('dashboard:order_detail', pk=order.pk)
        
        order.status = Order.STATUS_CANCELED
        order.save(update_fields=['status'])
        
        messages.success(
            request,
            f'Pedido #{order.pk} cancelado com sucesso.'
        )
        return redirect('dashboard:order_detail', pk=order.pk)
    
class DashboardLogoutView(StaffRequiredMixin, View):
    def post(self, request):
        logout(request)
        return redirect(reverse_lazy('dashboard:home'))
    
class DashboardEventListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = 'dashboard/event_list.html'
    context_object_name =  'events'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Event.objects.all().order_by(
            '-created_by'
        ).prefetch_related(
            'tickets'
        ).order_by('-created_at')
        
        search = self.request.GET.get('q')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(location__icontains=search)
            )
            
        if status == 'active':
            queryset = queryset.filter(is_active=True)
            
        if status == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_status'] = self.request.GET.get('status', '')
        
        context['total_events_count'] = Event.objects.count()
        context['active_events_count'] = Event.objects.filter(active=True).count()
        context['inactive_events_count'] = Event.objects.filter(active=False).count()
        
        return context