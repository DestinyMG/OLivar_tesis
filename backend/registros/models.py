from django.db import models
from django.contrib.auth.hashers import make_password

class SubPrograma(models.Model):
    nombre = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.nombre


class Persona(models.Model):

    ROL_CHOICES = (
        ('ESTUDIANTE', 'Estudiante'),
        ('JEFE_SUB_PROGRAMA', 'Jefe de Sub Programa'),
    )

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True)
    
    # 📧 Nuevo campo agregado para que coincida con PreRegistro
    email = models.EmailField(models.EmailField(max_length=255, null=True, blank=True))

    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='ESTUDIANTE'
    )

    sub_programa = models.ForeignKey(
        SubPrograma,
        on_delete=models.PROTECT,
        related_name='personas'
    )

    imagen = models.ImageField(
        upload_to='personas/',
        null=True,
        blank=True
    )

    # 🔐 Usuario y contraseña
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        # 🔹 Si la password no está hasheada, la hashea
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.rol} - {self.sub_programa}"