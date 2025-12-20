# apps/accesos/serializers.py

from rest_framework import serializers
from .models import ControlAcceso
from apps.users.serializers import UsuarioPerfilSerializer # ASUMIMOS que tienes un Serializer para el perfil del Usuario

class ControlAccesoSerializer(serializers.ModelSerializer):
    
    # 1. Añadir el Serializer anidado para el usuario (usando el nombre de la ForeignKey)
    usuario_detalle = UsuarioPerfilSerializer(source='usuario', read_only=True)
    
    # 2. Añadir el campo calculado de duración
    duracion_minutos = serializers.SerializerMethodField()

    class Meta:
        model = ControlAcceso
        # Asegúrate de incluir el campo 'usuario' y el campo calculado
        fields = ['id', 'usuario', 'usuario_detalle', 'hora_entrada', 'hora_salida', 'duracion_minutos']
        read_only_fields = ['id', 'hora_entrada', 'hora_salida', 'duracion_minutos']

    def get_duracion_minutos(self, obj):
        if obj.hora_salida and obj.hora_entrada:
            # Calcula la diferencia de tiempo
            delta = obj.hora_salida - obj.hora_entrada
            
            # Devuelve la duración en minutos
            return round(delta.total_seconds() / 60) 
        return None