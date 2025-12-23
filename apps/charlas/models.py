from django.db import models
from django.conf import settings

class Charla(models.Model):

    ESTADOS = (
        ('BORRADOR', 'En Repertorio'),
        ('ENVIADA', 'Enviada'),
    )
    
    tema = models.CharField(max_length=255)
    fecha = models.DateField()
    hora = models.TimeField()
    supervisor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='charlas_supervisadas',
        limit_choices_to={'rol__in': ['ADMIN', 'SUPERVISOR']}
    )
    #campo para archivos adjuntos
    archivo_adjunto = models.FileField(
    upload_to='media/charlas',
    null=True,
    blank=True,
    help_text='Archivo adjunto (PDF, DOCX, PPT)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='BORRADOR'
    )

    #cödigo para saber quien ha firmado la charla
    firmas = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='asistencias.Asistencia', # Usa tu modelo de asistencias existente
        related_name='charlas_firmadas',
        blank=True
    )

    class Meta:
        verbose_name = 'Charla'
        verbose_name_plural = 'Charlas'
        ordering = ['-fecha', '-hora']
    
    def __str__(self):
        return f"{self.tema} - {self.fecha} {self.hora}"
    @property
    def tiene_archivo(self):
        return bool(self.archivo_adjunto)
