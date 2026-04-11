# decorators.py
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    """Décorateur pour restreindre l'accès aux admins et superadmins"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('login')
        
        if not request.user.is_admin:
            messages.error(request, "Accès non autorisé. Réservé aux administrateurs.")
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def super_admin_required(view_func):
    """Décorateur pour restreindre l'accès aux superadmins uniquement"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('login')
        
        if not request.user.is_superadmin:
            messages.error(request, "Accès non autorisé. Réservé aux super administrateurs.")
            return redirect('dashboard')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def user_type_required(*allowed_types):
    """Décorateur pour restreindre l'accès selon le type d'utilisateur"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Vous devez être connecté.")
                return redirect('login')
            
            if request.user.user_type not in allowed_types:
                messages.error(request, "Accès non autorisé.")
                return redirect('login')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator