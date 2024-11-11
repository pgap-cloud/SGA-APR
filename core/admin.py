from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ['username', 'email', 'rol', 'is_active', 'is_staff']
    
    # Añade campos personalizados a los fieldsets
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('rol', 'direccion', 'telefono')}),
    )
    
    # Añade campos personalizados al crear un nuevo usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('rol', 'direccion', 'telefono')}),
    )

# Registra el modelo de usuario personalizado
admin.site.register(Usuario, UsuarioAdmin)