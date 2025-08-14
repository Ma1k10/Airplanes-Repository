# gestion_aerolinea/forms.py
from django import forms
from .models import Avion, Asiento, Reserva,Vuelo # Importa los modelos necesarios

class AvionForm(forms.ModelForm):
    class Meta:
        model = Avion
        fields = ['modelo', 'matricula', 'capacidad_asientos']
        widgets = {
            'modelo': forms.TextInput(attrs={'class': 'form-control'}),
            'matricula': forms.TextInput(attrs={'class': 'form-control'}),
            'capacidad_asientos': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

class ReservaForm(forms.Form): # Not ModelForm for multiple seats
    asientos_seleccionados = forms.ModelMultipleChoiceField(
        queryset=Asiento.objects.none(), # Will be set dynamically in the view
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Seleccione hasta 4 asientos."
    )

    def clean_asientos_seleccionados(self):
        asientos = self.cleaned_data['asientos_seleccionados']
        if len(asientos) == 0:
            raise forms.ValidationError("Debes seleccionar al menos un asiento.")
        if len(asientos) > 4:
            raise forms.ValidationError("No puedes seleccionar más de 4 asientos a la vez.")
        for asiento in asientos:
            if not asiento.esta_disponible:
                raise forms.ValidationError(f"El asiento {asiento.numero_asiento} ya no está disponible.")
        return asientos
class VueloForm(forms.ModelForm):
    class Meta:
        model = Vuelo
        fields = ['origen', 'destino', 'fecha_salida', 'hora_salida', 'duracion_minutos', 'avion']
        # If you want to automatically set the 'avion' in the view and not show it in the form:
        # exclude = ['avion']
        widgets = {
            'fecha_salida': forms.DateInput(attrs={'type': 'date'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time'}),
        }