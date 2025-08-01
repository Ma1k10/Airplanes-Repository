from django.db import models
from django.contrib.auth.models import User

class Avion(models.Model):
    modelo = models.CharField(max_length=100)
    capacidad = models.CharField(max_length=100)
    fabricante = models.CharField(max_length=100)
    anio_fabricacion = models.PositiveIntegerField(default=2020)
    

    def __str__(self):
        return f"{self.modelo} ({self.fabricante})"

class Vuelo(models.Model):
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    fecha = models.DateField()
    hora = models.TimeField()
    duracion = models.DurationField()

    def __str__(self):
        return f"{self.origen} → {self.destino} ({self.fecha})"

class Asiento(models.Model):
    avion = models.ForeignKey(Avion, on_delete=models.CASCADE, related_name='asientos')
    fila = models.IntegerField()
    columna = models.CharField(max_length=1)

    class Meta:
        unique_together = ('avion', 'fila', 'columna')

    def __str__(self):
        return f"Asiento {self.fila}{self.columna} en {self.avion.modelo}"

class Pasajero(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    dni = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.usuario.get_full_name()} ({self.dni})"

class Reserva(models.Model):
    pasajero = models.ForeignKey(Pasajero, on_delete=models.CASCADE)
    asiento = models.ForeignKey(Asiento, on_delete=models.CASCADE)
    fecha_reserva = models.DateTimeField(auto_now_add=True)
    confirmada = models.BooleanField(default=False)

    class Meta:
        unique_together = ('pasajero', 'asiento')   

    def __str__(self):
        return f"Reserva de {self.pasajero.usuario.username} - Asiento {self.asiento}"

class Boleto(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=10, unique=True)
    emitido_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Boleto {self.codigo} - {self.reserva.pasajero.usuario.username}"
