from django.urls import path
from . import views
from .views import registrar_avion

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('vuelos/', views.vuelos, name='vuelos'),
    path('pasajeros/', views.pasajeros, name='pasajeros'),
    path('reservas/', views.reservas, name='reservas'),

    path('home/', views.home, name='home'),  # ruta raíz de la app
    path('registrar-avion/', registrar_avion, name='registrar_avion'),
    path('avion/crear/', views.crear_avion, name='crear_avion'),
    path('avion/nuevo/', views.crear_avion, name='crear_avion'),
    path('aviones/', views.lista_aviones, name='lista_aviones'),
    path('aviones/crear/', views.crear_avion, name='crear_avion'),
    path('aviones/', views.lista_aviones, name='lista_aviones'),

]
