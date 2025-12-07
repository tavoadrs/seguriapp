from rest_framework import serializers
from .models import ControlAcceso
from apps.users.serializers import UsuarioPerfilSerializer

class ControlAccesoSerializer(serializers.ModelSerializer):
    usuario_detalle = UsuarioPerfilSerializer(source='usuario', read_only=True)
    duracion_minutos = serializers.SerializerMethodField()
    
    class Meta:
        model = ControlAcceso
        fields = ['id', 'usuario', 'usuario_detalle', 'hora_entrada', 
                  'hora_salida', 'duracion_minutos']
        read_only_fields = ['id', 'hora_entrada']
    
    def get_duracion_minutos(self, obj):
        if obj.hora_salida:
            delta = obj.hora_salida - obj.hora_entrada
            return int(delta.total_seconds() / 60)
        return None