from django.db import models
from registros.models import SubPrograma  # Importa SubPrograma de tu app registros
from django.contrib.auth.hashers import make_password

class PreRegistro(models.Model):

    ROL_CHOICES = (
        ('ESTUDIANTE', 'Estudiante'),
        ('JEFE_SUB_PROGRAMA', 'Jefe de Sub Programa'),
    )

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True)
    email = models.EmailField(max_length=255, unique=True)  # <-- Campo agregado
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)
    sub_programa = models.ForeignKey(
        SubPrograma,
        on_delete=models.PROTECT,
        related_name='preregistros'
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='ESTUDIANTE'
    )
    imagen = models.ImageField(upload_to='preregistro/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 🔹 Hashea la password automáticamente si no está hasheada
        if not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.rol} - {self.sub_programa}"