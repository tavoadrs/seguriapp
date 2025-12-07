from django.db import models
from django.conf import settings

class ControlAcceso(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='accesos'
    )
    hora_entrada = models.DateTimeField(auto_now_add=True)
    hora_salida = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Control de Acceso'
        verbose_name_plural = 'Controles de Acceso'
        ordering = ['-hora_entrada']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.hora_entrada}"