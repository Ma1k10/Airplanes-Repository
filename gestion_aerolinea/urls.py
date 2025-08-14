# gestion_aerolinea/urls.py
from django.urls import path
from . import views
# Remove 'from django.contrib.auth import views as auth_views' from here
# if you're including 'django.contrib.auth.urls' in your project-level urls.py

urlpatterns = [
    path('', views.home, name='home'),
    path('vuelos/', views.lista_vuelos, name='lista_vuelos'),
    path('vuelos/<int:vuelo_id>/', views.detalle_vuelo, name='detalle_vuelo'),

    # Use the correct 'reservar_asientos' URL as per our last discussion (plural for multiple seats)
    path('vuelos/<int:vuelo_id>/reservar/', views.reservar_asientos, name='reservar_asientos'),

    path('mis_reservas/', views.mis_reservas, name='mis_reservas'),

    # Changed 'reportes' to 'reporte' for consistency, ensure view name matches
    path('reporte/pasajeros-por-vuelo/', views.reporte_pasajeros_por_vuelo, name='reporte_pasajeros_por_vuelo'),

    # URLs for Aviones (cleaned up duplicates)
    path('aviones/', views.lista_aviones, name='lista_aviones'),
    path('aviones/crear/', views.crear_avion, name='crear_avion'),
    path('aviones/editar/<int:pk>/', views.editar_avion, name='editar_avion'),
    path('aviones/eliminar/<int:pk>/', views.eliminar_avion, name='eliminar_avion'),

    # URL for your custom signup view
    path('signup/', views.signup, name='signup'),
    path('vuelos/<int:vuelo_id>/asientos/', views.detalle_asientos_vuelo, name='detalle_asientos_vuelo'), # <-- ADD THIS NEW URL
    path('aviones/<int:avion_id>/vuelos/', views.vuelos_por_avion, name='vuelos_por_avion'),
    # URL for listing flights for a specific airplane
    path('aviones/<int:avion_id>/vuelos/', views.vuelos_por_avion, name='vuelos_por_avion'),

    # NEW: URL to program a flight for a specific airplane
    path('aviones/<int:avion_id>/programar-vuelo/', views.programar_vuelo, name='programar_vuelo'),
   
]