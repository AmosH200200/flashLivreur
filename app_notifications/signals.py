# app_notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    if created:

        # Définir le message selon le rôle
        if instance.user_type == 'livreur':
            subject = 'Bienvenue sur FlashLivreur !'
            message = f"""Bonjour {instance.get_full_name()},

Votre compte livreur a été créé avec succès sur FlashLivreur.

Afin de finaliser votre inscription, nous vous invitons à vous rendre à notre agence muni de vos documents (pièce d'identité, permis de conduire, etc.).

À très bientôt !
L'équipe FlashLivreur"""

        elif instance.user_type == 'commercial':
            subject = 'Bienvenue sur FlashLivreur !'
            message = f"""Bonjour {instance.get_full_name()},

Votre compte commercial a été créé avec succès sur FlashLivreur.

Afin de finaliser votre inscription, nous vous invitons à vous rendre à notre agence pour signer votre contrat et récupérer vos accès.

À très bientôt !
L'équipe FlashLivreur"""

        else:
            # Client, admin, superadmin
            subject = 'Bienvenue sur FlashLivreur !'
            message = f"""Bonjour {instance.get_full_name()},

Votre compte a été créé avec succès sur FlashLivreur.

Bonne expérience !
L'équipe FlashLivreur"""

        # Notification en base
        Notification.objects.create(
            user=instance,
            type='welcome',
            title='Bienvenue sur la plateforme !',
            message=message,
        )

        # Envoi email
        if instance.email:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )