from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import AvionForm 
from .models import Avion
from django.views.decorators.csrf import csrf_exempt


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario registrado correctamente. Ahora podés iniciar sesión.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'usuarios/register.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # o 'home' si querés
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Aquí redirige al home
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})
def home(request):
    return render(request, 'usuarios/home.html')




def lista_aviones(request):
    if request.method == "POST":
        if 'delete_id' in request.POST:
            # Eliminar avión
            avion = get_object_or_404(Avion, id=request.POST['delete_id'])
            avion.delete()
            return redirect('lista_aviones')

        elif 'edit_id' in request.POST:
            # Editar avión
            avion = get_object_or_404(Avion, id=request.POST['edit_id'])
            avion.modelo = request.POST.get('modelo', avion.modelo)
            avion.fabricante = request.POST.get('fabricante', avion.fabricante)
            avion.capacidad = request.POST.get('capacidad', avion.capacidad)
            avion.save()
            return redirect('lista_aviones')

    aviones = Avion.objects.all()
    return render(request, 'usuarios/lista_aviones.html', {'aviones': aviones})
def crear_avion(request):
    if request.method == 'POST':
        form = AvionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_aviones')
    else:
        form = AvionForm()
    return render(request, 'usuarios/crear_avion.html', {'form': form})

