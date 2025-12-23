from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
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

    # FUSIÓN DE PERMISOS: Un solo método para todos los casos
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            return [IsSupervisor()]
        elif self.action == 'destroy':
            # Permitimos la entrada para evaluar la lógica en perform_destroy
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated()]

    # LÓGICA DE ELIMINACIÓN: Supervisor borra lo suyo, Admin todo
    def perform_destroy(self, instance):
        user = self.request.user
        if user.rol == 'ADMIN' or (user.rol == 'SUPERVISOR' and instance.supervisor == user):
            instance.delete()
        else:
            raise PermissionDenied("No tienes permiso para eliminar esta charla.")

    # FUSIÓN DE FILTRADO: Lógica para Trabajador y Supervisor
    def get_queryset(self):
        user = self.request.user
        
        # Si no está autenticado (evita errores en carga inicial)
        if not user.is_authenticated:
            return Charla.objects.none()

        if user.rol == 'TRABAJADOR':
            # 1. Solo de su supervisor asignado
            # 2. Solo si están en estado ENVIADA
            # 3. Excluir las que YA firmó (asistencias)
            return Charla.objects.filter(
                supervisor=user.supervisor,
                estado='ENVIADA'
            ).exclude(asistencias__usuario=user).order_by('-fecha', '-hora')
        
        if user.rol == 'SUPERVISOR':
            # El supervisor ve su repertorio (borradores) y enviadas
            return Charla.objects.filter(supervisor=user).order_by('-fecha', '-hora')

        # Admin ve todo
        return Charla.objects.all().order_by('-fecha', '-hora')
    
    # --- Acciones adicionales ---
    
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
        # Se asume que el modelo Asistencia tiene una relación con Charla y Usuario
        from apps.asistencias.models import Asistencia
        Asistencia.objects.get_or_create(charla=charla, usuario=usuario)
        return Response({'status': 'Asistencia confirmada'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def republicar(self,request,pk=None):
        charla = self.get_object()

        # 1. Borramos las asistencias previas para que los trabajadores asignados vean la chala como "No firmada"
        charla.asistencias.all().delete()

        # cambiamos el estado a ENVIADA
        charla.estado = 'ENVIADA'
        charla.save()
        return Response({'status': 'Charla republicada con éxito'}, status=status.HTTP_200_OK)

def firmar_charla(request, charla_id):
    charla = get_object_or_404(Charla, id=charla_id)
    return render(request, 'charlas/firmar_charla.html', {'charla': charla})