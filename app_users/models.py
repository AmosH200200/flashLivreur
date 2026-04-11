# models.py
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('client', 'Client'),
        ('livreur', 'Livreur'),
        ('commercial', 'Commercial'),
        ('admin', 'Administrateur'),
        ('superadmin', 'Super Administrateur'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    telephone = models.CharField(max_length=20, blank=True, unique=True)
    date_naissance = models.DateField(blank=True, null=True)
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, default='')
    
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"
    
    # Méthode helper pour obtenir le statut de vérification
    def get_statut(self):
        """Retourne le statut de vérification si applicable (livreur/commercial)"""
        if self.user_type == 'livreur' and hasattr(self, 'livreur_profile'):
            return self.livreur_profile.statut
        elif self.user_type == 'commercial' and hasattr(self, 'commercial_profile'):
            return self.commercial_profile.statut
        return None

class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client_profile')
    def __str__(self):
        return f"Profil Client - {self.user.get_full_name()}"

class AdresseLivraison(models.Model):
    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name='adresses_livraison'
    )
    nom_adresse = models.CharField(max_length=100)   
    telephone_adresse = models.CharField(max_length=20)
    rue = models.CharField(max_length=200)
    quartier = models.CharField(max_length=100)

    par_defaut = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.par_defaut:
            AdresseLivraison.objects.filter(client=self.client, par_defaut=True).update(par_defaut=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom_adresse} — {self.client.user.username}"

class LivreurProfile(models.Model):
    STATUT_CHOICES = (
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('active', 'Actif'),
        ('blocked', 'Bloqué'),
    )

    VEHICULE_CHOICES = [
        ('moto',    '🏍️ Moto'),
        ('velo',    '🚲 Vélo'),
        ('voiture', '🚗 Voiture'),
        ('scooter', '🛵 Scooter'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='livreur_profile')
    numero_permis = models.CharField(max_length=50, blank=True, null=True)
    date_expiration_permis = models.DateField(blank=True, null=True)
    type_vehicule = models.CharField(max_length=20, choices=VEHICULE_CHOICES, default='moto')
    immatriculation = models.CharField(max_length=50, blank=True, null=True)
    modele_vehicule = models.CharField(max_length=100, blank=True, null=True)
    marque_vehicule = models.CharField(max_length=100, blank=True, null=True)
    zone_couverture = models.CharField(max_length=200, blank=True, null=True)
    disponibilite = models.BooleanField(default=True)
    numero_compte_bancaire = models.CharField(max_length=100, blank=True, null=True)
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='en_attente'
    )
    
    def __str__(self):
        return f"Profil Livreur - {self.user.get_full_name()}"

class CommercialProfile(models.Model):
    STATUT_CHOICES = (
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'), 
        ('active', 'Actif'),
        ('blocked', 'Bloqué'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='commercial_profile')

    nom_entreprise = models.CharField(max_length=200, blank=True, null=True)

    adresse_entreprise = models.TextField(blank=True, null=True)

    type_partenariat = models.CharField(max_length=100, blank=True, null=True)

    horaires_ouverture = models.JSONField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    logo = models.ImageField(upload_to='commerciaux/', blank=True, null=True)

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente'
    )

    def __str__(self):
        return f"Profil Commercial - {self.nom_entreprise or self.user.get_full_name()}"


class MaCourse(models.Model):

    ETAT_CHOICES = [
        ('attente', 'En attente'),
        ('enroute', 'En route vers client'),
        ('encours', 'En cours de livraison'),
        ('livre', 'Livré'),
        ('annule', 'Annulé'),
    ]

    TYPE_LIVRAISON_CHOICES = [
        ('standard', 'Standard'),
        ('express', 'Express'),
        ('programmer', 'Programmé'),
    ]
    numero_course = models.CharField(max_length=20,unique=True,blank=True)

    date_course_programmer = models.DateField(null=True, blank=True)  # DateField au lieu de DateTimeField
    heure_course_programmer = models.TimeField(null=True, blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(null=True, blank=True)

    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses_client'
    )

    livreur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses_livreur'
    )

    lieu_depart = models.CharField(max_length=255) 
    lieu_arrivee = models.CharField(max_length=255)

    latitude_depart = models.FloatField(null=True, blank=True)
    longitude_depart = models.FloatField(null=True, blank=True)

    latitude_arrivee = models.FloatField(null=True, blank=True)
    longitude_arrivee = models.FloatField(null=True, blank=True)

    # Position temps réel du livreur
    latitude_actuelle = models.FloatField(null=True, blank=True)
    longitude_actuelle = models.FloatField(null=True, blank=True)

    livreurs_ayant_refuse = models.ManyToManyField(User, blank=True, related_name='courses_refusees')

    type_livraison = models.CharField(max_length=20,choices=TYPE_LIVRAISON_CHOICES,default='standard')

    nature_colis = models.CharField(max_length=100)

    description_colis = models.TextField(blank=True) 

    nom_destinataire = models.CharField(max_length=150)

    telephone_destinataire = models.CharField(max_length=20)

    instructions = models.TextField(blank=True)

    temps_estime = models.IntegerField(null=True,blank=True,help_text="Temps estimé en minutes")

    prix = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)

    etat = models.CharField(
        max_length=20,
        choices=ETAT_CHOICES,
        default='attente'
    )

    def save(self, *args, **kwargs):
        if not self.numero_course:
            self.numero_course = "CR-" + str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_course} - {self.client.username}"
