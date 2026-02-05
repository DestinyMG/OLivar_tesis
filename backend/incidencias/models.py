from django.db import models
from django.core.exceptions import ValidationError
from registros.models import Persona

# ===============================
# Incidencia
# ===============================
class Incidencia(models.Model):
    ESTADO_CHOICES = (
        ('CREADA', 'Creada'),
        ('ABIERTA', 'Abierta'),
        ('RESUELTA', 'Resuelta'),
        ('RECHAZADA', 'Rechazada'),
    )

    TIPO_INCIDENCIA_CHOICES = (
        ('INSCRIPCION_TEMPORAL', 'Inscripción Temporal'),
        ('REINGRESO', 'Reingreso'),
        ('CARGA_NOTAS_TEMPORAL', 'Carga de Notas Temporal'),
        ('AUTO_ESTUDIO', 'Auto Estudio'),
        ('PRUEBA_GLOBAL', 'Prueba Global'),
        ('DENUNCIA', 'Denuncia'),
        ('INTERSEMESTRAL', 'Solicitud de Intersemestral'),
    )

    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='incidencias')
    tipo_incidencia = models.CharField(max_length=30, choices=TIPO_INCIDENCIA_CHOICES)
    descripcion = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='CREADA')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_incidencia_display()} - {self.persona}"


# ===============================
# Imagen de Incidencia
# ===============================
class IncidenciaImagen(models.Model):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='incidencias/')

    def clean(self):
        if self.imagen and not self.imagen.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError('Solo se permiten imágenes JPEG o PNG')

    def __str__(self):
        return f"Imagen incidencia #{self.incidencia.id}"


# ===============================
# Mensaje (Chat)
# ===============================
class Mensaje(models.Model):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name='mensajes')
    texto = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mensaje #{self.id} - Incidencia {self.incidencia.id}"


# ===============================
# Imagen de Mensaje
# ===============================
class MensajeImagen(models.Model):
    mensaje = models.ForeignKey(Mensaje, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='mensajes/')

    def clean(self):
        if self.imagen and not self.imagen.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValidationError('Solo se permiten imágenes JPEG o PNG')

    def __str__(self):
        return f"Imagen mensaje #{self.mensaje.id}"
