import csv
import xlsxwriter
from django.http import HttpResponse
from io import BytesIO
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
from tickets.services import send_tickets_email
from .forms import EventForm, TicketTypeForm

def get_filtered_orders(request):
    queryset = Order.objects.select_related(
        'user'
    ).prefetch_related(
        'items',
        'items__ticket_type',
        'items__ticket_type__event',
        'tickets',
    ).order_by('-created_at')
    
    status = request.GET.get('status')
    search = request.GET.get('q')
    
    if status in [
        Order.STATUS_PENDING,
        Order.STATUS_PAID,
        Order.STATUS_CANCELED
    ]:
        queryset = queryset.filter(status=status)
    
    if search:
        queryset = queryset.filter(
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(id__icontains=search) |
            Q(items__ticket_type__name__icontains=search) |
            Q(items__ticket_type__event__title__icontains=search)
        ).distinct()
    
    return queryset

def get_filtered_events(request):
    queryset = Event.objects.select_related(
        'created_by'
    ).prefetch_related(
        'tickets'
    ).order_by('-created_at')
    
    search = request.GET.get('q')
    status = request.GET.get('status')
    
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) |
            Q(location__icontains=search)
        )
        
    if status == 'active':
        queryset = queryset.filter(active=True)
        
    if status == 'inactive':
        queryset = queryset.filter(active=False)
        
    return queryset

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
    paginate_by = 10
    
    def get_queryset(self):
        return get_filtered_orders(self.request)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        context['total_orders_count'] = Order.objects.count()
        context['pending_orders_count'] = Order.objects.filter(
            status=Order.STATUS_PENDING
        ).count()
        context['paid_orders_count'] = Order.objects.filter(
            status=Order.STATUS_PAID
        ).count()
        context['canceled_orders_count'] = Order.objects.filter(
            status=Order.STATUS_CANCELED
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
            'tickets',
        )
        
class ConfirmPaymentView(StaffRequiredMixin, View):
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        
        if order.status == Order.STATUS_PAID:
            messages.info(request, 'Este pedido já está pago.')
            return redirect('dashboard:order_detail', pk=order.pk)
        
        if order.status == Order.STATUS_CANCELED:
            messages.error(
                request,
                'Não é possível confirmar o pagamento de um pedido cancelado.'
            )
            return redirect('dashboard:order_detail', pk=order.pk)
        
        try:
            order.mark_as_paid()
            send_tickets_email(order)
            
            messages.success(
                request,
                f'Pagamento do pedido #{order.id} confirmado com sucesso. o e-mail com os ingressos foram enviados para {order.user.email}.'
            )
        except Exception as error:
            messages.error(request, f'Erro ao confirmar pagamento: {error}')
            
        return redirect('dashboard:order_detail', pk=order.pk)
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
                messages.info(request, 'O pedido já está cancelado.')
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
        return redirect('events:event_list')
    
class DashboardEventListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = 'dashboard/event_list.html'
    context_object_name = 'events'
    paginate_by = 10
    
    def get_queryset(self):
        return get_filtered_events(self.request)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_status'] = self.request.GET.get('status', '')
        
        context['total_events_count'] = Event.objects.count()
        context['active_events_count'] = Event.objects.filter(active=True).count()
        context['inactive_events_count'] = Event.objects.filter(active=False).count()
        
        return context
    
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
    template_name = 'dashboard/ticket_form.html'
    
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
    template_name = 'dashboard/ticket_form.html'
    context_object_name = 'ticket_type'
    
    def form_valid(self, form):
        messages.success(self.request, 'Tipo de ingresso atualizado com sucesso.')
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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        code = self.kwargs.GET.get('code')
        
        try: 
            ticket = Ticket.objects.select_related(
                'order',
                'order__user',
            ).prefetch_related(
                'ticket_type',
                'ticket_type__event',
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
            context['message'] = 'Este ingresso já foi utilizado para check-in.'
            return context
        
        ticket.checked_in = True
        ticket.save(update_fields=['checked_in'])
        
        context['status'] = 'success'
        context['message'] = 'Check-in realizado com sucesso. Entrada liberada.'
        
        return context
    
class ExportOrdersCSVView(StaffRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="pedidos.csv"'
        
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        writer.writerow([
            'ID',
            'Cliente',
            'Email',
            'Status',
            'Total',
            'Ingressos',
            'Data',
        ])
        
        orders = get_filtered_orders(request)
        
        for order in orders:
            writer.writerow([
                order.id,
                order.user.get_full_name() or order.user.username,
                order.user.email,
                order.get_status_display(),
                order.total,
                order.tickets.count(),
                order.created_at.strftime('%d/%m/%Y %H:%M'),
            ])
            
        return response
    
class ExportOrdersXLSXView(StaffRequiredMixin, View):
    def get(self, request):
        output = BytesIO()
        
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Pedidos')
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0f172a',
            'font_color': '#ffffff',
            'border': 1,
            'align': 'center',
        })
        
        money_format = workbook.add_format({
            'num_format': 'R$ #,##0.00',
            'border': 1,
        })
        
        date_format = workbook.add_format({
            'num_format': 'dd/mm/yyyy hh:mm',
            'border': 1,
        })
        
        cell_format = workbook.add_format({
            'border': 1,
        })
        
        headers = [
            'ID',
            'Cliente',
            'Email',
            'Status',
            'Total',
            'Ingressos',
            'Data',
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            
        orders = get_filtered_orders(request)
        
        for row, order in enumerate(orders, start=1):
            worksheet.write(row, 0, order.id, cell_format)
            worksheet.write(row, 1, order.user.get_full_name() or order.user.username, cell_format)
            worksheet.write(row, 2, order.user.email, cell_format)
            worksheet.write(row, 3, order.get_status_display(), cell_format)
            worksheet.write_number(row, 4, float(order.total), money_format)
            worksheet.write_number(row, 5, order.tickets.count(), cell_format)
            worksheet.write_datetime(row, 6, order.created_at.replace(tzinfo=None), date_format)
            
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 28)
        worksheet.set_column('C:C', 34)
        worksheet.set_column('D:D', 16)
        worksheet.set_column('E:E', 16)
        worksheet.set_column('F:F', 14)
        worksheet.set_column('G:G', 22)
        
        worksheet.autofilter(0, 0, len(headers), len(headers) - 1)
        worksheet.freeze_panes(1, 0)
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="pedidos.xlsx"'
        
        return response
    
class ExportEventsCSVView(StaffRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="eventos.csv"'
        
        response.write('\ufeff')
        
        writer = csv.writer(response)
        
        writer.writerow([
            'Evento',
            'Data',
            'Local',
            'Status',
            'Tipo de ingresso',
            'Preço',
            'Quantidade',
            'Vendidos',
            'Disponíveis',
        ])
        
        events = get_filtered_events(request)
        
        for event in events:
            ticket_types = event.tickets.all()
            
            if ticket_types:
                for ticket_type in ticket_types:
                    writer.writerow([
                        event.title,
                        event.date.strftime('%d%m/%Y %H:%M'),
                        event.location,
                        'Ativo' if event.active else 'Inativo',
                        ticket_type.name,
                        ticket_type.price,
                        ticket_type.quantity,
                        ticket_type.sold,
                        ticket_type.available(),
                    ])
            else:
                writer.writerow([
                    event.title,
                    event.date.strftime('%d/%m/%Y %H:%M'),
                    event.location,
                    'Ativo' if event.active else 'Inativo',
                    'N/A',
                    'N/A',
                    'N/A',
                    'N/A',
                    'N/A',
                ])
        return response
    
class ExportEventsXLSXView(StaffRequiredMixin, View):
    def get(self, request):
        output = BytesIO()
        
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Eventos')
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#0f172a',
            'font_color': '#ffffff',
            'border': 1,
            'align': 'center',
        })
        
        money_format = workbook.add_format({
            'num_format': 'R$ #,##0.00',
            'border': 1,
        })
        
        date_format = workbook.add_format({
            'num_format': 'dd/mm/yyyy hh:mm',
            'border': 1,
        })
        
        cell_format = workbook.add_format({
            'border': 1,
        })
        
        headers = [
            'Evento',
            'Data',
            'Local',
            'Status',
            'Tipo de ingresso',
            'Preço',
            'Quantidade',
            'Vendidos',
            'Disponíveis',
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            
        events = get_filtered_events(request)
        
        row = 1
        for event in events:
            ticket_types = event.tickets.all()
            
            if ticket_types:
                for ticket_type in ticket_types:
                    worksheet.write(row, 0, event.title, cell_format)
                    worksheet.write_datetime(row, 1, event.date.replace(tzinfo=None), date_format)
                    worksheet.write(row, 2, event.location, cell_format)
                    worksheet.write(row, 3, 'Ativo' if event.active else 'Inativo', cell_format)
                    worksheet.write(row, 4, ticket_type.name, cell_format)
                    worksheet.write_number(row, 5, float(ticket_type.price), money_format)
                    worksheet.write_number(row, 6, ticket_type.quantity, cell_format)
                    worksheet.write_number(row, 7, ticket_type.sold, cell_format)
                    worksheet.write_number(row, 8, ticket_type.available(), cell_format)
                    row += 1
            else:
                worksheet.write(row, 0, event.title, cell_format)
                worksheet.write_datetime(row, 1, event.date.replace(tzinfo=None), date_format)
                worksheet.write(row, 2, event.location, cell_format)
                worksheet.write(row, 3, 'Ativo' if event.active else 'Inativo', cell_format)
                row += 1

        worksheet.set_column('A:A', 32)
        worksheet.set_column('B:B', 22)
        worksheet.set_column('C:C', 28)
        worksheet.set_column('D:D', 14)
        worksheet.set_column('E:E', 24)
        worksheet.set_column('F:F', 16)
        worksheet.set_column('G:G', 14)
        
        worksheet.set_column(0, 0, row, len(headers) - 1)
        worksheet.freeze_panes(1, 0)
        
        workbook.close()
        output.seek(0)
        
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="eventos.xlsx"'
        
        return response