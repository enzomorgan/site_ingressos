from django.urls import path

from .views import MyTicketsView


app_name = 'tickets'

urlpatterns = [
    path('meus-ingressos/', MyTicketsView.as_view(), name='my_tickets'),
]