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
        # 👇 Agregado 'autor_ci' para que Vue pueda enviarlo
        fields = ['id', 'incidencia', 'autor_ci', 'texto', 'fecha', 'imagenes']

# ------------------------------
# Incidencia
# ------------------------------
class IncidenciaSerializer(serializers.ModelSerializer):
    persona = PersonaSerializer(read_only=True)
    
    persona_id = serializers.PrimaryKeyRelatedField(
        queryset=Persona.objects.all(),
        source='persona', 
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
            'persona',
            'persona_id',
            'tipo_incidencia',
            'descripcion',
            'estado',
            'fecha_creacion',
            # 👇 NUEVOS CAMPOS: Para que Vue sepa si hay algo sin leer
            'leido_por_jefe',
            'leido_por_estudiante',
            'imagenes',
            'nuevas_imagenes',
            'mensajes'
        ]

    def create(self, validated_data):
        imagenes = validated_data.pop('nuevas_imagenes', [])
        incidencia = Incidencia.objects.create(**validated_data)
        
        for img in imagenes:
            IncidenciaImagen.objects.create(incidencia=incidencia, imagen=img)
        
        # Al crear la incidencia, el sistema genera el primer mensaje
        # Usamos la CI de la persona para que la señal sepa que es el mensaje inicial
        Mensaje.objects.create(
            incidencia=incidencia,
            autor_ci=incidencia.persona.ci,
            texto="Incidencia creada. Inicie el chat aquí."
        )
        return incidencia