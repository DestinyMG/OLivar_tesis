from rest_framework import serializers
from .models import Incidencia, IncidenciaImagen, Mensaje, MensajeImagen
from registros.models import Persona, SubPrograma

# ------------------------------
# SubPrograma
# ------------------------------
class SubProgramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubPrograma
        fields = ['id', 'nombre']

# ------------------------------
# Persona
# ------------------------------
class PersonaSerializer(serializers.ModelSerializer):
    sub_programa = SubProgramaSerializer(read_only=True)

    class Meta:
        model = Persona
        fields = ['id', 'nombre', 'apellido', 'ci', 'rol', 'sub_programa', 'imagen']

# ------------------------------
# Imagen de Incidencia
# ------------------------------
class IncidenciaImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidenciaImagen
        fields = ['id', 'incidencia', 'imagen']

# ------------------------------
# Imagen de Mensaje
# ------------------------------
class MensajeImagenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeImagen
        fields = ['id', 'mensaje', 'imagen']

# ------------------------------
# Mensaje (Chat)
# ------------------------------
class MensajeSerializer(serializers.ModelSerializer):
    imagenes = MensajeImagenSerializer(many=True, read_only=True)

    class Meta:
        model = Mensaje
        fields = ['id', 'incidencia', 'texto', 'fecha', 'imagenes']

# ------------------------------
# Incidencia
# ------------------------------
class IncidenciaSerializer(serializers.ModelSerializer):
    # Esto se queda igual para ver los datos del usuario
    persona = PersonaSerializer(read_only=True)
    
    # 👇 AGREGA ESTA LÍNEA: Este campo recibirá el ID desde Vue
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(),
        source='persona', # <--- Esto le dice que guarde el ID en el campo 'persona' del modelo
        write_only=True
    )
    
    imagenes = IncidenciaImagenSerializer(many=True, read_only=True)
    nuevas_imagenes = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )
    mensajes = MensajeSerializer(many=True, read_only=True)

    class Meta:
        model = Incidencia
        fields = [
            'id',
            'persona',       # Lectura
            'persona_id',    # Escritura (ID)
            'tipo_incidencia',
            'descripcion',
            'estado',
            'fecha_creacion',
            'imagenes',
            'nuevas_imagenes',
            'mensajes'
        ]

    def create(self, validated_data):
        # Ahora validated_data ya traerá el objeto 'persona' gracias a persona_id + source='persona'
        imagenes = validated_data.pop('nuevas_imagenes', [])
        incidencia = Incidencia.objects.create(**validated_data)
        
        for img in imagenes:
            IncidenciaImagen.objects.create(incidencia=incidencia, imagen=img)
        
        Mensaje.objects.create(
            incidencia=incidencia,
            texto="Incidencia creada. Inicie el chat aquí."
        )
        return incidencia