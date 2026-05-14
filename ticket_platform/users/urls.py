from django.urls import path

from .views import CustomerLoginView, CustomerLogoutView, CustomerRegisterView


app_name = 'users'

urlpatterns = [
    path('cadastro/', CustomerRegisterView.as_view(), name='register'),
    path('login/', CustomerLoginView.as_view(), name='login'),
    path('logout/', CustomerLogoutView.as_view(), name='logout'),
]