from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from .models import Persona, SubPrograma
from .serializers import PersonaSerializer, SubProgramaSerializer, AuthSerializer

# views.py

class AuthTokenView(APIView):
    """
    Vista personalizada para autenticación y generación de Token.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        persona = serializer.validated_data

        # 🔐 Token SIMPLE (Contiene ID y ROL para validaciones rápidas)
        token = AccessToken()
        token['persona_id'] = persona.id
        token['rol'] = persona.rol

        # 🚀 Respuesta con datos completos para el Frontend
        return Response({
            "access": str(token),
            "usuario": {
                "id": persona.id,
                "nombre": persona.nombre,
                "apellido": persona.apellido,
                "ci": persona.ci,
                "email": persona.email, # ✅ Agregado para que el perfil lo tenga desde el inicio
                "rol": persona.rol,
                "username": persona.username,
                "sub_programa": persona.sub_programa.nombre if persona.sub_programa else ''
            }
        }, status=status.HTTP_200_OK)


class SubProgramaViewSet(viewsets.ModelViewSet):
    """
    Viewset para gestionar los SubProgramas.
    """
    queryset = SubPrograma.objects.all()
    serializer_class = SubProgramaSerializer


class PersonaViewSet(viewsets.ModelViewSet):
    serializer_class = PersonaSerializer

    def get_queryset(self):
        queryset = Persona.objects.select_related('sub_programa')

        sub_programa_id = self.request.query_params.get('sub_programa_id')
        if sub_programa_id:
            queryset = queryset.filter(sub_programa_id=sub_programa_id)

        return queryset
