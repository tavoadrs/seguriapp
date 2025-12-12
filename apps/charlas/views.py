from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Charla
from .serializers import CharlaSerializer, CharlaListSerializer
from users.permissions import IsAdmin, IsSupervisor
from django.http import HttpResponse
import qrcode
from io import BytesIO

class CharlaViewSet(viewsets.ModelViewSet):
    queryset = Charla.objects.select_related('supervisor').all()
    serializer_class = CharlaSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CharlaListSerializer
        return CharlaSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsSupervisor()]
        elif self.action == 'destroy':
            return [IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_trabajador:
            # Trabajadores ven TODAS las charlas disponibles, no solo donde asistieron
            return Charla.objects.all().order_by('-fecha', '-hora')
        return Charla.objects.all()
    
    @action(detail=True, methods=['get'])
    def asistentes(self, request, pk=None):
        charla = self.get_object()
        from asistencias.serializers import AsistenciaSerializer
        asistencias = charla.asistencias.select_related('usuario').all()
        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data)
    
    def qr_code(self, request, pk=None):
        charla = self.get_object()
        qr_data = f"charla_seguridad://charla/{charla.id}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return HttpResponse(buffer, content_type='image/png')