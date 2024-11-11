from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
import re

# Obtiene el modelo de usuario personalizado
User = get_user_model()

class RegistroForm(UserCreationForm):
    """Formulario comprehensive para registro de usuarios."""
    
    # Campos personalizados con widgets y validaciones
    username = forms.CharField(
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese su nombre de usuario'
        }),
        help_text="El nombre de usuario debe tener al menos 3 caracteres."
    )
    
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'ejemplo@dominio.com'
        }),
        help_text="Ingrese un correo electrónico válido"
    )
    
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Ingrese su contraseña'
        }),
        help_text=(
            "La contraseña debe tener al menos 8 caracteres. "
            "Debe contener mayúsculas, minúsculas y números."
        )
    )
    
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Repita su contraseña'
        }),
        help_text="Repita la contraseña para confirmar"
    )
    
    telefono = forms.CharField(
        label="Teléfono (Opcional)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Número de teléfono'
        }),
        help_text="Ingrese su número de teléfono (opcional)"
    )
    
    direccion = forms.CharField(
        label="Dirección (Opcional)",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Dirección de contacto'
        }),
        help_text="Ingrese su dirección (opcional)"
    )
    
    class Meta:
        model = User
        fields = [
            'username', 
            'email', 
            'password1', 
            'password2', 
            'rol', 
            'telefono', 
            'direccion'
        ]
        
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'})
        }
    
    def clean_username(self):
        """Validaciones específicas para el nombre de usuario."""
        username = self.cleaned_data.get('username')
        
        # Validaciones
        if not username:
            raise ValidationError("El nombre de usuario es obligatorio.")
        
        if len(username) < 3:
            raise ValidationError("El nombre de usuario debe tener al menos 3 caracteres.")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("El nombre de usuario solo puede contener letras, números y guiones bajos.")
        
        # Chequeo de existencia
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        
        return username
    
    def clean_email(self):
        """Validaciones específicas para el correo electrónico."""
        email = self.cleaned_data.get('email')
        
        # Validación de formato
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Ingrese un correo electrónico válido.")
        
        # Chequeo de existencia
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        
        return email
    
    def clean_password1(self):
        """Validaciones específicas para la contraseña."""
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        # Complejidad de contraseña
        if not re.search(r'[A-Z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        
        if not re.search(r'\d', password):
            raise ValidationError("La contraseña debe contener al menos un número.")
        
        return password
    
    def clean(self):
        """Validaciones generales del formulario."""
        cleaned_data = super().clean()
        
        # Validación de coincidencia de contraseñas
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError({
                "password2": "Las contraseñas no coinciden."
            })
        
        return cleaned_data
    
    def clean_rol(self):
        """Validación del rol seleccionado."""
        rol = self.cleaned_data.get('rol')
        roles_validos = [r[0] for r in User.ROLES]
        
        if rol not in roles_validos:
            raise ValidationError("Seleccione un rol válido.")
        
        return rol
    
    def save(self, commit=True):
        """Personalización del guardado de usuario."""
        user = super().save(commit=False)
        
        # Asignación de campos
        user.email = self.cleaned_data['email']
        user.telefono = self.cleaned_data.get('telefono', '')
        user.direccion = self.cleaned_data.get('direccion', '')
        
        # Rol por defecto
        if not user.rol:
            user.rol = 'USUARIO'
        
        if commit:
            user.save()
        
        return user