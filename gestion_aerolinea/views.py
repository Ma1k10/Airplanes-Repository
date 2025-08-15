# gestion_aerolinea/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Vuelo, Pasajero, Asiento, Reserva, Avion
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db import transaction
from django.forms import ModelForm # Para formularios basados en modelos
from django.contrib import messages
from .forms import AvionForm # Importa el formulario de Aviones
from django import forms # <-- ADD THIS LINE
from django.http import HttpResponse
from reportlab.pdfgen import canvas # You likely have this
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors # You likely have this
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer # <-- ADD/ENSURE THIS LINE
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # <-- ADD/ENSURE THIS LINE
from io import BytesIO


def home(request):
    """
    Vista de la página de inicio.
    Redirige a 'signup' si el usuario no está autenticado.
    """
    if not request.user.is_authenticated:
        return redirect('signup') # Redirige al usuario no autenticado a la página de registro
    
    # Si el usuario está autenticado, procede a renderizar la página de inicio
    return render(request, 'gestion_aerolinea/home.html')

# --- Formularios ---
class PasajeroForm(ModelForm):
    class Meta:
        model = Pasajero
        fields = ['nombre', 'apellido', 'documento', 'email', 'telefono']

class ReservaForm(ModelForm):
    class Meta:
        model = Reserva
        fields = ['asiento'] # El pasajero se asignará automáticamente

# --- Vistas ---

def signup(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        pasajero_form = PasajeroForm(request.POST)
        if user_form.is_valid() and pasajero_form.is_valid():
            try:
                with transaction.atomic(): # Ensure atomicity for User and Pasajero creation
                    user = user_form.save()
                    pasajero = pasajero_form.save(commit=False)
                    pasajero.usuario = user
                    pasajero.email = user.email # Ensure passenger's email matches user's
                    pasajero.save()

                login(request, user) # Log in the user automatically after successful registration
                messages.success(request, '¡Registro exitoso! Bienvenido a Aerolínea XYZ.')
                return redirect('home') # Redirect to home or a welcome page
            except Exception as e:
                messages.error(request, f'Ocurrió un error durante el registro: {e}')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        user_form = UserCreationForm()
        pasajero_form = PasajeroForm()
    return render(request, 'registration/signup.html', {
        'user_form': user_form,
        'pasajero_form': pasajero_form
    })

def lista_vuelos(request):
    vuelos = Vuelo.objects.all().order_by('fecha_salida', 'hora_salida')
    return render(request, 'gestion_aerolinea/lista_vuelos.html', {'vuelos': vuelos})

def detalle_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    asientos_disponibles = Asiento.objects.filter(vuelo=vuelo, esta_disponible=True)
    return render(request, 'gestion_aerolinea/detalle_vuelo.html', {
        'vuelo': vuelo,
        'asientos_disponibles': asientos_disponibles
    })

@login_required
def reservar_asiento(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    
    # Asegúrate de que el usuario logueado tenga un perfil de Pasajero
    try:
        pasajero = request.user.pasajero
    except Pasajero.DoesNotExist:
        # Si el usuario no tiene un perfil de pasajero, crea uno
        pasajero = Pasajero.objects.create(usuario=request.user, 
                                            nombre=request.user.first_name or request.user.username, 
                                            apellido=request.user.last_name or '', 
                                            documento='N/A', # Deberías pedir esto en el registro
                                            email=request.user.email)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            asiento_id = form.cleaned_data['asiento'].id
            asiento = get_object_or_404(Asiento, pk=asiento_id, vuelo=vuelo, esta_disponible=True)
            
            with transaction.atomic(): # Asegura la integridad de la reserva
                if not asiento.esta_disponible:
                    # Manejar error: asiento ya no disponible
                    return render(request, 'gestion_aerolinea/detalle_vuelo.html', {
                        'vuelo': vuelo,
                        'asientos_disponibles': Asiento.objects.filter(vuelo=vuelo, esta_disponible=True),
                        'error_message': 'El asiento ya no está disponible.'
                    })
                
                reserva = form.save(commit=False)
                reserva.pasajero = pasajero
                reserva.asiento = asiento
                reserva.estado = 'RESERVADO'
                reserva.save()
                
                # Generar boletos electrónicos (simulado)
                # Esto podría ser una función que genere un PDF o un simple ID
                request.session['boleto_info'] = {
                    'reserva_id': reserva.id,
                    'vuelo': str(vuelo),
                    'asiento': asiento.numero_asiento,
                    'pasajero': str(pasajero),
                }

                return redirect('mis_reservas') # Redirigir a las reservas del usuario
        else:
            # Si el formulario no es válido, renderizar de nuevo con errores
            asientos_disponibles = Asiento.objects.filter(vuelo=vuelo, esta_disponible=True)
            return render(request, 'gestion_aerolinea/detalle_vuelo.html', {
                'vuelo': vuelo,
                'asientos_disponibles': asientos_disponibles,
                'form': form # Pasa el formulario con errores
            })
    else:
        # Crear instancias de AsientoForm para cada asiento disponible
        asientos_disponibles = Asiento.objects.filter(vuelo=vuelo, esta_disponible=True)
        form = ReservaForm() # Formulario vacío para GET
        return render(request, 'gestion_aerolinea/detalle_vuelo.html', {
            'vuelo': vuelo,
            'asientos_disponibles': asientos_disponibles,
            'form': form
        })

@login_required
def mis_reservas(request):
    try:
        pasajero = request.user.pasajero
        reservas = Reserva.objects.filter(pasajero=pasajero).select_related('asiento', 'asiento__vuelo')
    except Pasajero.DoesNotExist:
        reservas = []
    
    boleto_info = request.session.pop('boleto_info', None) # Obtener y eliminar info del boleto
    return render(request, 'gestion_aerolinea/mis_reservas.html', {
        'reservas': reservas,
        'boleto_info': boleto_info
    })

def signup(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        pasajero_form = PasajeroForm(request.POST)
        if user_form.is_valid() and pasajero_form.is_valid():
            user = user_form.save()
            pasajero = pasajero_form.save(commit=False)
            pasajero.usuario = user
            pasajero.email = user.email # Asegurar que el email del pasajero coincida con el del usuario
            pasajero.save()
            login(request, user)
            return redirect('home')
    else:
        user_form = UserCreationForm()
        pasajero_form = PasajeroForm()
    return render(request, 'registration/signup.html', {
        'user_form': user_form,
        'pasajero_form': pasajero_form
    })

@login_required # Solo usuarios logueados pueden ver reportes
def reporte_pasajeros_por_vuelo(request):
    vuelos = Vuelo.objects.all().order_by('fecha_salida')
    reporte_data = []
    for vuelo in vuelos:
        reservas_vuelo = Reserva.objects.filter(asiento__vuelo=vuelo, estado__in=['RESERVADO', 'OCUPADO'])
        pasajeros = [reserva.pasajero for reserva in reservas_vuelo]
        reporte_data.append({
            'vuelo': vuelo,
            'pasajeros': pasajeros
        })
    return render(request, 'gestion_aerolinea/reporte_pasajeros_por_vuelo.html', {'reporte_data': reporte_data})
def home(request):
    return render(request, 'gestion_aerolinea/home.html') # <-- 'gestion_aerolinea/home.html' es la ruta relativa desde la carpeta 'templates' de la app
@login_required
def crear_avion(request):
    if request.method == 'POST':
        form = AvionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Avión creado exitosamente!')
            return redirect('lista_aviones') # Redirigir a una lista de aviones
    else:
        form = AvionForm()
    return render(request, 'gestion_aerolinea/crear_editar_avion.html', {'form': form, 'titulo': 'Crear Avión'})

@login_required
def editar_avion(request, pk):
    avion = get_object_or_404(Avion, pk=pk)
    if request.method == 'POST':
        form = AvionForm(request.POST, instance=avion)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Avión actualizado exitosamente!')
            return redirect('lista_aviones')
    else:
        form = AvionForm(instance=avion)
    return render(request, 'gestion_aerolinea/crear_editar_avion.html', {'form': form, 'titulo': 'Editar Avión'})

@login_required
def lista_aviones(request):
    aviones = Avion.objects.all().order_by('modelo')
    return render(request, 'gestion_aerolinea/lista_aviones.html', {'aviones': aviones})

@login_required
def eliminar_avion(request, pk):
    avion = get_object_or_404(Avion, pk=pk)
    if request.method == 'POST':
        avion.delete()
        messages.success(request, 'Avión eliminado correctamente.')
        return redirect('lista_aviones')
    return render(request, 'gestion_aerolinea/confirmar_eliminar.html', {'objeto': avion, 'tipo': 'Avión'})


@login_required
def reservar_asientos(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)

    try:
        pasajero = request.user.pasajero
    except Pasajero.DoesNotExist:
        messages.error(request, "Por favor, completa tu perfil de pasajero para realizar reservas.")
        return redirect('signup') # O a una página de perfil para completar datos

    # Obtener asientos disponibles para este vuelo
    asientos_disponibles = vuelo.get_asientos_disponibles()

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        # Establecer el queryset para el campo de asientos antes de la validación
        form.fields['asientos_seleccionados'].queryset = asientos_disponibles

        if form.is_valid():
            selected_asientos = form.cleaned_data['asientos_seleccionados']
            
            if not selected_asientos:
                messages.error(request, "Debes seleccionar al menos un asiento.")
                # Renderizar la plantilla con el formulario y los errores
                return render(request, 'gestion_aerolinea/detalle_vuelo.html', {
                    'vuelo': vuelo,
                    'asientos_disponibles': asientos_disponibles, # Para la visualización del mapa
                    'form': form, # Pasar el formulario con errores
                })

            # Usar una transacción atómica para asegurar que todas las reservas se creen o ninguna
            try:
                with transaction.atomic():
                    created_reservas = []
                    for asiento_a_reservar in selected_asientos:
                        # Re-verificar la disponibilidad justo antes de crear la reserva (evitar condiciones de carrera)
                        # select_for_update bloquea la fila para evitar que otro proceso la modifique
                        asiento_actualizado = Asiento.objects.select_for_update().get(pk=asiento_a_reservar.pk)

                        if not asiento_actualizado.esta_disponible:
                            # Si un asiento no está disponible, se revierte toda la transacción
                            raise ValueError(f"El asiento {asiento_actualizado.numero_asiento} ya no está disponible.")

                        # Crear la reserva para cada asiento seleccionado
                        reserva = Reserva.objects.create(
                            pasajero=pasajero,
                            asiento=asiento_actualizado,
                            estado='RESERVADO' # Se actualizará la disponibilidad del asiento en el save() de Reserva
                        )
                        created_reservas.append(reserva)

                    messages.success(request, f'¡Tu reserva de {len(created_reservas)} asiento(s) ha sido creada exitosamente!')
                    # Redirigir a mis_reservas, quizás mostrando los nuevos boletos
                    # Podrías pasar los IDs de las nuevas reservas a la sesión para mostrarlos específicamente
                    request.session['nuevas_reservas_ids'] = [r.id for r in created_reservas]
                    return redirect('mis_reservas')

            except ValueError as e:
                messages.error(request, f'Error al procesar la reserva: {e}')
            except Exception as e:
                messages.error(request, f'Ocurrió un error inesperado al reservar: {e}')

            # Si hay un error, el formulario se re-renderiza con el error
            form = ReservaForm(initial={'asientos_seleccionados': selected_asientos}) # Para mantener la selección
            form.fields['asientos_seleccionados'].queryset = asientos_disponibles # Reestablecer queryset

    else: # GET request
        form = ReservaForm()
        # Establecer el queryset para el campo de asientos al cargar la página
        form.fields['asientos_seleccionados'].queryset = asientos_disponibles

    return render(request, 'gestion_aerolinea/detalle_vuelo.html', {
        'vuelo': vuelo,
        'asientos_disponibles': asientos_disponibles, # Pasar esto para la visualización del mapa
        'form': form, # Pasar el formulario al template
    })

# Actualizar mis_reservas para mostrar nuevas reservas
@login_required
def mis_reservas(request):
    try:
        pasajero = request.user.pasajero
        reservas = Reserva.objects.filter(pasajero=pasajero).select_related('asiento', 'asiento__vuelo').order_by('-fecha_reserva')
    except Pasajero.DoesNotExist:
        messages.info(request, "Aún no tienes un perfil de pasajero. Por favor, completa tu registro.")
        return redirect('signup')

    nuevas_reservas_ids = request.session.pop('nuevas_reservas_ids', [])
    nuevas_reservas_info = []
    if nuevas_reservas_ids:
        # Obtener los objetos de las nuevas reservas para mostrar su información completa
        nuevas_reservas_info = Reserva.objects.filter(id__in=nuevas_reservas_ids).select_related('asiento', 'asiento__vuelo')

    return render(request, 'gestion_aerolinea/mis_reservas.html', {
        'reservas': reservas,
        'nuevas_reservas_info': nuevas_reservas_info,
    })

def lista_vuelos(request):
    vuelos = Vuelo.objects.all().order_by('fecha_salida', 'hora_salida')
    return render(request, 'gestion_aerolinea/lista_vuelos.html', {'vuelos': vuelos})
class PasajeroForm(forms.ModelForm): # Changed to forms.ModelForm
    class Meta:
        model = Pasajero
        fields = ['nombre', 'apellido', 'documento', 'email', 'telefono']

class ReservaForm(forms.Form): # Now 'forms.Form' is recognized
    # This field needs to be defined using forms.ModelMultipleChoiceField
    asientos_seleccionados = forms.ModelMultipleChoiceField( # Now 'forms.ModelMultipleChoiceField' is recognized
        queryset=Asiento.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        help_text="Seleccione hasta 4 asientos."
    )

    def clean_asientos_seleccionados(self):
        asientos = self.cleaned_data['asientos_seleccionados']
        if len(asientos) > 4:
            raise forms.ValidationError("No puedes seleccionar más de 4 asientos a la vez.")
        for asiento in asientos:
            if not asiento.esta_disponible:
                raise forms.ValidationError(f"El asiento {asiento.numero_asiento} ya no está disponible.")
        return asientos

@login_required # Only logged-in users can reserve
def reservar_asientos(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)

    # Ensure the logged-in user has a Pasajero profile
    try:
        pasajero = request.user.pasajero
    except Pasajero.DoesNotExist:
        messages.error(request, "Por favor, completa tu perfil de pasajero para realizar reservas.")
        # Redirect to signup or a profile completion page if needed
        return redirect('signup') # Or whatever URL leads to profile completion

    asientos_disponibles = vuelo.get_asientos_disponibles() # Assuming this method exists

    if request.method == 'POST':
        form = ReservaForm(request.POST)
        # Important: Set the queryset for the form field *before* calling is_valid()
        form.fields['asientos_seleccionados'].queryset = asientos_disponibles

        if form.is_valid():
            selected_asientos = form.cleaned_data['asientos_seleccionados']
            
            try:
                with transaction.atomic(): # Ensures all reservations are created or none
                    created_reservas = []
                    for asiento_a_reservar in selected_asientos:
                        # Lock the row to prevent race conditions
                        asiento_actualizado = Asiento.objects.select_for_update().get(pk=asiento_a_reservar.pk)

                        if not asiento_actualizado.esta_disponible:
                            # If an seat is no longer available, roll back the entire transaction
                            raise ValueError(f"El asiento {asiento_actualizado.numero_asiento} ya no está disponible.")

                        # Create the reservation for each selected seat
                        reserva = Reserva.objects.create(
                            pasajero=pasajero,
                            asiento=asiento_actualizado,
                            estado='RESERVADO' # Assuming 'RESERVADO' is a valid state
                        )
                        created_reservas.append(reserva)

                    messages.success(request, f'¡Tu reserva de {len(created_reservas)} asiento(s) ha sido creada exitosamente!')
                    # Store new reservation IDs in session to display them on mis_reservas
                    request.session['nuevas_reservas_ids'] = [r.id for r in created_reservas]
                    return redirect('mis_reservas')

            except ValueError as e:
                messages.error(request, f'Error al procesar la reserva: {e}')
            except Exception as e:
                messages.error(request, f'Ocurrió un error inesperado al reservar: {e}')
            
            # If there's an error during the transaction, re-render the form with errors
            # Re-instantiate the form with POST data and set queryset again
            form = ReservaForm(request.POST)
            form.fields['asientos_seleccionados'].queryset = asientos_disponibles

        # If form is not valid, it falls through here, and the form with errors is rendered
    else: # GET request to this URL should ideally not happen if coming from a form submission
        # If a GET request somehow reaches here, redirect it or show an empty form
        form = ReservaForm()
        form.fields['asientos_seleccionados'].queryset = asientos_disponibles # Set queryset for GET too

    # This render is for when the form is invalid or an exception occurs during POST
    return render(request, 'gestion_aerolinea/detalle_vuelo.html', {
        'vuelo': vuelo,
        'asientos_disponibles': asientos_disponibles, # Pass for rendering the seat map
        'form': form, # Pass the form (possibly with errors)
    })
@login_required # Optional: Restrict seat viewing to logged-in users
def detalle_asientos_vuelo(request, vuelo_id):
    vuelo = get_object_or_404(Vuelo, pk=vuelo_id)
    # Fetch all seats related to this specific vuelo
    # Assuming your Asiento model has a ForeignKey to Vuelo with related_name='asientos'
    asientos = vuelo.asientos.all().order_by('numero_asiento')

    return render(request, 'gestion_aerolinea/detalle_asientos_vuelo.html', {
        'vuelo': vuelo,
        'asientos': asientos,
    })
@login_required # Optional: require login to see flights per plane
def vuelos_por_avion(request, avion_id):
    avion = get_object_or_404(Avion, pk=avion_id)
    vuelos = Vuelo.objects.filter(avion=avion).order_by('fecha_salida', 'hora_salida')

    return render(request, 'gestion_aerolinea/vuelos_por_avion.html', {
        'avion': avion,
        'vuelos': vuelos,
    })
class VueloForm(forms.ModelForm):
    class Meta:
        model = Vuelo
        # Exclude 'avion' from fields if you're setting it dynamically,
        # or include it if you want it as a dropdown
        fields = ['origen', 'destino', 'fecha_salida', 'hora_salida', 'duracion_minutos', 'avion']
        # If you want to automatically set the avion based on URL:
        # fields = ['origen', 'destino', 'fecha_salida', 'hora_salida', 'duracion_minutos']
        widgets = {
            'fecha_salida': forms.DateInput(attrs={'type': 'date'}),
            'hora_salida': forms.TimeInput(attrs={'type': 'time'}),
        }
@login_required
def programar_vuelo(request, avion_id):
    avion = get_object_or_404(Avion, pk=avion_id)

    if request.method == 'POST':
        # Pass instance=avion if AvionForm is for editing, not creating.
        # Here, VueloForm is for creating a Vuelo.
        form = VueloForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    vuelo = form.save(commit=False)
                    vuelo.avion = avion # Assign the airplane from the URL
                    vuelo.save()

                    # Now, create seats for the new flight based on the airplane's capacity
                    for i in range(1, avion.capacidad_asientos + 1):
                        Asiento.objects.create(vuelo=vuelo, numero_asiento=f'A-{i}', esta_disponible=True)
                        # You might use more sophisticated seat numbering (e.g., 1A, 1B, 2A)
                        # For now, A-1, A-2, etc. is fine as a placeholder.

                messages.success(request, f'Vuelo de {vuelo.origen} a {vuelo.destino} programado con éxito y asientos creados.')
                return redirect('detalle_asientos_vuelo', vuelo_id=vuelo.id) # Redirect to view seats for new flight
            except Exception as e:
                messages.error(request, f'Error al programar el vuelo: {e}')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else: # GET request
        # For GET, if you want to pre-select the airplane in the form,
        # you can pass initial data or filter the queryset for the 'avion' field.
        # If 'avion' is excluded from fields, it's not needed here.
        form = VueloForm(initial={'avion': avion}) # This pre-selects the avion if 'avion' is in form.Meta.fields

    return render(request, 'gestion_aerolinea/programar_vuelo.html', {
        'form': form,
        'avion': avion,
    })
@login_required # Only allow logged-in users to generate their tickets
def generar_boleto_pdf(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)

    # Security check: Ensure the logged-in user owns this reservation
    if reserva.pasajero.usuario != request.user:
        messages.error(request, 'No tienes permiso para ver este boleto.')
        return redirect('mis_reservas')

    # Create a file-like buffer to receive PDF data.
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its file.
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=inch, leftMargin=inch,
                            topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()

    # Define a custom style for the ticket details
    ticket_style = ParagraphStyle(
        'TicketDetail',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        spaceAfter=6,
    )

    elements = []

    # Title
    elements.append(Paragraph("<b>AEROLÍNEA XYZ - Boleto Electrónico</b>", styles['h1']))
    elements.append(Spacer(1, 0.2 * inch))

    # Basic Info
    elements.append(Paragraph(f"<b>Código de Boleto:</b> {reserva.codigo_boleto}", ticket_style))
    elements.append(Paragraph(f"<b>Estado:</b> {reserva.estado}", ticket_style))
    elements.append(Spacer(1, 0.1 * inch))

    # Passenger Details
    elements.append(Paragraph("<b>Datos del Pasajero:</b>", styles['h2']))
    elements.append(Paragraph(f"<b>Nombre:</b> {reserva.pasajero.nombre} {reserva.pasajero.apellido}", ticket_style))
    elements.append(Paragraph(f"<b>Documento:</b> {reserva.pasajero.documento}", ticket_style))
    elements.append(Paragraph(f"<b>Email:</b> {reserva.pasajero.email}", ticket_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Flight Details
    elements.append(Paragraph("<b>Datos del Vuelo:</b>", styles['h2']))
    elements.append(Paragraph(f"<b>Origen:</b> {reserva.asiento.vuelo.origen}", ticket_style))
    elements.append(Paragraph(f"<b>Destino:</b> {reserva.asiento.vuelo.destino}", ticket_style))
    elements.append(Paragraph(f"<b>Fecha de Salida:</b> {reserva.asiento.vuelo.fecha_salida.strftime('%d/%m/%Y')}", ticket_style))
    elements.append(Paragraph(f"<b>Hora de Salida:</b> {reserva.asiento.vuelo.hora_salida.strftime('%H:%M')}", ticket_style))
    elements.append(Paragraph(f"<b>Duración:</b> {reserva.asiento.vuelo.duracion_minutos} minutos", ticket_style))
    elements.append(Paragraph(f"<b>Avión:</b> {reserva.asiento.vuelo.avion.modelo} (Matrícula: {reserva.asiento.vuelo.avion.matricula})", ticket_style))
    elements.append(Paragraph(f"<b>Asiento Asignado:</b> {reserva.asiento.numero_asiento}", ticket_style))
    elements.append(Spacer(1, 0.2 * inch))

    # Footer
    elements.append(Paragraph("<i>Gracias por volar con Aerolínea XYZ.</i>", styles['Italic']))

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and make it an HTTP response.
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boleto_{reserva.codigo_boleto}.pdf"' # Forces download
    # response['Content-Disposition'] = f'inline; filename="boleto_{reserva.codigo_boleto}.pdf"' # Displays in browser

    return response