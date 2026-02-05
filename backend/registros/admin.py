from django.contrib import admin

# Register your models here.

from .models import Persona, SubPrograma

@admin.register(SubPrograma)
class SubProgramaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)


@admin.register(Persona)
class PersonaAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nombre',
        'apellido',
        'ci',
        'username',
        'rol',
        'sub_programa',
        'imagen',
    )
    search_fields = ('nombre', 'apellido', 'ci', 'username')
    list_filter = ('rol', 'sub_programa')
