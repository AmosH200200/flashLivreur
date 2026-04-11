# app_users/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class FlexibleAuthBackend(ModelBackend):
    """
    Backend d'authentification flexible :
    - Email pour admin/superadmin
    - Téléphone pour client/livreur/partenaire
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        
        user = None
        
        try:
            # Si ça ressemble à un email, cherchez par email
            if '@' in username:
                user = User.objects.get(email=username)
            # Sinon, cherchez par téléphone
            else:
                user = User.objects.get(telephone=username)
        except User.DoesNotExist:
            return None
        
        # Vérifiez le mot de passe
        if user and user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None