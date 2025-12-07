from rest_framework import serializers
from .models import Charla
from apps.users.serializers import UsuarioPerfilSerializer

class CharlaSerializer(serializers.ModelSerializer):
    supervisor_detalle = UsuarioPerfilSerializer(source='supervisor', read_only=True)
    
    class Meta:
        model = Charla
        fields = ['id', 'tema', 'fecha', 'hora', 'supervisor', 'supervisor_detalle', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate_supervisor(self, value):
        if value.rol not in ['ADMIN', 'SUPERVISOR']:
            raise serializers.ValidationError("El supervisor debe tener rol ADMIN o SUPERVISOR")
        return value

class CharlaListSerializer(serializers.ModelSerializer):
    supervisor_nombre = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    
    class Meta:
        model = Charla
        fields = ['id', 'tema', 'fecha', 'hora', 'supervisor_nombre', 'created_at']