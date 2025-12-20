from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ControlAcceso
from .serializers import ControlAccesoSerializer
from users.permissions import IsAdmin
from django.db.models import Q

class ControlAccesoViewSet(viewsets.ModelViewSet):
    queryset = ControlAcceso.objects.select_related('usuario').all()
    serializer_class = ControlAccesoSerializer
    
    def get_permissions(self):
        if self.action in ['destroy', 'update', 'partial_update']:
            return [IsAdmin()]
        return super().get_permissions()
    
    def get_queryset(self):
        # 1. Aplicar filtro base de permisos (trabajador solo ve sus accesos)
        user = self.request.user
        queryset = ControlAcceso.objects.select_related('usuario').all()
        
        if user.is_trabajador:
            queryset = queryset.filter(usuario=user)
        
        # 2. Obtener parámetros de consulta
        params = self.request.query_params


        
        # --- LÓGICA DE FILTROS ---
        
        # A. FILTRO POR NOMBRE/RUT (search)
        search_term = params.get('search')
        if search_term:
            # Usamos Q objects para buscar en múltiples campos (first_name, last_name, rut)
            queryset = queryset.filter(
                Q(usuario__first_name__icontains=search_term) |
                Q(usuario__last_name__icontains=search_term) |
                Q(usuario__rut__icontains=search_term)
            )

        # B. FILTRO POR FECHA (fecha)
        fecha_str = params.get('fecha')


        if fecha_str:
            try:
                # El Front-end envía YYYY-MM-DD
                queryset = queryset.filter(hora_entrada__date=fecha_str)

            except ValueError:
                pass# Opcional: manejar si el formato de fecha es incorrecto

        
        # C. FILTRO POR ESTADO (estado)
        estado = params.get('estado')
        if estado == 'en_sitio':
            queryset = queryset.filter(hora_salida__isnull=True)
        elif estado == 'salio':
            queryset = queryset.filter(hora_salida__isnull=False)

        return queryset.order_by('-hora_entrada') # Ordenar por hora más reciente


    # El método accesos_hoy es REDUNDANTE si usamos el filtro 'fecha' en get_queryset
    # Se recomienda que el Front-end llame a /api/accesos/?fecha=YYYY-MM-DD
    # Si quieres mantenerlo por separado, modifícalo para que también use los filtros:
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
    
# apps/accesos/views.py

# ... (resto de imports y la clase ControlAccesoViewSet) ...

    @action(detail=False, methods=['get'])
    def accesos_hoy(self, request):
        """Obtiene los accesos del día actual con formato paginado."""
        
        # Usamos localdate para obtener la fecha de hoy en la zona horaria de Django
        hoy = timezone.localdate()
        
        # 1. Obtiene el queryset base filtrado por permisos, y luego aplica el filtro de fecha
        #    IMPORTANTE: get_queryset ya aplica el filtro de Trabajador.
        queryset = self.get_queryset().filter(hora_entrada__date=hoy)
        
        # 2. APLICA PAGINACIÓN A LA RESPUESTA
        #    Esto transforma el queryset en una página de resultados con metadatos (count, next, previous)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Devuelve la respuesta paginada con la estructura {count: X, results: [...]}
            return self.get_paginated_response(serializer.data)
        
        # 3. Caso de fallback (si la paginación no está activa, aunque debería estarlo)
        serializer = ControlAccesoSerializer(queryset, many=True)
        return Response(serializer.data)