from rest_framework.routers import DefaultRouter
from .views import (
    IncidenciaViewSet,
    IncidenciaImagenViewSet,
    MensajeViewSet,
    MensajeImagenViewSet
)

router = DefaultRouter()
router.register(r'incidencias', IncidenciaViewSet, basename='incidencias')
router.register(r'incidencia-imagenes', IncidenciaImagenViewSet, basename='incidencia-imagenes')
router.register(r'mensajes', MensajeViewSet, basename='mensajes')
router.register(r'mensaje-imagenes', MensajeImagenViewSet, basename='mensaje-imagenes')

urlpatterns = router.urls
