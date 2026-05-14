from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Ticket

class MyTicketsView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/my_tickets.html'
    context_object_name = 'tickets'
    login_url = '/login'
    
    def get_queryset(self):
        return Ticket.objects.filter(
            order__user=self.request.user
        ).select_related(
            'order'
        ).prefetch_related(
            'order__items',
            'order__items__ticket_type',
            'order__items__ticket_type__event'
        ).order_by('-created_at')