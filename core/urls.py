from django.urls import path
from . import views  # Importa las vistas desde el archivo views.py

urlpatterns = [
    # --- Rutas de la aplicación ---
    path('', views.index, name='index'),  # Ruta para la página de inicio
    path('registro/', views.registro_view, name='registro'),  # Ruta para el registro de usuarios
    path('login/', views.login_view, name='login'),  # Ruta para el inicio de sesión
    path('logout/', views.logout_view, name='logout'),  # Ruta para cerrar sesión
    
    # --- Rutas de los Dashboards ---
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),  # Ruta para el dashboard de administradores
    path('dashboard/secretaria/', views.secretaria_dashboard, name='secretaria_dashboard'),  # Ruta para el dashboard de secretarias
    path('dashboard/operario/', views.operario_dashboard, name='operario_dashboard'),  # Ruta para el dashboard de operarios
    path('dashboard/usuario/', views.usuario_dashboard, name='usuario_dashboard'),  # Ruta para el dashboard de usuarios regulares
    path('acceso-denegado/', views.acceso_denegado, name='acceso_denegado'),  # Ruta para la página de acceso denegado
]