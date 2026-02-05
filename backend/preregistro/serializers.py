from rest_framework import serializers
from .models import PreRegistro
from registros.models import SubPrograma, Persona  # Importamos los usuarios ya registrados

class PreRegistroSerializer(serializers.ModelSerializer):
    sub_programa_id = serializers.PrimaryKeyRelatedField(
        queryset=SubPrograma.objects.all(),
        source='sub_programa',
        # ❌ Quitamos write_only=True para que el Admin pueda leer el ID
    )
    
    sub_programa = serializers.StringRelatedField(read_only=True)
    
    # ❌ Quitamos write_only=True para que el Admin pueda leer la contraseña y migrarla
    password = serializers.CharField(required=True) 

    class Meta:
        model = PreRegistro
        fields = [
            'id',
            'nombre',
            'apellido',
            'ci',
            'username',
            'password',
            'sub_programa',
            'sub_programa_id',
            'rol',
            'imagen',
            'fecha_creacion'
        ]

    # ----------------------
    # Validaciones para unicidad en ambos lugares
    # ----------------------
    def validate_ci(self, value):
        # Revisar en usuarios ya registrados
        if Persona.objects.filter(ci=value).exists():
            raise serializers.ValidationError("La cédula ya está registrada en el sistema")
        # Revisar en preregistros pendientes
        if PreRegistro.objects.filter(ci=value).exists():
            raise serializers.ValidationError("La cédula ya tiene una solicitud pendiente")
        return value

    def validate_username(self, value):
        # Revisar en usuarios ya registrados
        if Persona.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario ya está registrado en el sistema")
        # Revisar en preregistros pendientes
        if PreRegistro.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario ya tiene una solicitud pendiente")
        return value
