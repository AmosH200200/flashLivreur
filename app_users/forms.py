import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, ClientProfile, LivreurProfile, CommercialProfile, MaCourse

# ==================== FORMULAIRES DE CONNEXION ====================

class ClientLoginForm(AuthenticationForm):
    """Formulaire de connexion pour les clients"""
    username = forms.CharField()

class PartenaireLoginForm (AuthenticationForm):
    """Formulaire de onnexion pour les partenaires"""
    def confirm_login_allowed(self, user):
        if user.user_type not in ['livreur', 'commercial']:
            raise forms.ValidationError(
                "Ce compte n'est pas un compte partenaire"
            )
        if not user.is_active:
            raise forms.ValidationError(
                "Ce compte partenaire n'est pas encore activé. Veuillez contacter le support."
            )
        
        

class SuperAdminLoginForm(AuthenticationForm):
    """Formulaire de connexion pour les super administrateurs"""
    username = forms.EmailField()
    
      
# ==================== FORMULAIRES D'INSCRIPTION ====================

class ClientRegistrationForm(UserCreationForm):
    """Formulaire d'inscription pour les clients"""
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    telephone = forms.CharField(max_length=20, required=True)
    date_naissance = forms.DateField(required=False)
    ville = forms.CharField(max_length=100, required=False)    
    
    # Champs du profil client
    adresse_livraison = forms.CharField(required=False, widget=forms.Textarea())

    
    class Meta:
        model = User
        fields = ['telephone', 'first_name', 'last_name', 'email',  
                  'date_naissance', 'password1', 'password2']
    
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['username'] = cleaned_data.get('telephone')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('telephone')
        user.user_type = 'client'
        if commit:
            user.save()
            ClientProfile.objects.create(
                user=user,
            )
        return user


class LivreurRegistrationForm(UserCreationForm):
    """Formulaire d'inscription pour les livreurs"""

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    telephone = forms.CharField(required=True)
    date_naissance = forms.DateField(required=False)
    photo = forms.ImageField(required=False)

    # Champs spécifiques livreur (TOUS OPTIONNELS)
    type_partenariat = forms.CharField(required=True)
    nom_entreprise = forms.CharField(required=False)
    adresse_entreprise = forms.CharField(required=True, widget=forms.Textarea())
    numero_permis = forms.CharField(required=False)
    date_expiration_permis = forms.DateField(required=False)
    type_vehicule = forms.CharField(required=False)
    immatriculation = forms.CharField(required=False)
    zone_couverture = forms.CharField(required=False)
    numero_compte_bancaire = forms.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'telephone',
            'first_name',
            'last_name',
            'email',
            'date_naissance',
            'photo',
            'password1',
            'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('telephone')
        user.user_type = 'livreur'
        user.is_active = False

        if commit:
            user.save()
            LivreurProfile.objects.create(user=user, statut='en_attente')

        return user


class CommercialRegistrationForm(UserCreationForm):
    """Formulaire d'inscription pour les commerciaux"""
    # Informations utilisateur
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    telephone = forms.CharField(required=True)
    
    # Informations entreprise
    type_partenariat = forms.CharField(required=True)
    nom_entreprise = forms.CharField(required=True)
    adresse_entreprise = forms.CharField(required=True, widget=forms.Textarea())
    description = forms.CharField(required=False, widget=forms.Textarea())
    logo = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['telephone', 'first_name', 'last_name', 'email',
                  'password1', 'password2']
    
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['username'] = cleaned_data.get('telephone')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('telephone')
        user.user_type = 'commercial'
        user.is_active = False

        if commit:
            user.save()
            CommercialProfile.objects.create(user=user, statut='en_attente')

        return user
    

'''class AdminRegistrationForm(UserCreationForm):
    """Formulaire d'inscription pour les administrateurs"""
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    telephone = forms.CharField(max_length=20, required=False)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'telephone',
                  'password1', 'password2']
    
    def clean(self):
        cleaned_data = super().clean()
        # Pour les admins, username = email
        cleaned_data['username'] = cleaned_data.get('email')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('email')
        user.user_type = 'admin'
        user.is_staff = True  # ⭐ Important pour les admins
        if commit:
            user.save()
        return user

'''

class SuperAdminRegistrationForm(UserCreationForm):
    """Formulaire d'inscription pour les super administrateurs"""
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']
    
    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['username'] = cleaned_data.get('email')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data.get('email')
        user.user_type = 'superadmin'
        user.is_staff = True      # ⭐ Accès zone admin
        user.is_superuser = True  # ⭐ Tous les droits
        if commit:
            user.save()
        return user

class UserCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "telephone",
            "user_type",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email existe déjà")
        return email
    
    def clean_telephone(self):
        telephone = self.cleaned_data.get("telephone")
        if telephone and User.objects.filter(username=telephone).exists():
            # username = téléphone, donc on vérifie ici
            raise forms.ValidationError("Ce numéro de téléphone est déjà utilisé")
        return telephone    
    


class PersonalInfoForm(forms.Form):
    """Validation des informations personnelles du livreur."""
    first_name      = forms.CharField(max_length=50,  label="Prénom")
    last_name       = forms.CharField(max_length=50,  label="Nom")
    email           = forms.EmailField(label="Email")
    telephone       = forms.CharField(max_length=20,  label="Téléphone")
    date_naissance  = forms.DateField(input_formats=['%Y-%m-%d'],label="Date de naissance",required=False)
    zone_couverture = forms.CharField(max_length=200, label="Zone de couverture", required=False)


class VehiculeInfoForm(forms.Form):
    """Validation des informations véhicule du livreur."""
    VEHICULE_CHOICES = [
        ('moto',    '🏍️ Moto'),
        ('velo',    '🚲 Vélo'),
        ('voiture', '🚗 Voiture'),
        ('scooter', '🛵 Scooter'),
    ]
    type_vehicule          = forms.ChoiceField(choices=VEHICULE_CHOICES)
    immatriculation        = forms.CharField(max_length=50,  required=False)
    marque_vehicule        = forms.CharField(max_length=100, required=False)
    modele_vehicule        = forms.CharField(max_length=100, required=False)
    numero_permis          = forms.CharField(max_length=50,  required=False)
    date_expiration_permis = forms.DateField(input_formats=['%Y-%m-%d'], required=False)   
 
class MaCourseForm(forms.ModelForm):

    class Meta:
        model = MaCourse
        fields = [
            'lieu_depart',
            'lieu_arrivee',
            'type_livraison',
            'nature_colis',
            'description_colis',
            'nom_destinataire',
            'telephone_destinataire',
            'instructions',
            'date_course_programmer',
            'heure_course_programmer',
        ]

    def clean_telephone_destinataire(self):
        telephone = self.cleaned_data.get('telephone_destinataire')
        if not re.match(r'^[\d\s\+\-]{8,20}$', telephone):
            raise forms.ValidationError("Numéro de téléphone invalide.")
        return telephone
    

class ClientProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'telephone', 'date_naissance', 'ville']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False