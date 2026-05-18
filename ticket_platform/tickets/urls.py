from django.urls import path

from .views import MyTicketsView, TicketDetailView


app_name = 'tickets'

urlpatterns = [
    path('meus-ingressos/', MyTicketsView.as_view(), name='my_tickets'),
    path('meus-ingressos/<int:pk>/', TicketDetailView.as_view(), name='ticket_detail'),
]