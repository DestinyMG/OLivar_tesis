from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import PreRegistro
from .serializers import PreRegistroSerializer
from rest_framework.exceptions import ValidationError

class PreRegistroViewSet(viewsets.ModelViewSet):
    queryset = PreRegistro.objects.all().order_by('-fecha_creacion')
    serializer_class = PreRegistroSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            # Esto ejecutará las validaciones de ci, username y el nuevo email
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(
                {
                    "message": "Solicitud de registro enviada con éxito.",
                    "data": serializer.data
                }, 
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        except ValidationError as e:
            # Centralizamos la respuesta de errores para el frontend
            return Response(
                {
                    "error": "Error de validación",
                    "details": e.detail
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

    # Opcional: Si quieres que al listar los veas del más reciente al más antiguo
    def get_queryset(self):
        return PreRegistro.objects.all().order_by('-fecha_creacion')