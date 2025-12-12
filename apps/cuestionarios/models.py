from django.db import models
from django.conf import settings
from apps.charlas.models import Charla

class Cuestionario(models.Model):
    charla = models.OneToOneField(
        Charla,
        on_delete=models.CASCADE,
        related_name='cuestionario'
    )
    titulo = models.CharField(max_length=255)
    aprobacion_minima = models.IntegerField(default=70, help_text='Porcentaje mínimo para aprobar')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cuestionario'
        verbose_name_plural = 'Cuestionarios'
    
    def __str__(self):
        return f"Cuestionario - {self.charla.tema}"

class Pregunta(models.Model):
    cuestionario = models.ForeignKey(
        Cuestionario,
        on_delete=models.CASCADE,
        related_name='preguntas'
    )
    texto = models.TextField()
    orden = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'
        ordering = ['orden']
    
    def __str__(self):
        return f"{self.orden}. {self.texto[:50]}"

class Opcion(models.Model):
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='opciones'
    )
    texto = models.CharField(max_length=255)
    es_correcta = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Opción'
        verbose_name_plural = 'Opciones'
    
    def __str__(self):
        return self.texto

class RespuestaCuestionario(models.Model):
    cuestionario = models.ForeignKey(
        Cuestionario,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='respuestas_cuestionarios'
    )
    puntaje = models.DecimalField(max_digits=5, decimal_places=2)
    aprobado = models.BooleanField(default=False)
    intento = models.IntegerField(default=1)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Respuesta Cuestionario'
        verbose_name_plural = 'Respuestas Cuestionarios'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.puntaje}% (Intento {self.intento})"

class RespuestaDetalle(models.Model):
    respuesta_cuestionario = models.ForeignKey(
        RespuestaCuestionario,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    opcion_seleccionada = models.ForeignKey(Opcion, on_delete=models.CASCADE)
    es_correcta = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Respuesta Detalle'
        verbose_name_plural = 'Respuestas Detalle'