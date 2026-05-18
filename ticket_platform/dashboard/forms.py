from django import forms
from events.models import Event, TicketType

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            'title',
            'description',
            'date',
            'location',
            'banner',
            'active',
        )
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do evento'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descrição do evento'
            }),
            'date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Local do evento'
            }),
            'banner': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check'
            }),
        }
        
        labels = {
            'title': 'Título',
            'description': 'Descrição',
            'date': 'Data e Hora',
            'location': 'Local',
            'banner': 'Banner',
            'active': 'Evento ativo',
        }

class TicketTypeForm(forms.ModelForm):
    class Meta:
        model = TicketType
        fields = (
            'name',
            'price',
            'quantity',
        )
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Pista, VIP, Camarote'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
        }
        
        labels = {
            'name': 'Nome do ingresso',
            'price': 'Preço',
            'quantity': 'Quantidade total',
        }
        
    def clean_price(self):
        price = self.cleaned_data.get('price')
        
        if price is not None and price < 0:
            raise forms.ValidationError('O preço não pode ser negativo.')
        
        return price
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError('A quantidade deve ser maior que zero.')
        
        return quantity