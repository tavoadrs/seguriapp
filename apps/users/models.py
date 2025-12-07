from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('SUPERVISOR', 'Supervisor'),
        ('TRABAJADOR', 'Trabajador'),
    )
    
    rut = models.CharField(max_length=12, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='TRABAJADOR')
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.rut})"
    
    @property
    def is_admin(self):
        return self.rol == 'ADMIN'
    
    @property
    def is_supervisor(self):
        return self.rol == 'SUPERVISOR'
    
    @property
    def is_trabajador(self):
        return self.rol == 'TRABAJADOR'