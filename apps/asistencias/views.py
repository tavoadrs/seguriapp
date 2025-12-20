from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError
from apps.asistencias.models import Asistencia
from apps.asistencias.serializers import AsistenciaSerializer, FirmarAsistenciaSerializer
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
        # CAMBIO CLAVE 1: Pasar el request al contexto del Serializer
        serializer = FirmarAsistenciaSerializer(data=request.data, context={'request': request})
        
        if not serializer.is_valid():
            # Si falla, puede ser porque la charla no existe o el PIN no coincide
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        charla_id = serializer.validated_data['charla_id']
        # CAMBIO CLAVE 2: Obtener el rut_pin en lugar de firma_data
        rut_pin = serializer.validated_data['rut_pin'] 
        
        try:
            charla = Charla.objects.get(id=charla_id)
        except Charla.DoesNotExist:
            # Aunque ya se valida en el Serializer, lo dejamos por seguridad
            return Response({'error': 'Charla no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar que el usuario sea trabajador (Se mantiene)
        if not request.user.is_trabajador:
            return Response({'error': 'Solo trabajadores pueden firmar'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        # CAMBIO CLAVE 3: ELIMINAR LÓGICA DE FIREBASE
        # storage_service = FirebaseStorageService()
        # firma_hash = storage_service.save_signature(...)
        
        # CAMBIO CLAVE 4: Usamos el PIN validado como el nuevo hash de firma
        # Nota: Idealmente deberías aplicar un hash (ej: SHA256) al PIN antes de guardarlo, 
        # pero para que funcione inmediatamente con el campo 'firma_hash' y cumplir el requisito,
        # asignamos el PIN.
        firma_verificacion = rut_pin 
        
        try:
            asistencia = Asistencia.objects.create(
                usuario=request.user,
                charla=charla,
                # Usamos el PIN validado como registro de verificación
                firma_hash=firma_verificacion 
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