from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ControlAcceso
from .serializers import ControlAccesoSerializer
from users.permissions import IsAdmin

class ControlAccesoViewSet(viewsets.ModelViewSet):
    queryset = ControlAcceso.objects.select_related('usuario').all()
    serializer_class = ControlAccesoSerializer
    
    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_trabajador:
            return ControlAcceso.objects.filter(usuario=user)
        return ControlAcceso.objects.all()
    
    @action(detail=False, methods=['post'])
    def registrar_entrada(self, request):
        """Registra la entrada de un trabajador"""
        # Verificar si ya tiene una entrada sin salida
        entrada_abierta = ControlAcceso.objects.filter(
            usuario=request.user,
            hora_salida__isnull=True
        ).first()
        
        if entrada_abierta:
            return Response({
                'error': 'Ya tienes una entrada registrada sin salida',
                'entrada': ControlAccesoSerializer(entrada_abierta).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        acceso = ControlAcceso.objects.create(usuario=request.user)
        serializer = ControlAccesoSerializer(acceso)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def registrar_salida(self, request):
        """Registra la salida de un trabajador"""
        # Buscar la última entrada sin salida
        entrada_abierta = ControlAcceso.objects.filter(
            usuario=request.user,
            hora_salida__isnull=True
        ).order_by('-hora_entrada').first()
        
        if not entrada_abierta:
            return Response({
                'error': 'No tienes una entrada registrada para marcar salida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        entrada_abierta.hora_salida = timezone.now()
        entrada_abierta.save()
        
        serializer = ControlAccesoSerializer(entrada_abierta)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mis_accesos(self, request):
        """Obtiene los accesos del usuario actual"""
        accesos = ControlAcceso.objects.filter(usuario=request.user)
        serializer = ControlAccesoSerializer(accesos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def accesos_hoy(self, request):
        """Obtiene los accesos del día actual"""
        from django.utils import timezone
        hoy = timezone.now().date()
        
        queryset = self.get_queryset().filter(hora_entrada__date=hoy)
        serializer = ControlAccesoSerializer(queryset, many=True)
        return Response(serializer.data)