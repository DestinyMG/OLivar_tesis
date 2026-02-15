from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Incidencia, IncidenciaImagen, Mensaje, MensajeImagen
from .serializers import (
    IncidenciaSerializer,
    IncidenciaImagenSerializer,
    MensajeSerializer,
    MensajeImagenSerializer
)

class IncidenciaViewSet(viewsets.ModelViewSet):
    queryset = Incidencia.objects.all().select_related('persona__sub_programa').prefetch_related('imagenes', 'mensajes')
    serializer_class = IncidenciaSerializer
    permission_classes = [AllowAny]

    # 👇 ESTA ES LA FUNCIÓN QUE QUITA LA SEÑAL (EL "1" O PUNTO ROJO)
    @action(detail=True, methods=['post'], url_path='marcar-lectura')
    def marcar_lectura(self, request, pk=None):
        """
        Endpoint: POST /api3/incidencias/{id}/marcar-lectura/
        Cuerpo: { "rol": "JEFE_SUB_PROGRAMA" } o { "rol": "ESTUDIANTE" }
        """
        incidencia = self.get_object()
        rol = request.data.get('rol')

        if rol == 'JEFE_SUB_PROGRAMA':
            incidencia.leido_por_jefe = True
            incidencia.save()
            return Response({'status': 'Notificación jefe leída'}, status=status.HTTP_200_OK)
        
        elif rol == 'ESTUDIANTE':
            incidencia.leido_por_estudiante = True
            incidencia.save()
            return Response({'status': 'Notificación estudiante leída'}, status=status.HTTP_200_OK)
        
        return Response({'error': 'Rol no válido'}, status=status.HTTP_400_BAD_REQUEST)

class IncidenciaImagenViewSet(viewsets.ModelViewSet):
    queryset = IncidenciaImagen.objects.all().select_related('incidencia')
    serializer_class = IncidenciaImagenSerializer
    permission_classes = [AllowAny] 

class MensajeViewSet(viewsets.ModelViewSet):
    # Optimizamos con prefetch_related para cargar las imágenes de los mensajes de un solo golpe
    queryset = Mensaje.objects.all().select_related('incidencia').prefetch_related('imagenes')
    serializer_class = MensajeSerializer
    permission_classes = [AllowAny] 

class MensajeImagenViewSet(viewsets.ModelViewSet):
    queryset = MensajeImagen.objects.all().select_related('mensaje')
    serializer_class = MensajeImagenSerializer
    permission_classes = [AllowAny]