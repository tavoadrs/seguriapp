from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError
from .models import Asistencia
from .serializers import AsistenciaSerializer, FirmarAsistenciaSerializer
from apps.charlas.models import Charla
from apps.users.permissions import IsAdmin, IsSupervisor
from .services import FirebaseStorageService

class AsistenciaViewSet(viewsets.ModelViewSet):
    queryset = Asistencia.objects.select_related('usuario', 'charla').all()
    serializer_class = AsistenciaSerializer
    
    def get_permissions(self):
        if self.action in ['destroy']:
            return [IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        user = self.request.user
        if user.is_trabajador:
            return Asistencia.objects.filter(usuario=user)
        elif user.is_supervisor:
            return Asistencia.objects.filter(charla__supervisor=user)
        return Asistencia.objects.all()
    
    @action(detail=False, methods=['post'])
    def firmar(self, request):
        serializer = FirmarAsistenciaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        charla_id = serializer.validated_data['charla_id']
        firma_data = serializer.validated_data['firma_data']
        
        try:
            charla = Charla.objects.get(id=charla_id)
        except Charla.DoesNotExist:
            return Response({'error': 'Charla no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar que el usuario sea trabajador
        if not request.user.is_trabajador:
            return Response({'error': 'Solo trabajadores pueden firmar'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # Guardar firma en Firebase y obtener hash
        storage_service = FirebaseStorageService()
        firma_hash = storage_service.save_signature(
            user_id=request.user.id,
            charla_id=charla_id,
            signature_data=firma_data
        )
        
        try:
            asistencia = Asistencia.objects.create(
                usuario=request.user,
                charla=charla,
                firma_hash=firma_hash
            )
            serializer = AsistenciaSerializer(asistencia)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({'error': 'Ya has firmado asistencia a esta charla'}, 
                          status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def mis_asistencias(self, request):
        asistencias = Asistencia.objects.filter(usuario=request.user)
        serializer = AsistenciaSerializer(asistencias, many=True)
        return Response(serializer.data)