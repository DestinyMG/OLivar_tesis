from rest_framework import serializers
from .models import Persona, SubPrograma

# registros/serializers.py
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from .models import Persona

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
        required=False, # Lo hacemos opcional para que el PATCH de perfil no lo exija
        allow_null=True
    )

    # 🔹 Ocultar password al leer, solo permitir escribir. 
    # required=False permite actualizar el perfil sin cambiar la clave cada vez.
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Persona
        fields = [
            'id',
            'nombre',
            'apellido',
            'ci',
            'rol',
            'username',
            'password',
            'imagen',
            'sub_programa',
            'sub_programa_id',
        ]

    # --- AQUÍ ESTÁ EL TRUCO PARA EL PERFIL ---
    def update(self, instance, validated_data):
        # 1. Extraemos el password si viene en la petición
        password = validated_data.pop('password', None)
        
        # 2. Actualizamos los demás campos (nombre, apellido, imagen, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # 3. Si el usuario envió una nueva contraseña, la encriptamos antes de guardar
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance