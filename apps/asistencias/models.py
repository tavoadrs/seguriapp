from django.db import models
from django.conf import settings
from apps.charlas.models import Charla

class Asistencia(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='asistencias',
        limit_choices_to={'rol': 'TRABAJADOR'}
    )
    charla = models.ForeignKey(
        Charla,
        on_delete=models.CASCADE,
        related_name='asistencias'
    )
    hora_firma = models.DateTimeField(auto_now_add=True)
    firma_hash = models.CharField(max_length=255)
    
    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ['usuario', 'charla']
        ordering = ['-hora_firma']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.charla.tema}"