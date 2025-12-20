import json # <--- IMPORTANTE: Necesario para leer el JSON de preguntas
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

# Asegúrate de importar TODOS tus modelos necesarios
from .models import Cuestionario, Pregunta, Opcion, RespuestaCuestionario, RespuestaDetalle
from .serializers import CuestionarioSerializer, RespuestaCuestionarioSerializer

# CAMBIO 1: Usamos ModelViewSet en lugar de ReadOnlyModelViewSet
class CuestionarioViewSet(viewsets.ModelViewSet):
    queryset = Cuestionario.objects.all()
    serializer_class = CuestionarioSerializer
    
    # CAMBIO 2: Sobrescribimos el método 'create' para manejar las preguntas
    def create(self, request, *args, **kwargs):
        # 1. Validar los datos básicos (Charla, Título, Aprobación)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # 2. Guardar el Cuestionario (Padre)
            cuestionario = serializer.save()
            
            # 3. Procesar las Preguntas (que vienen como string JSON desde el FormData)
            preguntas_json = request.data.get('preguntas')
            
            if preguntas_json:
                # Convertir el string "[{...}]" a una lista real de Python
                preguntas_data = json.loads(preguntas_json)
                
                for preg in preguntas_data:
                    # Crear la Pregunta
                    nueva_pregunta = Pregunta.objects.create(
                        cuestionario=cuestionario,
                        texto=preg['texto']
                    )
                    
                    # Crear las Opciones de esa pregunta
                    for op in preg['opciones']:
                        Opcion.objects.create(
                            pregunta=nueva_pregunta,
                            texto=op['texto'],
                            es_correcta=op['es_correcta']
                        )

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Exception as e:
            # Si algo falla, borramos el cuestionario para no dejar basura y avisamos
            if 'cuestionario' in locals():
                cuestionario.delete()
            return Response(
                {'detail': f'Error al guardar preguntas: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # --- TUS MÉTODOS EXISTENTES (Sin cambios) ---
    
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
        respuestas = request.data.get('respuestas', [])
        
        total_preguntas = cuestionario.preguntas.count()
        correctas = 0
        
        intentos_previos = RespuestaCuestionario.objects.filter(
            cuestionario=cuestionario,
            usuario=request.user
        ).count()
        
        respuesta_cuestionario = RespuestaCuestionario.objects.create(
            cuestionario=cuestionario,
            usuario=request.user,
            puntaje=0,
            intento=intentos_previos + 1
        )
        
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
        
        puntaje = (correctas / total_preguntas * 100) if total_preguntas > 0 else 0
        aprobado = puntaje >= cuestionario.aprobacion_minima
        
        respuesta_cuestionario.puntaje = puntaje
        respuesta_cuestionario.aprobado = aprobado
        respuesta_cuestionario.save()
        
        serializer = RespuestaCuestionarioSerializer(respuesta_cuestionario)
        return Response(serializer.data)