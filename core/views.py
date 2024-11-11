from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from .forms import RegistroForm
from .models import Usuario
import logging
from django.urls import reverse
from .decorators import logout_required

# --- Configuración de loggers ---
logger = logging.getLogger('django')  # Logger general para Django
auth_logger = logging.getLogger('authentication')  # Logger específico para autenticación

# --- Vistas ---

@logout_required
def index(request):
    """Vista para la página de inicio"""
    return render(request, 'core/index.html')

@logout_required
def registro_view(request):
    """Vista para el registro de usuarios"""
    if request.method == 'POST':
        form = RegistroForm(request.POST)  # Inicializa el formulario con los datos POST
        if form.is_valid():  # Verifica si el formulario es válido
            user = form.save()  # Guarda el usuario
            messages.success(request, '¡Registro exitoso! Por favor, inicia sesión.')
            return redirect('login')  # Redirige a la página de inicio de sesión
        else:
            # Mostrar errores específicos del formulario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = RegistroForm()  # Crea un formulario vacío si no es un POST
    
    return render(request, 'core/registro.html', {'form': form})  # Renderiza la plantilla de registro

@logout_required
def login_view(request):
    """Vista para el inicio de sesión"""
    logger.info(f"Login view called - Method: {request.method}")
    logger.info(f"Current path: {request.path}")
    logger.info(f"Referer: {request.META.get('HTTP_REFERER', 'No referer')}")

    if request.method == 'POST':
        username = request.POST.get('username')  # Obtiene el nombre de usuario
        password = request.POST.get('password')  # Obtiene la contraseña
        
        user = authenticate(request, username=username, password=password)  # Autentica al usuario
        
        if user is not None:  # Si la autenticación es exitosa
            login(request, user)  # Inicia la sesión del usuario
            logger.info(f"User {username} logged in successfully")
            
            # Redirigir según el rol del usuario
            return redirect_to_dashboard(user)
        else:
            logger.warning(f"Failed login attempt for username: {username}")
            messages.error(request, 'Credenciales inválidas.')  # Mensaje de error en caso de fallo
    
    context = {
        'debug_info': {
            'current_path': request.path,
            'referer': request.META.get('HTTP_REFERER', 'No referer')
        }
    }
    return render(request, 'core/login.html', context)  # Renderiza la plantilla de inicio de sesión

@never_cache
def logout_view(request):
    """Vista para cerrar sesión"""
    # Obtener el rol antes de cerrar sesión para redirigir correctamente
    user_rol = request.user.rol if request.user.is_authenticated else None
    
    # Cerrar sesión
    logout(request)
    
    # Limpiar la sesión completamente
    request.session.flush()
    
    # Configurar headers para prevenir caché
    response = redirect('index')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return response

def redirect_to_dashboard(user):
    """Función auxiliar para redirigir al dashboard según el rol"""
    dashboards = {
        'ADMINISTRADOR': 'admin_dashboard',
        'SECRETARIA': 'secretaria_dashboard',
        'OPERARIO': 'operario_dashboard',
        'USUARIO': 'usuario_dashboard'
    }
    
    # Obtener el nombre de la vista de dashboard correspondiente al rol
    dashboard_name = dashboards.get(user.rol, 'index')
    
    return redirect(dashboard_name)

# --- Dashboards ---

@login_required
def admin_dashboard(request):
    """Dashboard para administradores"""
    if not request.user.es_administrador:
        messages.error(request, 'No tienes permiso para acceder a este dashboard.')
        return redirect_to_dashboard(request.user)
    
    context = {
        'usuario': request.user,
    }
    return render(request, 'core/dashboards/admin_dashboard.html', context)

@login_required
def secretaria_dashboard(request):
    """Dashboard para secretarias"""
    if not request.user.es_secretaria:
        messages.error(request, 'No tienes permiso para acceder a este dashboard.')
        return redirect_to_dashboard(request.user)
    
    context = {
        'usuario': request.user,
    }
    return render(request, 'core/dashboards/secretaria_dashboard.html', context)

@login_required
def operario_dashboard(request):
    """Dashboard para operarios"""
    if not request.user.es_operario:
        messages.error(request, 'No tienes permiso para acceder a este dashboard.')
        return redirect_to_dashboard(request.user)
    
    context = {
        'usuario': request.user,
    }
    return render(request, 'core/dashboards/operario_dashboard.html', context)

@login_required
def usuario_dashboard(request):
    """Dashboard para usuarios regulares"""
    if not request.user.es_usuario:
        messages.error(request, 'No tienes permiso para acceder a este dashboard.')
        return redirect_to_dashboard(request.user)
    
    context = {
        'usuario': request.user,
    }
    return render(request, 'core/dashboards/usuario_dashboard.html', context)

def acceso_denegado(request):
    """Vista para acceso denegado"""
    return render(request, 'core/acceso_denegado.html', status=403)