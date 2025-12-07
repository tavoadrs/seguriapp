from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'rut', 'rol', 'is_active']
    list_filter = ['rol', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'rut', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rut', 'rol')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('rut', 'rol', 'email', 'first_name', 'last_name')}),
    )

# charlas/admin.py
from django.contrib import admin
from apps.charlas.models import Charla

@admin.register(Charla)
class CharlaAdmin(admin.ModelAdmin):
    list_display = ['tema', 'fecha', 'hora', 'supervisor', 'created_at']
    list_filter = ['fecha', 'supervisor']
    search_fields = ['tema', 'supervisor__username']
    date_hierarchy = 'fecha'

# asistencias/admin.py
from django.contrib import admin
from apps.asistencias.models import Asistencia

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'charla', 'hora_firma']
    list_filter = ['hora_firma', 'charla']
    search_fields = ['usuario__username', 'charla__tema']
    date_hierarchy = 'hora_firma'

# reportes/admin.py
from django.contrib import admin
from apps.reportes.models import Reporte

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['charla', 'fecha_generado', 'url_pdf']
    list_filter = ['fecha_generado']
    search_fields = ['charla__tema']
    date_hierarchy = 'fecha_generado'

# accesos/admin.py
from django.contrib import admin
from apps.accesos.models import ControlAcceso

@admin.register(ControlAcceso)
class ControlAccesoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'hora_entrada', 'hora_salida']
    list_filter = ['hora_entrada', 'usuario']
    search_fields = ['usuario__username']
    date_hierarchy = 'hora_entrada'