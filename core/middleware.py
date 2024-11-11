# En core/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import logging
from django.utils import timezone
# middleware.py
from django.utils.cache import add_never_cache_headers

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si el usuario no está autenticado, añade headers para prevenir caché
        if not request.user.is_authenticated:
            add_never_cache_headers(response)
        
        return response


logger = logging.getLogger(__name__)

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Definir mapeo de rutas por rol
        self.role_routes = {
            'ADMINISTRADOR': [
                '/dashboard/admin/',
                '/admin/',
                '/configuraciones/',
                '/reportes/'
            ],
            'SECRETARIA': [
                '/dashboard/secretaria/',
                '/registro-consumo/',
                '/generar-boletas/',
                '/pagos/'
            ],
            'OPERARIO': [
                '/dashboard/operario/',
                '/mantenimiento/',
                '/lecturas-medidor/'
            ],
            'USUARIO': [
                '/dashboard/usuario/',
                '/mis-consumos/',
                '/mis-pagos/'
            ]
        }

    def __call__(self, request):
        # Logging detallado
        logger.info(f"RoleMiddleware processing: {request.path}")
        
        # Verifica si el usuario está autenticado
        if request.user.is_authenticated:
            # Verificar que el usuario tenga un rol definido
            if not hasattr(request.user, 'rol'):
                logger.warning(f"User {request.user.username} has no role defined")
                messages.error(request, "Tu cuenta no tiene un rol asignado. Contacta al administrador.")
                return redirect(reverse('logout'))
            
            # Control de acceso por rol
            current_path = request.path
            user_role = request.user.rol

            # Verificar si la ruta está restringida para este rol
            for role, routes in self.role_routes.items():
                if role != user_role:
                    for route in routes:
                        if current_path.startswith(route):
                            logger.warning(f"Unauthorized access attempt by {request.user.username} to {current_path}")
                            messages.error(request, "No tienes permiso para acceder a esta página.")
                            return redirect(reverse('index'))
            
            # Redirigir a dashboard correcto si accede a dashboard genérico
            if current_path == '/dashboard/':
                return self.redirect_to_correct_dashboard(request)
        
        # Continúa con el procesamiento normal
        response = self.get_response(request)
        
        return response

    def redirect_to_correct_dashboard(self, request):
        """Redirige al dashboard correcto según el rol del usuario"""
        dashboards = {
            'ADMINISTRADOR': 'admin_dashboard',
            'SECRETARIA': 'secretaria_dashboard',
            'OPERARIO': 'operario_dashboard',
            'USUARIO': 'usuario_dashboard'
        }
        
        dashboard_name = dashboards.get(request.user.rol, 'index')
        logger.info(f"Redirecting {request.user.username} to {dashboard_name}")
        
        return redirect(reverse(dashboard_name))

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Solo procesar para usuarios autenticados
        if request.user.is_authenticated:
            # Verificar la duración de la sesión
            if not request.session.get('_session_init_timestamp'):
                # Inicializar timestamp de sesión
                request.session['_session_init_timestamp'] = timezone.now().timestamp()
            
            # Definir tiempo de expiración (por ejemplo, 2 horas)
            session_timeout = 2 * 60 * 60  # 2 horas en segundos
            current_time = timezone.now().timestamp()
            
            # Verificar si la sesión ha expirado
            if (current_time - request.session.get('_session_init_timestamp', 0)) > session_timeout:
                logger.warning(f"Session timeout for user {request.user.username}")
                messages.warning(request, "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.")
                logout(request)
                return redirect(reverse('login'))
        
        response = self.get_response(request)
        return response

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Añadir headers de seguridad
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response