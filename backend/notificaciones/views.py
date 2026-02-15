from django.shortcuts import render

import random
from django.core import signing
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from registros.models import Persona
from .utils import enviar_correo_codigo

class SolicitarCodigoView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')

        try:
            # 1. Validar que el usuario y correo coincidan
            Persona.objects.get(username=username, email=email)
            
            # 2. Generar código aleatorio
            codigo = str(random.randint(100000, 999999))

            # 3. Crear Token Firmado (Contiene el código y el email cifrados)
            token_temporal = signing.dumps({'email': email, 'codigo': codigo})

            # 4. Enviar por correo
            if enviar_correo_codigo(email, codigo):
                return Response({
                    "message": "Código enviado con éxito",
                    "token_temporal": token_temporal # 👈 Se envía al Vue
                }, status=status.HTTP_200_OK)
            
            return Response({"error": "Error al conectar con el servidor de correos"}, status=status.INTERNAL_SERVER_ERROR)

        except Persona.DoesNotExist:
            return Response({"error": "El usuario o el correo no son correctos"}, status=status.HTTP_404_NOT_FOUND)

class ConfirmarCambioPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        token_temporal = request.data.get('token_temporal')
        codigo_usuario = request.data.get('codigo')
        nueva_password = request.data.get('password')

        try:
            # 1. Abrir el token (falla si pasaron más de 10 min o si fue alterado)
            datos = signing.loads(token_temporal, max_age=600)
            
            # 2. Comparar códigos
            if str(codigo_usuario) == str(datos['codigo']):
                usuario = Persona.objects.get(email=datos['email'])
                usuario.password = nueva_password # Se hashea en el save() de tu modelo
                usuario.save()
                return Response({"message": "Contraseña actualizada correctamente"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "El código introducido es incorrecto"}, status=status.HTTP_400_BAD_REQUEST)

        except signing.SignatureExpired:
            return Response({"error": "El código ha expirado, solicita uno nuevo"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"error": "Error de validación de seguridad"}, status=status.HTTP_400_BAD_REQUEST)