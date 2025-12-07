from django.db import models
from django.conf import settings

class Charla(models.Model):
    tema = models.CharField(max_length=255)
    fecha = models.DateField()
    hora = models.TimeField()
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='charlas_supervisadas',
        limit_choices_to={'rol__in': ['ADMIN', 'SUPERVISOR']}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Charla'
        verbose_name_plural = 'Charlas'
        ordering = ['-fecha', '-hora']
    
    def __str__(self):
        return f"{self.tema} - {self.fecha} {self.hora}"