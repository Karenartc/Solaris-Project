from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
import datetime


class User(AbstractUser):
    # Opciones para el campo 'role' de usuario
    ROLES_CHOICES = [
        ('Propietario de vivienda', 'Propietario de vivienda'),
        ('Miembro de la comunidad', 'Miembro de la comunidad'),
        ('Administrador', 'Administrador'),
        ('Inversor', 'Inversor'),
        ('Usuario preocupado por el medio ambiente', 'Usuario preocupado por el medio ambiente'),
    ]
    rut = models.CharField(max_length=15, blank=True, unique=True)
    role = models.CharField(max_length=50, choices=ROLES_CHOICES)
    gender = models.CharField(max_length=10, blank=True)
    age = models.IntegerField(blank=True, null=True, default=0)
    address = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.get_full_name() if self.get_full_name() else self.username

    class Meta:
        verbose_name = _('user') # Nombre en singular del modelo
        verbose_name_plural = _('users') # Nombre en plural del modelo

    # Relaciones ManyToMany y ManyToOne para grupos y permisos de usuario
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_groups',  # Nombre de relación inversa
        related_query_name='user',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_permissions', # Nombre de relación inversa
        help_text=_('Specific permissions for this user.'), # Ayuda para el campo
    )

class EnergyProduction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Usuario asociado a la producción de energía
    power_generated = models.FloatField(null=True)  # Potencia generada (W)
    accumulated_energy = models.FloatField(null=True)  # Energía acumulada (kWh)
    efficiency = models.FloatField(null=True)  # Eficiencia del sistema (%)
    timestamp = models.DateTimeField(auto_now_add=True) # Fecha y hora de creación

    def __str__(self):
        return f"{self.user} - {self.timestamp}"

class EnergyConsumption(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuario asociado al consumo de energía
    amount = models.FloatField() # Cantidad de energía consumida
    timestamp = models.DateTimeField(auto_now_add=True) # Fecha y hora de creación

class MaintenanceAlert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Usuario asociado a la alerta de mantenimiento
    title = models.CharField(max_length=100, default='Maintenance Alert') # Título de la alerta
    message = models.TextField() # Mensaje de la alerta
    timestamp = models.DateTimeField(auto_now_add=True) # Fecha y hora de creación
    energy_production = models.ForeignKey('EnergyProduction', on_delete=models.CASCADE, null=True, blank=True) # Producción de energía asociada, opcional

    def __str__(self):
        return f'{self.title} - {self.timestamp}'

class Community(models.Model):
    name = models.CharField(max_length=100) # Nombre de la comunidad

class CommunityMember(models.Model): 
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Usuario asociado a la membresía
    community = models.ForeignKey(Community, on_delete=models.CASCADE)  # Comunidad asociada

class CommunityEnergyTransaction(models.Model):
    from_user = models.ForeignKey(User, related_name='from_user', on_delete=models.CASCADE) # Usuario que realiza la transacción
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE) # Usuario receptor de la transacción
    amount = models.FloatField() # Cantidad de energía transaccionada
    timestamp = models.DateTimeField(auto_now_add=True) # Fecha y hora de creación

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Usuario asociado al código de reseteo
    code = models.CharField(max_length=5, unique=True) # Código único para reseteo de contraseña
    created_at = models.DateTimeField(auto_now_add=True) # Fecha y hora de creación

    def is_valid(self):
        return timezone.now() < self.created_at + datetime.timedelta(minutes=10) # Comprueba si el código sigue siendo válido