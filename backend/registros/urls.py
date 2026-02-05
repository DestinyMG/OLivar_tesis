from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PersonaViewSet, SubProgramaViewSet, AuthTokenView  # 👈 agregamos AuthTokenView

router = DefaultRouter()
router.register(r'personas', PersonaViewSet)
router.register(r'sub-programas', SubProgramaViewSet)

urlpatterns = [
    path('', include(router.urls)),           # 🔹 rutas de los ViewSets
    path('auth/token/', AuthTokenView.as_view(), name='auth-token'),  # 🔹 login JWT
]
