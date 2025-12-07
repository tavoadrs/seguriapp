from django.db import models
from apps.charlas.models import Charla

class Reporte(models.Model):
    charla = models.OneToOneField(
        Charla,
        on_delete=models.CASCADE,
        related_name='reporte'
    )
    pdf_file = models.FileField(upload_to='reportes/', null=True, blank=True)
    url_pdf = models.URLField(max_length=500, blank=True)
    fecha_generado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-fecha_generado']
    
    def __str__(self):
        return f"Reporte - {self.charla.tema}"