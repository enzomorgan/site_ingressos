from django.urls import path
from .views import CreateOrderView, OrderSuccessView

app_name = 'orders'

urlpatterns = [
    path('compar/', CreateOrderView.as_view(), name='create_order'),
    path('pedido/<int:pk>sucesso/', OrderSuccessView.as_view(), name='order_success'),
]
