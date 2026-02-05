from rest_framework import viewsets
from .models import Persona, SubPrograma
from .serializers import PersonaSerializer, SubProgramaSerializer


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import AuthSerializer

class AuthTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        persona = serializer.validated_data

        # 🔐 Token SIMPLE
        token = AccessToken()
        token['persona_id'] = persona.id
        token['rol'] = persona.rol

        return Response({
    "access": str(token),
    "usuario": {
        "id": persona.id,
        "nombre": persona.nombre,
        "apellido": persona.apellido,
        "ci": persona.ci,
        "rol": persona.rol,
        "username": persona.username,
        "sub_programa": persona.sub_programa.nombre if persona.sub_programa else ''
    }
}, status=status.HTTP_200_OK)

class SubProgramaViewSet(viewsets.ModelViewSet):
    """
    Viewset para SubProgramas
    """
    queryset = SubPrograma.objects.all()
    serializer_class = SubProgramaSerializer


class PersonaViewSet(viewsets.ModelViewSet):
    """
    Viewset para Personas (Estudiantes y Jefes)
    """
    queryset = Persona.objects.select_related('sub_programa')
    serializer_class = PersonaSerializer
