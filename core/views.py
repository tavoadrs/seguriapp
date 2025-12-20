

from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.shortcuts import get_object_or_404
from apps.charlas.views import Charla

def login_view(request):
    """Vista de login - Sin autenticación requerida"""
    return render(request, 'usuarios/login.html')

# DASHBOARDS - Sin @login_required, la autenticación se maneja por JWT en el frontend
def dashboard_admin(request):
    """Dashboard para administradores"""
    return render(request, 'dashboard/admin_dashboard.html')

def dashboard_supervisor(request):
    """Dashboard para supervisores"""
    return render(request, 'dashboard/supervisor_dashboard.html')

def dashboard_trabajador(request):
    """Dashboard para trabajadores"""
    return render(request, 'dashboard/trabajador_dashboard.html')

def dashboard_home(request):
    """Página de dashboard genérica - el JS decidirá a dónde ir"""
    return render(request, 'dashboard/trabajador_dashboard.html')

# CHARLAS
def listar_charlas(request):
    """Lista todas las charlas"""
    return render(request, 'charlas/listar_charlas.html')

def crear_charla(request):
    """Formulario para crear charla"""
    return render(request, 'charlas/crear_charla.html')

def detalle_charla(request, charla_id):
    """Detalle de una charla específica"""
    return render(request, 'charlas/detalle_charla.html', {'charla_id': charla_id})

def firmar_charla(request, charla_id):
    """Vista para firmar asistencia"""
    charla = get_object_or_404(Charla.objects.select_related('supervisor'), # CLAVE
    id=charla_id
    )
    return render(request, 'charlas/firmar_charla.html', {'charla': charla})

#CUESTIONARIOS
def crear_cuestionario(request):
    """Formulario para crear cuestionarios"""
    return render(request,'cuestionarios/crear_cuestionario.html')

# USUARIOS
def gestionar_usuarios(request):
    """Gestión de usuarios"""
    return render(request, 'usuarios/gestionar_usuarios.html')

# REPORTES
def listar_reportes(request):
    """Lista de reportes"""
    return render(request, 'reportes/listar_reportes.html')

# ACCESOS
def control_accesos(request):
    """Control de accesos"""
    return render(request, 'accesos/control.html')

# API Stats para dashboard
def api_stats(request):
    """Estadísticas para el dashboard"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    
    if not token:
        return JsonResponse({'error': 'No token provided'}, status=401)
    
    # Hacer requests a la API interna
    headers = {'Authorization': f'Bearer {token}'}
    base_url = f'http://{request.get_host()}'
    
    try:
        usuarios = requests.get(f'{base_url}/api/usuarios/', headers=headers).json()
        charlas = requests.get(f'{base_url}/api/charlas/', headers=headers).json()
        asistencias = requests.get(f'{base_url}/api/asistencias/', headers=headers).json()
        reportes = requests.get(f'{base_url}/api/reportes/', headers=headers).json()
        
        return JsonResponse({
            'usuarios': usuarios.get('count', 0),
            'charlas': charlas.get('count', 0),
            'asistencias': asistencias.get('count', 0),
            'reportes': reportes.get('count', 0),
        })
    except Exception as e:
        return JsonResponse({
            'usuarios': 0,
            'charlas': 0,
            'asistencias': 0,
            'reportes': 0,
        })