# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Vuelo,Avion



class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, label='Nombre')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']


class VueloForm(forms.ModelForm):
    class Meta:
        model = Vuelo
        fields = ['origen', 'destino', 'fecha', 'hora', 'duracion']
    
class AvionForm(forms.ModelForm):
    class Meta:
        model = Avion
        fields = ['modelo', 'capacidad', 'fabricante', 'anio_fabricacion']