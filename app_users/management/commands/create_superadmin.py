from django.core.management.base import BaseCommand
from app_users.models import User  

class Command(BaseCommand):
    help = 'Crée le premier super administrateur'

    def handle(self, *args, **kwargs):
        email = input('Email du super admin: ')
        telephone = input('Téléphone: ')
        first_name = input('Prénom: ')
        last_name = input('Nom: ')
        password = input('Mot de passe: ')
        
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_user(
                username=email,
                email=email,
                telephone=telephone,
                first_name=first_name,
                last_name=last_name,
                password=password,
                user_type='superadmin'
            )
            self.stdout.write(self.style.SUCCESS(f'Super admin {email} créé avec succès!'))
        else:
            self.stdout.write(self.style.ERROR('Cet email existe déjà!'))