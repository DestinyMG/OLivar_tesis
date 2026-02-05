from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import PreRegistro
from .serializers import PreRegistroSerializer
from rest_framework.exceptions import ValidationError

class PreRegistroViewSet(viewsets.ModelViewSet):
    queryset = PreRegistro.objects.all()
    serializer_class = PreRegistroSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            # Valida los datos, incluyendo nuestras validaciones de ci y username
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # Devuelve los errores al frontend de forma clara
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
