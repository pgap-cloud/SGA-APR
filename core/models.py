from django.db import models
from django.contrib.auth.models import AbstractUser 
from django.contrib.auth.hashers import make_password
from django.utils import timezone

class Usuario(AbstractUser):
    """Modelo personalizado para el usuario que extiende AbstractUser."""
    
    # Definición de los roles disponibles
    ROLES = [
        ('USUARIO', 'Usuario'),
        ('SECRETARIA', 'Secretaria'),
        ('ADMINISTRADOR', 'Administrador'),
        ('OPERARIO', 'Operario')
    ]
    
    # Campos de rol y perfil
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='USUARIO'
    )
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    
    # Campos de seguridad
    failed_login_attempts = models.IntegerField(
        default=0,
        verbose_name='Intentos de inicio de sesión fallidos'
    )
    last_login_attempt = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Último intento de inicio de sesión'
    )
    locked_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='Fecha de bloqueo de cuenta'
    )
    is_account_locked = models.BooleanField(
        default=False,
        verbose_name='Cuenta bloqueada'
    )
    
    # Campos de auditoría con default
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Última actualización'
    )
    
    # Campos de seguimiento de actividad
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última actividad'
    )
    
    def __str__(self):
        """Devuelve el nombre de usuario como representación del objeto."""
        return f"{self.username} - {self.get_rol_display()}"

    def save(self, *args, **kwargs):
        """Sobrescribe el método save para encriptar la contraseña antes de guardar."""
        # Verifica si la contraseña ya está encriptada
        if not self.password.startswith('pbkdf2_sha256$'):
            self.password = make_password(self.password)
        
        # Actualizar campos de auditoría
        if not self.pk:  # Si es un nuevo usuario
            self.created_at = timezone.now()
        
        self.updated_at = timezone.now()
        
        super().save(*args, **kwargs)

    # Resto del código permanece igual...

    # Métodos para verificación rápida de roles (mantenidos igual)
    @property
    def es_usuario(self):
        return self.rol == 'USUARIO'

    @property
    def es_secretaria(self):
        return self.rol == 'SECRETARIA'

    @property
    def es_administrador(self):
        return self.rol == 'ADMINISTRADOR'

    @property
    def es_operario(self):
        return self.rol == 'OPERARIO'

    # Campos para grupos y permisos (mantenidos igual)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuarios_core',
        blank=True,
        help_text='Los grupos a los que pertenece este usuario.',
        verbose_name='grupos',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuarios_core',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        verbose_name='permisos de usuario',
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']  # Ordenar por fecha de creación