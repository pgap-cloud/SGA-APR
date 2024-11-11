# core/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def logout_required(function):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.warning(request, "Ya estás autenticado.")
            # Redirige al dashboard correspondiente según el rol del usuario
            if request.user.es_administrador:
                return redirect('admin_dashboard')
            elif request.user.es_secretaria:
                return redirect('secretaria_dashboard')
            elif request.user.es_operario:
                return redirect('operario_dashboard')
            elif request.user.es_usuario:
                return redirect('usuario_dashboard')
            else:
                return redirect('index')
        return function(request, *args, **kwargs)
    return wrapper