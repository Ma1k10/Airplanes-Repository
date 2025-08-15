# gestion_aerolinea/models.py
from django.db import models
from django.utils import timezone
import uuid
from django.contrib.auth.models import User

# Asegúrate de que Avion, Pasajero estén como los últimos que te di

class Avion(models.Model):
    modelo = models.CharField(max_length=100)
    matricula = models.CharField(max_length=20, unique=True)
    capacidad_asientos = models.IntegerField()

    def __str__(self):
        return f"{self.modelo} ({self.matricula})"
    
    

class Vuelo(models.Model):
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha_salida = models.DateField()
    hora_salida = models.TimeField()
    duracion_minutos = models.IntegerField(help_text="Duración estimada del vuelo en minutos.")
    avion = models.ForeignKey(Avion, on_delete=models.PROTECT, related_name='vuelos',
                              help_text="Avión asignado a este vuelo. No se podrá eliminar el avión si tiene vuelos asignados.")

    class Meta:
        ordering = ['fecha_salida', 'hora_salida']

    def __str__(self):
        return f"Vuelo de {self.origen} a {self.destino} el {self.fecha_salida} a las {self.hora_salida}"

    def get_asientos_disponibles(self):
        # Filtra los asientos asociados a este vuelo que están disponibles
        return self.asientos.filter(esta_disponible=True)

    def get_asientos_ocupados(self):
        # Filtra los asientos asociados a este vuelo que están ocupados
        return self.asientos.filter(esta_disponible=False)

    def get_asientos_totales(self):
        # Devuelve el número total de asientos basado en la capacidad del avión asignado
        if self.avion:
            return self.avion.capacidad_asientos
        return 0

class Asiento(models.Model):
    vuelo = models.ForeignKey(Vuelo, on_delete=models.CASCADE, related_name='asientos')
    numero_asiento = models.CharField(max_length=5) # Ej: '1A', '23C'
    esta_disponible = models.BooleanField(default=True)

    class Meta:
        unique_together = ('vuelo', 'numero_asiento')
        ordering = ['numero_asiento']

    def __str__(self):
        return f"Asiento {self.numero_asiento} - Vuelo {self.vuelo.id}"

class Pasajero(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    documento = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.documento})"

class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('RESERVADO', 'Reservado'),
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
        ('CHECKED_IN', 'Check-in Realizado'),
    ]
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE, related_name='reservas')
    asiento = models.OneToOneField(Asiento, on_delete=models.PROTECT)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='RESERVADO')
    codigo_boleto = models.CharField(max_length=100, unique=True, blank=True, null=True)

    class Meta:
        ordering = ['-fecha_reserva']

    def __str__(self):
        return f"Reserva {self.codigo_boleto or self.id} de {self.pasajero} para Vuelo {self.asiento.vuelo.id} - Asiento {self.asiento.numero_asiento}"

    def save(self, *args, **kwargs):
        if not self.codigo_boleto:
            self.codigo_boleto = str(uuid.uuid4())[:8].upper()

        # Actualizar la disponibilidad del asiento al guardar la reserva
        if self.estado in ['RESERVADO', 'CONFIRMADO', 'CHECKED_IN']:
            self.asiento.esta_disponible = False
        else: # Si se cancela
            self.asiento.esta_disponible = True
        self.asiento.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.asiento.esta_disponible = True
        self.asiento.save()
        super().delete(*args, **kwargs)