from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomerRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='E-mail'
    )
    
    first_name = forms.CharField(
        required=True,
        label='Nome'
    )
    
    last_name = forms.CharField(
        required=True,
        label='Sobrenome'
    )
    
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        )
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
            
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Já existe uma conta com esse e-mail.')
            
        return email