from rest_framework import serializers
from .models import PreRegistro
from registros.models import SubPrograma, Persona

class PreRegistroSerializer(serializers.ModelSerializer):
    sub_programa_id = serializers.PrimaryKeyRelatedField(
        queryset=SubPrograma.objects.all(),
        source='sub_programa'
    )
    
    sub_programa = serializers.StringRelatedField(read_only=True)
    
    # Mantenemos password visible para la lógica de migración que mencionaste
    password = serializers.CharField(required=True) 

    class Meta:
        model = PreRegistro
        fields = [
            'id',
            'nombre',
            'apellido',
            'ci',
            'email',      # <-- Nuevo campo incluido
            'username',
            'password',
            'sub_programa',
            'sub_programa_id',
            'rol',
            'imagen',
            'fecha_creacion'
        ]

    # ----------------------
    # Validaciones de unicidad
    # ----------------------

    def validate_email(self, value):
        # Revisar en usuarios ya registrados
        if Persona.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado en el sistema")
        # Revisar en preregistros pendientes
        if PreRegistro.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya tiene una solicitud pendiente")
        return value

    def validate_ci(self, value):
        if Persona.objects.filter(ci=value).exists():
            raise serializers.ValidationError("La cédula ya está registrada en el sistema")
        if PreRegistro.objects.filter(ci=value).exists():
            raise serializers.ValidationError("La cédula ya tiene una solicitud pendiente")
        return value

    def validate_username(self, value):
        if Persona.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario ya está registrado en el sistema")
        if PreRegistro.objects.filter(username=value).exists():
            raise serializers.ValidationError("El usuario ya tiene una solicitud pendiente")
        return value