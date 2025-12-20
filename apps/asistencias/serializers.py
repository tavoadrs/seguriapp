from rest_framework import serializers
from apps.asistencias.models import Asistencia
from users.serializers import UsuarioPerfilSerializer
from apps.charlas.serializers import CharlaListSerializer
from django.core.validators import RegexValidator 

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
    # CAMBIO 1: Reemplazar firma_data por rut_pin
    rut_pin = serializers.CharField(
        max_length=4, 
        min_length=4,
        # Opcional: puedes usar un validador Regex para asegurar que son solo dígitos
        
    )
    
    def validate_charla_id(self, value):
        from apps.charlas.models import Charla
        if not Charla.objects.filter(id=value).exists():
            raise serializers.ValidationError("La charla no existe")
        return value
        
    # CAMBIO 2: Añadir la validación de la lógica de negocio (PIN vs. RUT)
    def validate(self, data):
        """
        Realiza la validación cruzada del rut_pin contra el RUT del usuario actual.
        Nota: Esto requiere que la View pase el objeto 'request' al Serializer al instanciarlo 
        (ej: serializer = FirmarAsistenciaSerializer(data=request.data, context={'request': request}))
        """
        request = self.context.get('request')
        
        if not request:
            # Esto es un error de configuración si se llama desde la API
            raise serializers.ValidationError("Falta el objeto request en el contexto del Serializer.")
            
        trabajador = request.user
        rut_pin_ingresado = data['rut_pin']
        
        # --- Lógica de cálculo del PIN correcto ---
        
        # 1. Obtener el RUT del usuario (asumo que está en un campo llamado 'rut')
        rut_completo = getattr(trabajador, 'rut', None) 

        if not rut_completo:
            raise serializers.ValidationError({"rut_pin": "No se puede verificar el RUT del usuario."})
        
        try:
            # 2. Limpiar el RUT (quitar puntos y guión) y obtener los últimos 4 dígitos
            # Ejemplo: "12.345.678-9" -> "12345678" -> "5678"
            rut_sin_puntos_guion = rut_completo.replace('.', '').split('-')[0]
            codigo_correcto = rut_sin_puntos_guion[-4:]
            
        except (IndexError, AttributeError):
            raise serializers.ValidationError({"rut_pin": "El formato de RUT almacenado es inválido."})

        # 3. Comparación Final
        if rut_pin_ingresado != codigo_correcto:
            # Mensaje de error específico para el cliente
            raise serializers.ValidationError({"rut_pin": "El código PIN ingresado no coincide con los últimos 4 dígitos de tu RUT."})
            
        # Si todo es correcto, devuelve los datos
        return data