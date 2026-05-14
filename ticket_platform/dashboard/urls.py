from django.urls import path

from .views import ConfirmPaymentView, DashboardHomeView, DashboardOrderListView, DashboardLogoutView


app_name = 'dashboard'

urlpatterns = [
    path('painel/', DashboardHomeView.as_view(), name='home'),
    path('painel/pedidos/', DashboardOrderListView.as_view(), name='order_list'),
    path(
        'painel/pedidos/<int:pk>/confirmar-pagamento/',
        ConfirmPaymentView.as_view(),
        name='confirm_payment'
    ),
    path('painel/sair/', DashboardLogoutView.as_view(), name='logout')
]