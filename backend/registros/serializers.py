from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from .models import Persona, SubPrograma

# registros/serializers.py

class AuthSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            persona = Persona.objects.get(username=data['username'])
        except Persona.DoesNotExist:
            raise serializers.ValidationError("Credenciales incorrectas")

        if not check_password(data['password'], persona.password):
            raise serializers.ValidationError("Credenciales incorrectas")

        return persona


class SubProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubPrograma
        fields = '__all__'


class PersonaSerializer(serializers.ModelSerializer):
    sub_programa = SubProgramaSerializer(read_only=True)
    sub_programa_id = serializers.PrimaryKeyRelatedField(
        queryset=SubPrograma.objects.all(),
        source='sub_programa',
        write_only=True,
        required=False, 
        allow_null=True
    )

    # El campo email ahora es parte integral del serializador
    email = serializers.EmailField(required=False, allow_blank=True)

    # Ocultar password al leer, permitir escribir de forma opcional
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Persona
        fields = [
            'id',
            'nombre',
            'apellido',
            'ci',
            'email',        # ✅ Campo agregado
            'rol',
            'username',
            'password',
            'imagen',
            'sub_programa',
            'sub_programa_id',
        ]

    def update(self, instance, validated_data):
        # 1. Extraemos el password si viene en la petición
        password = validated_data.pop('password', None)
        
        # 2. Actualizamos los demás campos (nombre, apellido, email, imagen, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 3. Si hay un nuevo password, lo asignamos.
        # Al llamar a instance.save(), el método save() de tu modelo Persona 
        # detectará que no está hasheado y lo encriptará automáticamente.
        if password:
            instance.password = password
            
        instance.save()
        return instance