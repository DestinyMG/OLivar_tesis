from rest_framework import viewsets
from .models import Incidencia, IncidenciaImagen, Mensaje, MensajeImagen
from .serializers import (
    IncidenciaSerializer,
    IncidenciaImagenSerializer,
    MensajeSerializer,
    MensajeImagenSerializer
)
from rest_framework.permissions import AllowAny
class IncidenciaViewSet(viewsets.ModelViewSet):
    queryset = Incidencia.objects.all().select_related('persona')
    serializer_class = IncidenciaSerializer
    permission_classes = [AllowAny] 

class IncidenciaImagenViewSet(viewsets.ModelViewSet):
    queryset = IncidenciaImagen.objects.all().select_related('incidencia')
    serializer_class = IncidenciaImagenSerializer
    permission_classes = [AllowAny] 

class MensajeViewSet(viewsets.ModelViewSet):
    queryset = Mensaje.objects.all().select_related('incidencia')
    serializer_class = MensajeSerializer
    permission_classes = [AllowAny] 

class MensajeImagenViewSet(viewsets.ModelViewSet):
    queryset = MensajeImagen.objects.all().select_related('mensaje')
    serializer_class = MensajeImagenSerializer
    permission_classes = [AllowAny] 


