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
from apps.cuestionarios.views import CuestionarioViewSet

# Importar vistas del frontend
from core import views

# Router API


router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'charlas', CharlaViewSet, basename='charla')
router.register(r'asistencias', AsistenciaViewSet, basename='asistencia')
router.register(r'reportes', ReporteViewSet, basename='reporte')
router.register(r'accesos', ControlAccesoViewSet, basename='acceso')
router.register(r'cuestionarios', CuestionarioViewSet, basename='cuestionario')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Routes
    path('api/', include(router.urls)),
    path('api/stats/', views.api_stats, name='api_stats'),
    
    # ========== FRONTEND VIEWS ==========
    
    # Auth
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    
    # Dashboards
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/supervisor/', views.dashboard_supervisor, name='dashboard_supervisor'),
    path('dashboard/trabajador/', views.dashboard_trabajador, name='dashboard_trabajador'),
    
    # Charlas
    path('charlas/', views.listar_charlas, name='listar_charlas'),
    path('charlas/crear/', views.crear_charla, name='crear_charla'),
    path('charlas/<int:charla_id>/', views.detalle_charla, name='detalle_charla'),

    path('charlas/<int:charla_id>/firmar/', views.firmar_charla, name='firmar_charla'),
    
    # Cuestionarios
    path('cuestionarios/crear',views.crear_cuestionario, name= 'crear_cuestionario'),
    path('cuestionarios/detalle', views.detalle_cuestionario, name='detalle_cuestionario'),
    # Usuarios
    path('usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    
    # Reportes
    path('reportes/', views.listar_reportes, name='listar_reportes'),
    
    # Accesos
    path('accesos/', views.control_accesos, name='control_accesos'),
]

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)