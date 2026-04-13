import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flashLivreur.settings')
django.setup()

from app_users.models import User

username = os.environ.get('ADMIN_USER')
email    = os.environ.get('ADMIN_EMAIL')
password = os.environ.get('ADMIN_PASS')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username=username,
        email=email,
        password=password,
        first_name='Super',
        last_name='Admin',
        user_type='superadmin'
    )
    print("✅ Superadmin créé avec succès !")
else:
    print("⚠️ Superadmin existe déjà, rien n'a été fait.")