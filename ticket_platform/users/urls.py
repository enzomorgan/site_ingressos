from django.urls import path

from .views import CustomerLoginView, CustomerLogoutView, CustomerRegisterView, ProfileView, ProfileUpdateView


app_name = 'users'

urlpatterns = [
    path('cadastro/', CustomerRegisterView.as_view(), name='register'),
    path('login/', CustomerLoginView.as_view(), name='login'),
    path('logout/', CustomerLogoutView.as_view(), name='logout'),
    path('perfil/', ProfileView.as_view(), name='profile'),
    path('perfil/editar/', ProfileUpdateView.as_view(), name='profile_edit'),
]