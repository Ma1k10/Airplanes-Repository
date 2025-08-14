# gestion_aerolinea/tests.py
from django.test import TestCase
from .models import Avion, Vuelo, Pasajero, Asiento, Reserva
from django.contrib.auth.models import User

class AvionModelTest(TestCase):
    def test_avion_creation(self):
        avion = Avion.objects.create(modelo="Boeing 747", matricula="LV-ABC", capacidad_asientos=400)
        self.assertEqual(avion.modelo, "Boeing 747")
        self.assertEqual(avion.matricula, "LV-ABC")

# Agrega más pruebas para otros modelos y vistas