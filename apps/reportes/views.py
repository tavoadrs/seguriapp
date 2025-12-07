from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse
from .models import Reporte
from .serializers import ReporteSerializer, SubirPDFSerializer
from apps.charlas.models import Charla
from apps.users.permissions import IsAdmin, IsSupervisor
from .services import PDFGeneratorService

class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.select_related('charla').all()
    serializer_class = ReporteSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'generar_pdf', 'subir_pdf']:
            return [IsSupervisor()]
        elif self.action == 'destroy':
            return [IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_supervisor:
            return Reporte.objects.filter(charla__supervisor=user)
        return Reporte.objects.all()
    
    @action(detail=False, methods=['post'])
    def generar_pdf(self, request):
        """Genera automáticamente un PDF para una charla"""
        charla_id = request.data.get('charla_id')
        
        if not charla_id:
            return Response({'error': 'charla_id requerido'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            charla = Charla.objects.get(id=charla_id)
        except Charla.DoesNotExist:
            return Response({'error': 'Charla no encontrada'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Verificar permisos
        if request.user.is_supervisor and charla.supervisor != request.user:
            return Response({'error': 'No tienes permiso para generar el reporte de esta charla'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Generar PDF
        pdf_service = PDFGeneratorService()
        pdf_path = pdf_service.generate_charla_report(charla)
        
        # Crear o actualizar reporte
        reporte, created = Reporte.objects.update_or_create(
            charla=charla,
            defaults={'url_pdf': pdf_path}
        )
        
        serializer = ReporteSerializer(reporte, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def subir_pdf(self, request):
        """Permite a supervisores subir PDFs manualmente"""
        serializer = SubirPDFSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        charla_id = serializer.validated_data['charla_id']
        pdf_file = serializer.validated_data['pdf_file']
        
        try:
            charla = Charla.objects.get(id=charla_id)
        except Charla.DoesNotExist:
            return Response({'error': 'Charla no encontrada'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Verificar permisos
        if request.user.is_supervisor and charla.supervisor != request.user:
            return Response({'error': 'No tienes permiso para subir reportes de esta charla'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Crear o actualizar reporte
        reporte, created = Reporte.objects.update_or_create(
            charla=charla,
            defaults={'pdf_file': pdf_file}
        )
        
        serializer = ReporteSerializer(reporte, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def descargar(self, request, pk=None):
        """Descarga el PDF del reporte"""
        reporte = self.get_object()
        
        if reporte.pdf_file:
            return FileResponse(
                reporte.pdf_file.open('rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=f'reporte_{reporte.charla.id}.pdf'
            )
        
        return Response({'error': 'PDF no disponible'}, 
                       status=status.HTTP_404_NOT_FOUND)