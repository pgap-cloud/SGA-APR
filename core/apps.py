from django.apps import AppConfig

class CoreConfig(AppConfig):
    """Configuración de la aplicación Core."""
    
    default_auto_field = 'django.db.models.BigAutoField'  # Define el tipo de campo automático por defecto para los modelos
    name = 'core'  # Nombre de la aplicación

    def ready(self):
        """Método que se ejecuta cuando la aplicación está lista."""
        # Importa las señales para que se registren al iniciar la aplicación
        import core.signals