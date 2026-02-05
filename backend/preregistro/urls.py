from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import PreRegistroViewSet

router = DefaultRouter()
router.register(r'preregistros', PreRegistroViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
