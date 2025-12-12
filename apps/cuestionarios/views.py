from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cuestionario, RespuestaCuestionario, RespuestaDetalle, Opcion
from .serializers import CuestionarioSerializer, RespuestaCuestionarioSerializer

class CuestionarioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Cuestionario.objects.all()
    serializer_class = CuestionarioSerializer
    
    @action(detail=False, methods=['get'], url_path='charla/(?P<charla_id>[^/.]+)')
    def por_charla(self, request, charla_id=None):
        try:
            cuestionario = Cuestionario.objects.get(charla_id=charla_id)
            serializer = self.get_serializer(cuestionario)
            return Response(serializer.data)
        except Cuestionario.DoesNotExist:
            return Response({'error': 'No hay cuestionario para esta charla'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def responder(self, request, pk=None):
        cuestionario = self.get_object()
        respuestas = request.data.get('respuestas', [])  # [{pregunta_id, opcion_id}]
        
        # Calcular puntaje
        total_preguntas = cuestionario.preguntas.count()
        correctas = 0
        
        # Contar intentos previos
        intentos_previos = RespuestaCuestionario.objects.filter(
            cuestionario=cuestionario,
            usuario=request.user
        ).count()
        
        # Crear respuesta
        respuesta_cuestionario = RespuestaCuestionario.objects.create(
            cuestionario=cuestionario,
            usuario=request.user,
            puntaje=0,
            intento=intentos_previos + 1
        )
        
        # Procesar cada respuesta
        for resp in respuestas:
            try:
                opcion = Opcion.objects.get(id=resp['opcion_id'])
                es_correcta = opcion.es_correcta
                
                RespuestaDetalle.objects.create(
                    respuesta_cuestionario=respuesta_cuestionario,
                    pregunta_id=resp['pregunta_id'],
                    opcion_seleccionada=opcion,
                    es_correcta=es_correcta
                )
                
                if es_correcta:
                    correctas += 1
            except:
                pass
        
        # Calcular puntaje final
        puntaje = (correctas / total_preguntas * 100) if total_preguntas > 0 else 0
        aprobado = puntaje >= cuestionario.aprobacion_minima
        
        respuesta_cuestionario.puntaje = puntaje
        respuesta_cuestionario.aprobado = aprobado
        respuesta_cuestionario.save()
        
        serializer = RespuestaCuestionarioSerializer(respuesta_cuestionario)
        return Response(serializer.data)