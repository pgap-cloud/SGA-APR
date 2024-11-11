# core/signals.py
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from .models import Usuario  # Asegúrate de importar tu modelo de Usuario

# Configura el logger
logger = logging.getLogger('authentication')
security_logger = logging.getLogger('security')

def get_client_ip(request):
    """
    Obtiene la dirección IP del cliente
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Registra cada inicio de sesión exitoso con detalles adicionales
    """
    try:
        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Actualizar último inicio de sesión
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Registro de seguridad detallado
        security_logger.info(f"Inicio de sesión exitoso - Usuario: {user.username}, "
                              f"Rol: {user.rol}, "
                              f"IP: {ip}, "
                              f"User Agent: {user_agent}")
        
        # Registro de auditoría
        logger.info(f"Inicio de sesión - Usuario: {user.username}, Rol: {user.rol}")
    except Exception as e:
        logger.error(f"Error al registrar inicio de sesión: {e}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Registra cada cierre de sesión
    """
    try:
        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        security_logger.info(f"Cierre de sesión - Usuario: {user.username}, "
                              f"Rol: {user.rol}, "
                              f"IP: {ip}, "
                              f"User Agent: {user_agent}")
    except Exception as e:
        logger.error(f"Error al registrar cierre de sesión: {e}")

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """
    Registra intentos de inicio de sesión fallidos con más detalles
    """
    try:
        ip = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        username = credentials.get('username', 'Unknown')
        
        # Registro de seguridad detallado para intentos fallidos
        security_logger.warning(f"Intento de inicio de sesión fallido - "
                                 f"Usuario: {username}, "
                                 f"IP: {ip}, "
                                 f"User Agent: {user_agent}")
        
        # Opcional: Implementar lógica de bloqueo de cuenta
        self.check_and_lock_account(username)
    except Exception as e:
        logger.error(f"Error al registrar inicio de sesión fallido: {e}")

def check_and_lock_account(username):
    """
    Verifica y bloquea la cuenta después de múltiples intentos fallidos
    """
    try:
        # Buscar el usuario
        user = Usuario.objects.filter(username=username).first()
        
        if user:
            # Incrementar contador de intentos fallidos
            user.failed_login_attempts += 1
            
            # Bloquear cuenta después de X intentos fallidos
            if user.failed_login_attempts >= 5:
                user.is_active = False
                user.locked_at = timezone.now()
                security_logger.critical(f"Cuenta bloqueada - Usuario: {username}")
            
            user.save(update_fields=['failed_login_attempts', 'is_active', 'locked_at'])
    except Exception as e:
        logger.error(f"Error al verificar bloqueo de cuenta: {e}")

@receiver(post_save, sender=Usuario)
def handle_user_creation(sender, instance, created, **kwargs):
    """
    Maneja la creación de nuevos usuarios
    """
    if created:
        try:
            # Registro de creación de usuario
            logger.info(f"Nuevo usuario creado - Username: {instance.username}, Rol: {instance.rol}")
            
            # Opcional: Enviar notificación de bienvenida
            # send_welcome_email(instance)
        except Exception as e:
            logger.error(f"Error al procesar creación de usuario: {e}")

# Función opcional para enviar correo de bienvenida
def send_welcome_email(user):
    """
    Envía un correo de bienvenida al nuevo usuario
    """
    try:
        # Implementar lógica de envío de correo
        pass
    except Exception as e:
        logger.error(f"Error al enviar correo de bienvenida: {e}")