from rest_framework import serializers
from .models import Asistencia
from users.serializers import UsuarioPerfilSerializer
from apps.charlas.serializers import CharlaListSerializer

class AsistenciaSerializer(serializers.ModelSerializer):
    usuario_detalle = UsuarioPerfilSerializer(source='usuario', read_only=True)
    charla_detalle = CharlaListSerializer(source='charla', read_only=True)
    
    class Meta:
        model = Asistencia
        fields = ['id', 'usuario', 'charla', 'hora_firma', 'firma_hash', 
                  'usuario_detalle', 'charla_detalle']
        read_only_fields = ['id', 'hora_firma', 'firma_hash']

class FirmarAsistenciaSerializer(serializers.Serializer):
    charla_id = serializers.IntegerField()
    firma_data = serializers.CharField()  # Base64 o datos de la firma
    
    def validate_charla_id(self, value):
        from charlas.models import Charla
        if not Charla.objects.filter(id=value).exists():
            raise serializers.ValidationError("La charla no existe")
        return value