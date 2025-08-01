from django.contrib import admin
from .models import Avion, Vuelo, Asiento, Pasajero, Reserva, Boleto

admin.site.register(Vuelo)
admin.site.register(Asiento)
admin.site.register(Pasajero)
admin.site.register(Reserva)
admin.site.register(Boleto)
admin.site.register(Avion)