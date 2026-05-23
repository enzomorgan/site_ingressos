from django.urls import path
from .views import CreateOrderView, MyOrderDetailView , OrderSuccessView, MyOrderView

app_name = 'orders'

urlpatterns = [
    path('comprar/', CreateOrderView.as_view(), name='create_order'),
    path('pedido/<int:pk>/sucesso/', OrderSuccessView.as_view(), name='order_success'),
    path('meus-pedidos/', MyOrderView.as_view(), name='my_orders'),
    path('meus-pedidos/<int:pk>/', MyOrderDetailView.as_view(), name='my_order_detail'),
]
