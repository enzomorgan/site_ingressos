from django.urls import path

from .views import (
    ConfirmPaymentView,
    DashboardEventCreateView,
    DashboardEventListView,
    DashboardEventUpdateView,
    DashboardHomeView,
    DashboardLogoutView,
    DashboardOrderListView,
)


app_name = 'dashboard'

urlpatterns = [
    path('painel/', DashboardHomeView.as_view(), name='home'),
    path('painel/eventos', DashboardEventListView.as_view(), name='event_list'),
    path('painel/eventos/novo', DashboardEventCreateView.as_view(), name='event_create'),
    path('painel/eventos/<int:pk>/editar/', DashboardEventUpdateView.as_view(), name='event_update'),
    path('painel/pedidos/', DashboardOrderListView.as_view(), name='order_list'),
    path(
        'painel/pedidos/<int:pk>/confirmar-pagamento/',
        ConfirmPaymentView.as_view(),
        name='confirm_payment'
    ),
    path('painel/sair/', DashboardLogoutView.as_view(), name='logout')
]