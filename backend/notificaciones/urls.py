from django.urls import path
from .views import SolicitarCodigoView, ConfirmarCambioPasswordView

urlpatterns = [
    path('solicitar-codigo/', SolicitarCodigoView.as_view(), name='solicitar_codigo'),
    path('confirmar-cambio/', ConfirmarCambioPasswordView.as_view(), name='confirmar_cambio'),
]