from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Charla
from .serializers import CharlaSerializer, CharlaListSerializer
from apps.users.permissions import IsAdmin, IsSupervisor

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
            # Trabajadores solo ven charlas donde asistieron
            return Charla.objects.filter(asistencias__usuario=user).distinct()
        return Charla.objects.all()
    
    @action(detail=True, methods=['get'])
    def asistentes(self, request, pk=None):
        charla = self.get_object()
        from asistencias.serializers import AsistenciaSerializer
        asistencias = charla.asistencias.select_related('usuario').all()
        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data)