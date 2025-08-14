# gestion_aerolinea/admin.py
from django.contrib import admin
from .models import Avion, Vuelo, Pasajero, Asiento, Reserva

@admin.register(Avion)
class AvionAdmin(admin.ModelAdmin):
    list_display = ('modelo', 'matricula', 'capacidad_asientos')
    search_fields = ('modelo', 'matricula')

@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    list_display = ('origen', 'destino', 'fecha_salida', 'hora_salida', 'avion')
    list_filter = ('origen', 'destino', 'fecha_salida')
    search_fields = ('origen', 'destino')
    raw_id_fields = ('avion',) # Para seleccionar aviones por ID en el admin

@admin.register(Pasajero)
class PasajeroAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'documento', 'email')
    search_fields = ('nombre', 'apellido', 'documento', 'email')

@admin.register(Asiento)
class AsientoAdmin(admin.ModelAdmin):
    list_display = ('vuelo', 'numero_asiento', 'esta_disponible')
    list_filter = ('esta_disponible', 'vuelo')
    search_fields = ('numero_asiento',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('pasajero', 'asiento', 'fecha_reserva', 'estado')
    list_filter = ('estado', 'fecha_reserva')
    search_fields = ('pasajero__nombre', 'pasajero__apellido', 'asiento__numero_asiento')
    raw_id_fields = ('pasajero', 'asiento') # Para seleccionar pasajeros y asientos por ID