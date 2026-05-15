from django import forms
from events.models import Event

class EventForm(forms.ModelForm):
    class Meta:
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