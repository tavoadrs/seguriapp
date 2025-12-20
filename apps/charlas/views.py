from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.charlas.models import Charla
from apps.charlas.serializers import CharlaSerializer, CharlaListSerializer
from users.permissions import IsAdmin, IsSupervisor
from apps.asistencias.serializers import AsistenciaSerializer
from django.shortcuts import render, get_object_or_404

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
    
    def firmar_charla(request,charla_id):
        #vista HTML para que el trabajador vea el material, responda cuestionario
        charla = get_object_or_404(Charla, id=charla_id)
        return render(request, 'charlas/firmar_charla.html',{'charla':charla})

    
    def get_queryset(self):
        user = self.request.user
        if user.is_trabajador:
            # Trabajadores ven TODAS las charlas disponibles, no solo donde asistieron
            return Charla.objects.all().order_by('-fecha', '-hora')
        return Charla.objects.all()
    
    @action(detail=True, methods=['get'])
    def asistentes(self, request, pk=None):
        charla = self.get_object()
        asistencias = charla.asistencias.select_related('usuario').all()
        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def confirmar_asistencia(self, request, pk=None):
        charla = self.get_object()
        usuario = request.user
        
        # Opción A: Si tienes un campo ManyToMany 'asistentes' en Charla
        if usuario not in charla.asistentes.all():
            charla.asistentes.add(usuario)
            return Response({'status': 'Asistencia confirmada'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'Ya estabas registrado'}, status=status.HTTP_200_OK)
            
        # Opción B: Si tienes un modelo intermedio 'AsistenciaCharla'
        # AsistenciaCharla.objects.get_or_create(charla=charla, usuario=usuario)
        # return Response({'status': 'Confirmado'})
