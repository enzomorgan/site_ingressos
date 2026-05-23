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
    
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'E-mail'
            }),
        }
        
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'E-mail',
        }
    
    def clean_email(self):
        email = self.clean_data.get('email')
        
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Já existe uma conta com este e-mail.')
        
        return email