from rest_framework import serializers
from .models import Reporte
from apps.charlas.serializers import CharlaListSerializer

class ReporteSerializer(serializers.ModelSerializer):
    charla_detalle = CharlaListSerializer(source='charla', read_only=True)
    pdf_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Reporte
        fields = ['id', 'charla', 'charla_detalle', 'pdf_file', 'url_pdf', 
                  'pdf_url', 'fecha_generado']
        read_only_fields = ['id', 'fecha_generado']
    
    def get_pdf_url(self, obj):
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
        return obj.url_pdf or None

class SubirPDFSerializer(serializers.Serializer):
    charla_id = serializers.IntegerField()
    pdf_file = serializers.FileField()
    
    def validate_pdf_file(self, value):
        if not value.name.endswith('.pdf'):
            raise serializers.ValidationError("El archivo debe ser un PDF")
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("El archivo no debe exceder 10MB")
        return value