from django.db import models
from django.core.exceptions import ValidationError
from registros.models import Persona
from django.db.models.signals import post_save
from django.dispatch import receiver

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

    # --- CAMPOS DE NOTIFICACIÓN ---
    # Se marcan en False cuando hay algo nuevo que leer para ese rol
    leido_por_jefe = models.BooleanField(default=True)
    leido_por_estudiante = models.BooleanField(default=True)

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
    # Identifica quién envía el mensaje para disparar la lógica de notificación
    autor_ci = models.CharField(max_length=20, blank=True, null=True) 
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


# ==============================================================
# LÓGICA DE NOTIFICACIÓN AUTOMÁTICA (SIGNALS)
# ==============================================================

@receiver(post_save, sender=Mensaje)
def actualizar_notificacion_lectura(sender, instance, created, **kwargs):
    """
    Cada vez que se crea un mensaje, marcamos la incidencia 
    como NO LEÍDA para el receptor basándonos en la CI del autor.
    """
    if created:
        incidencia = instance.incidencia
        
        # Si el autor del mensaje es el dueño de la incidencia (Estudiante)
        if instance.autor_ci == incidencia.persona.ci:
            incidencia.leido_por_jefe = False
            incidencia.leido_por_estudiante = True 
        else:
            # Si el autor es el Jefe o Administrador
            incidencia.leido_por_estudiante = False
            incidencia.leido_por_jefe = True 
        
        incidencia.save()