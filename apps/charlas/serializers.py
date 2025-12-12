from rest_framework import serializers
from .models import Charla
from users.serializers import UsuarioPerfilSerializer

class CharlaSerializer(serializers.ModelSerializer):
    supervisor_detalle = UsuarioPerfilSerializer(source='supervisor', read_only=True)
    archivo_url = serializers.SerializerMethodField()
    tiene_archivo = serializers.ReadOnlyField()
    
    class Meta:
        model = Charla
        fields = ['id', 'tema', 'fecha', 'hora', 'supervisor', 'supervisor_detalle', 
                  'archivo_adjunto', 'archivo_url', 'tiene_archivo', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_archivo_url(self, obj):
        if obj.archivo_adjunto:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo_adjunto.url)
        return None
    
    def validate_supervisor(self, value):
        if value.rol not in ['ADMIN', 'SUPERVISOR']:
            raise serializers.ValidationError("El supervisor debe tener rol ADMIN o SUPERVISOR")
        return value
    
    def validate_archivo_adjunto(self, value):
        if value:
            # Validar extensión
            ext = value.name.split('.')[-1].lower()
            allowed = ['pdf', 'docx', 'doc', 'ppt', 'pptx']
            if ext not in allowed:
                raise serializers.ValidationError(
                    f"Formato no permitido. Solo se aceptan: {', '.join(allowed)}"
                )
            # Validar tamaño (máximo 10MB)
            if value.size > 10 * 1024 * 1024:
                raise serializers.ValidationError("El archivo no debe exceder 10MB")
        return value

class CharlaListSerializer(serializers.ModelSerializer):
    supervisor_nombre = serializers.CharField(source='supervisor.get_full_name', read_only=True)
    tiene_archivo = serializers.ReadOnlyField()
    
    class Meta:
        model = Charla
        fields = ['id', 'tema', 'fecha', 'hora', 'supervisor_nombre', 'tiene_archivo', 'created_at']