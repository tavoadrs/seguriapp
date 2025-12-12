from rest_framework import serializers
from .models import Cuestionario, Pregunta, Opcion, RespuestaCuestionario

class OpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opcion
        fields = ['id', 'texto']  # NO incluir es_correcta

class PreguntaSerializer(serializers.ModelSerializer):
    opciones = OpcionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pregunta
        fields = ['id', 'texto', 'orden', 'opciones']

class CuestionarioSerializer(serializers.ModelSerializer):
    preguntas = PreguntaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cuestionario
        fields = ['id', 'charla', 'titulo', 'aprobacion_minima', 'preguntas']

class RespuestaCuestionarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaCuestionario
        fields = ['id', 'puntaje', 'aprobado', 'intento', 'fecha']