from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomerRegisterForm, ProfileUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView
from orders.models import Order
from tickets.models import Ticket

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
    
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['total_orders'] = Order.objects.filter(
            user=self.request.user,
        ).count()
        
        context['paid_orders'] = Order.objects.filter(
            user=self.request.user,
            status=Order.STATUS_PAID
        ).count()
        
        context['pending_orders'] = Order.objects.filter(
            user=self.request.user,
            status=Order.STATUS_PENDING
        ).count()
        
        context['total_tickets'] = Ticket.objects.filter(
            order__user=self.request.user
        ).count()
        
        return context
    
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUpdateForm
    template_name = 'users/profile_form.html'
    success_url = reverse_lazy('users:profile')
    login_url = '/login/'
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso.')
        return super().form_valid(form)