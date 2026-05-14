from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomerRegisterForm

class CustomerRegisterView(CreateView):
    form_class = CustomerRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('events:event_list')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, 'Conta criada com sucesso.')
        return redirect(self.success_url)
    
class CustomerLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('events:event_list')
    
class CustomerLogoutView(LogoutView):
    next_page = reverse_lazy('events:event_list')