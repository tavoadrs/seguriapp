from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.users.views import UsuarioViewSet
from apps.charlas.views import CharlaViewSet
from apps.asistencias.views import AsistenciaViewSet
from apps.reportes.views import ReporteViewSet
from apps.accesos.views import ControlAccesoViewSet

# Router principal
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'charlas', CharlaViewSet, basename='charla')
router.register(r'asistencias', AsistenciaViewSet, basename='asistencia')
router.register(r'reportes', ReporteViewSet, basename='reporte')
router.register(r'accesos', ControlAccesoViewSet, basename='acceso')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Routes
    path('api/', include(router.urls)),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)