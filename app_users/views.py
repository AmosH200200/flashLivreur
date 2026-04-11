import datetime
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .forms import *
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import timedelta
from .models import ( AdresseLivraison, User, ClientProfile, LivreurProfile, CommercialProfile)
from .utils import search_users
from django.core.serializers.json import DjangoJSONEncoder
from django.core.paginator import Paginator


#Vue des page principale
def index(request):
    return render(request, 'index.html')

def tarifs(request):
    return render(request, 'tarifs.html')

def supports(request):
    return render(request, 'supports.html')

def contacts(request):
    return render(request, 'contacts.html')

# ==================== VUES D'INSCRIPTION ====================

def client_register(request):
    """Vue d'inscription pour les clients"""
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Récupérez le mot de passe brut avant qu'il soit hashé
            raw_password = form.cleaned_data.get('password') 

            #  Authentifiez l'utilisateur avec votre backend personnalisé
            authenticated_user = authenticate(
                request, 
                username=user.telephone,  # Le backend utilisera ce username pour chercher par telephone
                password=raw_password
            )

            if authenticated_user is not None:
                #  Connectez l'utilisateur automatiquement après inscription
                login(request, authenticated_user)  
                messages.success(request, 'Inscription réussie ! Bienvenue sur Flash Livreur.')        
                return redirect('index')
            else:
                messages.error(request, 'Erreur d\'authentification après l\'inscription.')
                return redirect('client_login')
        else:
            messages.error(request, 'Erreur lors de l\'inscription. Veuillez vérifier les informations.')
            print("Erreurs du formulaire:", form.errors)  # Regardez dans la console
            print("Erreurs non-field:", form.non_field_errors())
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'clients/client_register.html', {'form': form})


def partenaire_register(request):
    """Inscription pour les partenaires (livreurs et commerciaux)"""
    if request.user.is_authenticated:
        return redirect('partenaire_login')

    if request.method == 'POST':
        type_partenariat = request.POST.get('type_partenariat')

        if type_partenariat == 'livreur':
            form = LivreurRegistrationForm(request.POST, request.FILES)
        elif type_partenariat == 'commercial':
            form = CommercialRegistrationForm(request.POST, request.FILES)
        else:
            messages.error(request, "Veuillez choisir un type de partenaire.")
            return redirect('partenaire_register')

        if form.is_valid():
            form.save()  # Tout est créé automatiquement
            messages.success(
                request,
                "Inscription réussie ! Votre compte sera vérifié par notre équipe."
            )
            return redirect('partenaire_login')
        else:
            messages.error(request, "Erreur lors de l'inscription.")

    else:
        form = LivreurRegistrationForm()  # Formulaire vide pour l'affichage initial

    return render(request, 'partenaires/partenaire_register.html', {'form': form})



def admin_register(request):
    """Vue d'inscription pour les administrateurs"""
    # ⭐ Seuls les superadmins peuvent créer des admins
    if not request.user.is_authenticated or request.user.user_type != 'superadmin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Administrateur {user.get_full_name()} créé avec succès !')
            return redirect('super_admin_dashboard')
        else:
            messages.error(request, 'Erreur lors de la création.')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'admins/admin_register.html', {'form': form})


# ==================== VUES DE CONNEXION ====================

def client_login(request):
    """Vue de connexion pour les clients"""
    if request.user.is_authenticated:
        return redirect('client_dashboard')
    
    if request.method == 'POST':
        form = ClientLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                if user.user_type == 'client':
                    login(request, user)
                    messages.success(request, f'Bienvenue {user.get_full_name()} !')
                    return redirect('index')
                else:
                    messages.error(request, 'Ce compte n\'est pas un compte client.')
            else:
                messages.error(request, 'Identifiants incorrects.')
        else:
            messages.error(request, 'Erreur de connexion. Veuillez vérifier vos identifiants.')

            print("Erreurs du formulaire:", form.errors)  # Regardez dans la console
            print("Erreurs non-field:", form.non_field_errors())

    else:
        form = ClientLoginForm()
    
    return render(request, 'clients/client_login.html', {'form': form})


def partenaire_login(request):
    """Vue de connexion des partenaires"""

    # Déjà connecté
    if request.user.is_authenticated:
        if request.user.user_type == 'livreur':
            return redirect('livreur_dashboard')
        elif request.user.user_type == 'commercial':
            return redirect('commercial_dashboard')

    if request.method == 'POST':
        form = PartenaireLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()  # 🔥 LA bonne façon

            login(request, user)
            messages.success(request, f'Bienvenue {user.get_full_name()} !')

            # 🔁 Redirection selon le type
            if user.user_type == 'livreur':
                return redirect('livreur_dashboard')
            elif user.user_type == 'commercial':
                return redirect('commercial_dashboard')
            else:
                messages.error(
                    request,
                    "Ce compte n'est pas un compte partenaire."
                )
        else:
            messages.error(
                request,
                "Erreur de connexion. Veuillez vérifier vos identifiants."
            )

            # Debug (optionnel)
            print("Erreurs formulaire:", form.errors)
            print("Erreurs non-field:", form.non_field_errors())

    else:
        form = PartenaireLoginForm()

    return render(request, 'partenaires/partenaire_login.html', {
        'form': form
    })

def admin_login(request):
    """Vue de connexion pour les administrateurs"""
    if request.user.is_authenticated:
        if request.user.user_type == 'admin':
            return redirect('admin_dashboard')
        else:
            return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')  # Peut être email
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.user_type == 'admin':
                    login(request, user)
                    messages.success(request, f'Bienvenue {user.get_full_name()} !')
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Ce compte n\'est pas un compte administrateur.')
            else:
                messages.error(request, 'Identifiants incorrects.')
        else:
            messages.error(request, 'Erreur de connexion.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'admins/admin_login.html', {'form': form})


def super_admin_login(request):
    """Vue de connexion pour les superadmins"""

    if request.user.is_authenticated:
        if request.user.user_type == 'superadmin':
            return redirect('gestion_client')
        return redirect('index')

    if request.method == 'POST':
        form = SuperAdminLoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()  # ⭐ UTILISE TOUJOURS ÇA

            if user.user_type == 'superadmin' and user.is_superuser:
                login(request, user)
                messages.success(request, f'Bienvenue {user.get_full_name()} !')
                return redirect('gestion_client')
            else:
                messages.error(
                    request,
                    "Ce compte n'est pas un super administrateur."
                )
        else:
            print("Erreurs du formulaire:", form.errors)
            messages.error(request, "Identifiants incorrects.")

    else:
        form = SuperAdminLoginForm()
    return render(request, 'admin_supers/super_admin_login.html',{'form': form})

# ====================== fonction pour lancer une course ====================== 
def lancer_course(request):
    if request.method == 'POST':
        form = MaCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.client = request.user  # on associe le client connecté
            course.etat = 'attente'       # état par défaut

            # Combiner date et heure si c'est une course programmée
            if course.type_livraison == "programmer":  # ou votre valeur choisie
                date = form.cleaned_data.get('date_course_programmer')
                heure = form.cleaned_data.get('heure_course_programmer')
                if date and heure:
                    from datetime import datetime
                    course.date_course_programmer = datetime.combine(date, heure)

            course.save()
            return redirect('historique_client')  # redirige vers la liste
        else:
            print("erreur de formulaire:", form.errors)
    else:
        form = MaCourseForm()    
    return render(request, 'clients/lancer_course.html', {'form': form})    


@login_required
def accepter_course(request, course_id):
    """Livreur accepte → enroute"""
    course = get_object_or_404(MaCourse, id=course_id, etat='attente')
    course.livreur = request.user
    course.etat = 'enroute'
    course.save()
    return redirect('livreur_dashboard')

@login_required
def demarrer_course(request, course_id):
    """Livreur démarre → encours"""
    course = get_object_or_404(MaCourse, id=course_id, livreur=request.user, etat='enroute')
    course.etat = 'encours'
    course.save()
    return redirect('livreur_dashboard')

@login_required
def livrer_course(request, course_id):
    """Livreur livre → livre"""
    course = get_object_or_404(MaCourse, id=course_id, livreur=request.user, etat='encours')
    course.etat = 'livre'
    course.date_fin = timezone.now() 
    course.save()
    return redirect('livreur_dashboard')

@login_required #client
def annuler_course(request, course_id):
    """Client annule → annule"""
    course = get_object_or_404(MaCourse, id=course_id, client=request.user)
    if course.etat not in ['livre', 'annule']:
        course.etat = 'annule'
        course.date_fin = timezone.now()
        course.save()
    return redirect('historique_client')

@login_required
def refuser_course(request, course_id):
    """Livreur refuse → reste en attente, pas assigné"""
    course = get_object_or_404(MaCourse, id=course_id, etat='attente')
    course.livreurs_ayant_refuse.add(request.user) 
    return redirect('livreur_dashboard')

@login_required
def annuler_course_livreur(request, course_id):
    """livreur annule une course en cours → annule"""
    course = get_object_or_404(MaCourse, id=course_id, livreur=request.user, etat='enroute')
    course.etat = 'annule'
    course.date_fin = timezone.now()
    course.save()
    return redirect('livreur_dashboard')

# ==================== DASHBOARD CLIENT ====================

@login_required
def profil_client(request):

    adresses = AdresseLivraison.objects.filter(client=request.user.client_profile)

    if request.method == 'POST':
        form = ClientProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profil_client')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = ClientProfileForm(instance=request.user)

    return render(request, 'clients/profil_client.html', {'user_form': form, 'user': request.user,'adresses':adresses })

# ----------------Adresse de livraisons clients ---------------

@login_required
def add_adresse_client(request):
    if request.method == 'POST':
        client = request.user.client_profile
        AdresseLivraison.objects.create(
            client      = client,
            nom_adresse = request.POST.get('nom_adresse'),
            telephone_adresse   = request.POST.get('telephone_adresse'),
            rue         = request.POST.get('rue'),
            quartier    = request.POST.get('quartier'),
        )
        messages.success(request, 'Adresse ajoutée avec succès !')
        return redirect('profil_client')
    return redirect('profil_client')


@login_required
def edit_adresse_client(request, adresse_id):
    adresse = get_object_or_404(AdresseLivraison, id=adresse_id, client=request.user.client_profile)
    if request.method == 'POST':
        adresse.nom_adresse = request.POST.get('nom_adresse')
        adresse.telephone_adresse   = request.POST.get('telephone_adresse')
        adresse.rue         = request.POST.get('rue')
        adresse.quartier    = request.POST.get('quartier')
        adresse.save()
        messages.success(request, 'Adresse modifiée avec succès !')
        return redirect('profil_client')
    return redirect('profil_client')


@login_required
def delete_adresse_client(request, adresse_id):
    adresse = get_object_or_404(AdresseLivraison, id=adresse_id, client=request.user.client_profile)
    if request.method == 'POST':
        adresse.delete()
        messages.success(request, 'Adresse supprimée.')
    return redirect('profil_client')


# -------------------------------------------------------------
""" Vue pour la page historique client """
@login_required
def historique_client(request):
    limite = timezone.now() - timedelta(minutes=2)

    # Courses encore visibles dans la liste
    courses_actives = MaCourse.objects.filter(
        client=request.user
    ).filter(
        Q(etat__in=['attente', 'enroute', 'encours']) |
        Q(etat__in=['livre', 'annule'], date_fin__gte=limite)
    ).order_by('-date_creation')

    # Historique réel (plus de 2 minutes)
    courses_livrees = MaCourse.objects.filter(
        client=request.user,
        etat='livre',
        date_fin__lt=limite
    ).order_by('-date_fin')[:3]

    courses_annulees = MaCourse.objects.filter(
        client=request.user,
        etat='annule',
        date_fin__lt=limite
    ).order_by('-date_fin')[:3]

    return render(request, 'clients/historique_client.html', {
        'courses_actives': courses_actives,
        'courses_livrees': courses_livrees,
        'courses_annulees': courses_annulees,
    })

@login_required
def detail_course_client(request, course_id):
    course = get_object_or_404(MaCourse, id=course_id, client=request.user)
    return render(request, 'clients/detail_course_client.html', {
        'course': course 
    })

@login_required
def historique_course_client(request):
    if request.user.user_type != 'client':
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')

    # Paramètres GET
    tab_active = request.GET.get('tab', 'livrees')
    periode    = request.GET.get('periode', 'all')
    tri        = request.GET.get('tri', 'date-desc')
    q          = request.GET.get('q', '')
    page       = request.GET.get('page', 1)

    # Queryset de base (les deux états pour les stats)
    toutes = MaCourse.objects.filter(
        client=request.user,
        etat__in=['livre', 'annule']
    )
    livrees  = toutes.filter(etat='livre')
    annulees = toutes.filter(etat='annule')
    gains    = livrees.aggregate(total=Sum('prix'))['total'] or 0

    # Queryset selon l'onglet actif
    etat_filtre = 'livre' if tab_active == 'livrees' else 'annule'
    courses = toutes.filter(etat=etat_filtre)

    # Filtre période
    aujourd_hui = datetime.date.today()
    if periode == 'day':
        courses = courses.filter(date_creation__date=aujourd_hui)
    elif periode == 'week':
        debut = aujourd_hui - datetime.timedelta(days=6)
        courses = courses.filter(date_creation__date__gte=debut)
    elif periode == 'month':
        debut = aujourd_hui - datetime.timedelta(days=29)
        courses = courses.filter(date_creation__date__gte=debut)

    # Recherche
    if q:
        courses = courses.filter(
            Q(numero_course__icontains=q) |
            Q(lieu_depart__icontains=q)   |
            Q(client__first_name__icontains=q) |
            Q(client__last_name__icontains=q)
        )

    # Tri
    tri_map = {
        'date-desc': '-date_creation',
        'date-asc':   'date_creation',
        'prix-desc':  '-prix',
        'prix-asc':    'prix',
    }
    courses = courses.order_by(tri_map.get(tri, '-date_creation'))

    # Pagination
    paginator    = Paginator(courses, 8)
    courses_page = paginator.get_page(page)

    return render(request, 'clients/historique_course_client.html', {
        'courses':      toutes,
        'livrees':      livrees,
        'annulees':     annulees,
        'gains':        gains,
        'courses_page': courses_page,
        'tab_active':   tab_active,
        'periode':      periode,
        'tri':          tri,
        'q':            q,
    })
# ==================== DASHBOARD LIVREUR ====================

@login_required
def livreur_dashboard(request):
    """Dashboard livreur"""
    if request.user.user_type != 'livreur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')

    from django.db.models import Q
    from django.utils import timezone
    from datetime import timedelta

    limite = timezone.now() - timedelta(minutes=2)

    # Courses actives : disponibles + en cours + terminées récemment (< 2 min)
    courses_actives = MaCourse.objects.filter(
        Q(etat='attente', livreur=None) |  # disponibles pour tous
        Q(etat__in=['enroute', 'encours'], livreur=request.user) |  # en cours par ce livreur
        Q(etat__in=['livre', 'annule'], livreur=request.user, date_fin__gte=limite)  # terminées récemment
    ).exclude(
    etat='attente', livreurs_ayant_refuse=request.user  # cache les courses refusées
    ).order_by('-date_creation')

    # Historique réel : terminées depuis plus de 2 minutes
    courses_livrees = MaCourse.objects.filter(
        livreur=request.user,
        etat='livre',
        date_fin__lt=limite
    ).order_by('-date_fin')[:3]

    courses_annulees = MaCourse.objects.filter(
        livreur=request.user,
        etat='annule',
        date_fin__lt=limite
    ).order_by('-date_fin')[:3]

    return render(request, 'livreurs/livreur_dashboard.html', {
        'courses_actives': courses_actives,
        'courses_livrees': courses_livrees,
        'courses_annulees': courses_annulees,
    })


@login_required
def detail_course_livreur(request, course_id):
    course = get_object_or_404(MaCourse, id=course_id)
    return render(request, 'livreurs/detail_course_livreur.html', {'course': course})

@login_required
def historique_course_livreur(request):
    if request.user.user_type != 'livreur':
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')

    # Paramètres GET
    tab_active = request.GET.get('tab', 'livrees')
    periode    = request.GET.get('periode', 'all')
    tri        = request.GET.get('tri', 'date-desc')
    q          = request.GET.get('q', '')
    page       = request.GET.get('page', 1)

    # Queryset de base (les deux états pour les stats)
    toutes = MaCourse.objects.filter(
        livreur=request.user,
        etat__in=['livre', 'annule']
    )
    livrees  = toutes.filter(etat='livre')
    annulees = toutes.filter(etat='annule')
    gains    = livrees.aggregate(total=Sum('prix'))['total'] or 0

    # Queryset selon l'onglet actif
    etat_filtre = 'livre' if tab_active == 'livrees' else 'annule'
    courses = toutes.filter(etat=etat_filtre)

    # Filtre période
    aujourd_hui = datetime.date.today()
    if periode == 'day':
        courses = courses.filter(date_creation__date=aujourd_hui)
    elif periode == 'week':
        debut = aujourd_hui - datetime.timedelta(days=6)
        courses = courses.filter(date_creation__date__gte=debut)
    elif periode == 'month':
        debut = aujourd_hui - datetime.timedelta(days=29)
        courses = courses.filter(date_creation__date__gte=debut)

    # Recherche
    if q:
        courses = courses.filter(
            Q(numero_course__icontains=q) |
            Q(lieu_depart__icontains=q)   |
            Q(livreur__first_name__icontains=q) |
            Q(livreur__last_name__icontains=q)
        )

    # Tri
    tri_map = {
        'date-desc': '-date_creation',
        'date-asc':   'date_creation',
        'prix-desc':  '-prix',
        'prix-asc':    'prix',
    }
    courses = courses.order_by(tri_map.get(tri, '-date_creation'))

    # Pagination
    paginator    = Paginator(courses, 8)
    courses_page = paginator.get_page(page)

    return render(request, 'livreurs/historique_course_livreur.html', {
        'courses':      toutes,
        'livrees':      livrees,
        'annulees':     annulees,
        'gains':        gains,
        'courses_page': courses_page,
        'tab_active':   tab_active,
        'periode':      periode,
        'tri':          tri,
        'q':            q,
    })

@login_required
def profil_livreur(request):
    profile = getattr(request.user, 'livreur_profile', None)
    return render(request, 'livreurs/profil_livreur.html', {
        'user': request.user,
        'profile': profile,})    
    
@login_required
def detail_course_livreur(request, course_id):
    course = get_object_or_404(MaCourse, id=course_id, livreur=request.user)
    return render(request, 'livreurs/detail_course_livreur.html', {
        'course': course 
    })

# API : Mettre à jour les infos personnelles

@login_required
@require_http_methods(["POST"])
def update_profil_livreur(request):
    """
    Reçoit les données personnelles en JSON et les enregistre.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Données JSON invalides.'}, status=400)

    print("DATA REÇUE :", data) 

    form = PersonalInfoForm(data)
    if not form.is_valid():
        # Aplatir les erreurs en un seul message lisible
        errors = {field: msgs[0] for field, msgs in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors}, status=422)

    cd = form.cleaned_data
    user = request.user

    # ── Mise à jour du modèle User ──
    user.first_name     = cd['first_name']
    user.last_name      = cd['last_name']
    user.email          = cd['email']
    user.telephone      = cd['telephone']
    user.date_naissance = cd.get('date_naissance')
    user.save(update_fields=['first_name', 'last_name', 'email', 'telephone', 'date_naissance'])

    profile, _ = LivreurProfile.objects.get_or_create(user=user)
    profile.zone_couverture = cd.get('zone_couverture', '')
    profile.save(update_fields=['zone_couverture'])

    return JsonResponse({'success': True, 'message': 'Informations personnelles mises à jour !'})


# API : Mettre à jour les infos véhicule

@login_required
@require_http_methods(["POST"])
def update_vehicule(request):
    """
    Reçoit les données du véhicule en JSON et les enregistre.
    Champs mis à jour dans LivreurProfile :
        type_vehicule, immatriculation, marque_vehicule, modele_vehicule,
        numero_permis, date_expiration_permis, numero_compte_bancaire
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Données JSON invalides.'}, status=400)

    form = VehiculeInfoForm(data)
    if not form.is_valid():
        errors = {field: msgs[0] for field, msgs in form.errors.items()}
        return JsonResponse({'success': False, 'errors': errors}, status=422)

    cd = form.cleaned_data

    if not hasattr(request.user, 'livreur_profile'):
        return JsonResponse({'success': False, 'message': 'Profil livreur introuvable.'}, status=404)

    profile = request.user.livreur_profile
    profile.type_vehicule          = cd['type_vehicule']
    profile.immatriculation        = cd.get('immatriculation', '')
    profile.marque_vehicule        = cd.get('marque_vehicule', '')
    profile.modele_vehicule        = cd.get('modele_vehicule', '')
    profile.numero_permis          = cd.get('numero_permis', '')
    profile.date_expiration_permis = cd.get('date_expiration_permis')
    profile.numero_compte_bancaire = cd.get('numero_compte_bancaire', '')
    profile.save(update_fields=[
        'type_vehicule', 'immatriculation', 'marque_vehicule', 'modele_vehicule',
        'numero_permis', 'date_expiration_permis', 'numero_compte_bancaire'
    ])

    return JsonResponse({'success': True, 'message': 'Informations véhicule mises à jour !'})

# ==================== DASHBOARD COMMERCIAL ====================

#Vues dashboard commercial
@login_required
def commercial_dashboard(request):
    """Dashboard commercial"""
    if request.user.user_type != 'commercial':
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    return render(request, 'commercial/commercial_dashboard.html')

# ==================== DASHBOARD ADMIN ====================

#Vues dashboard admin
@login_required
def admin_dashboard(request):
    """Dashboard administrateur"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    return render(request, 'admins/admin_dashboard.html')

# =======================GESTION CLIENTS ======================

@login_required
def gestion_client(request):
    """Liste et gestion des clients"""

    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')

    clients = User.objects.filter(user_type='client').select_related('client_profile').order_by('-date_joined')

    context = {
        'clients': clients,
    }    
    return render(request, 'admin_supers/gestion_client.html', context)

@login_required
def add_client(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.username = user.telephone  # Utiliser le téléphone comme nom d'utilisateur            
            user.set_password("12345678") # mot de passe temporaire

            # gestion des rôles
            if user.user_type == "superadmin":
                user.is_staff = True
                user.is_superuser = True

            elif user.user_type == "admin":
                user.is_staff = True

            else:
                user.is_staff = False
                user.is_superuser = False

            user.save()
            messages.success(request, "Utilisateur ajouté avec succès")
            return redirect("gestion_client")
    else:
        form = UserCreateForm()

    return render(request, "admin_supers/gestion_client.html", {"form": form})

@login_required
def desactivate_client(request, client_id):
    """Désactiver un client par son ID"""
    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    
    try:
        client = User.objects.get(id=client_id, user_type='client')
        client.is_active = False
        client.save()
        messages.success(request, f'Client {client.get_full_name()} désactivé avec succès.')
    except User.DoesNotExist:
        messages.error(request, 'Client non trouvé.')
    
    return redirect('gestion_client')


def activate_client(request, client_id):
    """Réactiver un client désactivé"""
    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    
    try:
        client = User.objects.get(id=client_id, user_type='client')
        client.is_active = True
        client.save()
        messages.success(request, f'Client {client.get_full_name()} réactivé avec succès.')
    except User.DoesNotExist:
        messages.error(request, 'Client non trouvé.')
    
    return redirect('gestion_client')

@login_required
def detail_client(request, client_id):
    """Détail d'un client par son id"""
    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    
    try:
        client = User.objects.get(id=client_id, user_type='client')
    except User.DoesNotExist:
        messages.error(request, 'Client non trouvé.')
        return redirect('gestion_client') 
 
    client_statut = 'Actif' if client.is_active else 'Inactif'

    context = {
        'client': client,
        'client_statut': client_statut,
    }

    return render(request, 'admin_supers/detail_client.html', context)


@login_required
@require_http_methods(["POST"])
def update_client(request, client_id):
    try:
        # Récupérer le client
        client = get_object_or_404(User, id=client_id)
        
        # Récupérer les données du formulaire
        data = json.loads(request.body)
        
        # Mettre à jour les champs
        client.last_name = data.get('nom', client.last_name)
        client.first_name = data.get('prenom', client.first_name)
        client.email = data.get('email', client.email)
        client.telephone = data.get('telephone', client.telephone)
        
        # Mettre à jour le statut
        statut = data.get('statut', '').lower()
        if statut == 'actif':
            client.is_active = True
        elif statut == 'inactif':
            client.is_active = False
        
        # Sauvegarder
        client.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Client modifié avec succès!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=400)
    

def live_search_users(request):
    query = request.GET.get("q", "")
    user_type = request.GET.get("type")  # client | livreur | commercial | admin

    users = User.objects.filter(user_type=user_type).order_by("-date_joined")
    users = search_users(users, query)

    data = []

    for user in users:
        # Détermination sécurisée du statut
        if user.user_type == 'livreur' and hasattr(user, 'livreur_profile'):
            statut = user.livreur_profile.statut
        elif user.user_type == 'commercial' and hasattr(user, 'commercial_profile'):
            statut = user.commercial_profile.statut
        else:
            statut = None

        data.append({
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "telephone": user.telephone,
            "is_active": user.is_active,
            "user_type": user.user_type,
            "photo": user.photo.url if user.photo else None,
            "statut": statut
        })
    return JsonResponse(data, safe=False)

# ======================= VUES DE GESTION DES PARTENAIRES ======================
@login_required
def confirmer_partenaire(request, user_id):
    user = get_object_or_404(
        User,
        id=user_id,
        user_type__in=['livreur', 'commercial']
    )

    # LIVREUR
    if user.user_type == 'livreur' and hasattr(user, 'livreur_profile'):
        profil = user.livreur_profile

    # COMMERCIAL
    elif user.user_type == 'commercial' and hasattr(user, 'commercial_profile'):
        profil = user.commercial_profile

    else:
        messages.error(request, "Profil partenaire introuvable.")
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

    # Validation
    if profil.statut == 'en_attente':
        profil.statut = 'active'
        profil.save()

        user.is_active = True
        user.save()

        messages.success(
            request,
            f"{user.get_user_type_display()} confirmé avec succès."
        )

    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


# =======================GESTION LIVREURS ======================
@login_required
def gestion_livreur(request):
    """Liste et gestion des livreurs"""
    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    
    livreurs = User.objects.filter(user_type='livreur').select_related('livreur_profile').order_by('-date_joined')
    
    context ={
        'livreurs': livreurs,
    }
    return render(request, 'admin_supers/gestion_livreur.html', context)


def add_livreur(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.username = user.telephone  # Utiliser le téléphone comme nom d'utilisateur            
            user.set_password("12345678") # mot de passe temporaire

            # gestion des rôles
            if user.user_type == "superadmin":
                user.is_staff = True
                user.is_superuser = True

            elif user.user_type == "admin":
                user.is_staff = True

            else:
                user.is_staff = False
                user.is_superuser = False

            user.save()
            messages.success(request, "Utilisateur ajouté avec succès")
            return redirect("gestion_livreur")
    else:
        form = UserCreateForm()

    return render(request, "admin_supers/gestion_livreur.html", {"form": form})

def detail_livreur(request, livreur_id):
    livreur = get_object_or_404(User, id=livreur_id, user_type='livreur')

    # Statut sécurisé
    statut = None
    if hasattr(livreur, 'livreur_profile'):
        statut = livreur.livreur_profile.statut

    return render(
        request,
        'admin_supers/detail_livreur.html',
        {
            "livreur": livreur,
            "livreur_statut": statut}
    )

def activate_livreur(request, livreur_id):
    """Réactiver un livreur désactivé"""
    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    try:
        livreur = User.objects.get(id=livreur_id, user_type='livreur')
        livreur.is_active = True
        livreur.save()
        messages.success(request, f'livreur {livreur.get_full_name()} réactivé avec succès.')
    except User.DoesNotExist:
        messages.error(request, 'livreur non trouvé.')
    
    return redirect('gestion_livreur')

@login_required
def desactivate_livreur(request, livreur_id):
    """Désactiver un livreur par son ID"""
    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    
    try:
        livreur = User.objects.get(id=livreur_id, user_type='livreur')
        livreur.is_active = False
        livreur.save()
        messages.success(request, f'livreur {livreur.get_full_name()} désactivé avec succès.')
    except User.DoesNotExist:
        messages.error(request, 'livreur non trouvé.')
    
    return redirect('gestion_livreur')

@login_required
@require_http_methods(["POST"])
def update_livreur(request, livreur_id):
    try:
        # Récupérer le client
        livreur = get_object_or_404(User, id=livreur_id)
        
        # Récupérer les données du formulaire
        data = json.loads(request.body)
        
        # Mettre à jour les champs
        livreur.last_name = data.get('nom', livreur.last_name)
        livreur.first_name = data.get('prenom', livreur.first_name)
        livreur.email = data.get('email', livreur.email)
        livreur.telephone = data.get('telephone', livreur.telephone)
        
        # Mettre à jour le statut
        statut = data.get('statut', '').lower()
        if statut == 'actif':
            livreur.is_active = True
        elif statut == 'inactif':
            livreur.is_active = False
        
        # Sauvegarder
        livreur.save()
        
        return JsonResponse({
            'success': True,
            'message': 'livreur modifié avec succès!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=400)

# =======================GESTION COMMERCIAUX ======================

@login_required
def gestion_commercial(request):
    """Liste et gestion des commerciaux"""
    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    
    commercials = User.objects.filter(user_type='commercial').select_related('commercial_profile').order_by('-date_joined')
   
    context ={
        'commerciaux': commercials,
    }
    return render(request, 'admin_supers/gestion_commercial.html', context)


def add_commercial(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            user.username = user.telephone  # Utiliser le téléphone comme nom d'utilisateur            
            user.set_password("12345678") # mot de passe temporaire

            # gestion des rôles
            if user.user_type == "superadmin":
                user.is_staff = True
                user.is_superuser = True

            elif user.user_type == "admin":
                user.is_staff = True

            else:
                user.is_staff = False
                user.is_superuser = False

            user.save()
            messages.success(request, "Utilisateur ajouté avec succès")
            return redirect("gestion_commercial")
    else:
        form = UserCreateForm()

    return render(request, "admin_supers/gestion_commercial.html", {"form": form})


def detail_commercial(request, commercial_id):
    commercial = get_object_or_404(User, id=commercial_id, user_type='commercial')

    # Statut sécurisé
    statut = None
    if hasattr(commercial, 'commercial_profile'):
        statut = commercial.commercial_profile.statut

    return render(
        request,
        'admin_supers/detail_commercial.html',
        {
            "commercial": commercial,
            "commercial_statut": statut}
    )

def activate_commercial(request, commercial_id):
    """Réactiver un commercial désactivé"""
    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    try:
        commercial = User.objects.get(id=commercial_id, user_type='commercial')
        commercial.is_active = True
        commercial.save()
        messages.success(request, f'commercial {commercial.get_full_name()} réactivé avec succès.')
    except User.DoesNotExist:
        messages.error(request, 'commercial non trouvé.')
    
    return redirect('gestion_commercial')

@login_required
def desactivate_commercial(request, commercial_id):
    """Désactiver un livreur par son ID"""
    if request.user.user_type not in ['superadmin', 'admin']:
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    
    try:
        commercial = User.objects.get(id=commercial_id, user_type='commercial')
        commercial.is_active = False
        commercial.save()
        messages.success(request, f'commercial {commercial.get_full_name()} désactivé avec succès.')
    except User.DoesNotExist:
        messages.error(request, 'commercial non trouvé.')
    
    return redirect('gestion_commercial')

@login_required
@require_http_methods(["POST"])
def update_commercial(request, commercial_id):
    try:
        # Récupérer le client
        commercial = get_object_or_404(User, id=commercial_id)
        
        # Récupérer les données du formulaire
        data = json.loads(request.body)
        
        # Mettre à jour les champs
        commercial.last_name = data.get('nom', commercial.last_name)
        commercial.first_name = data.get('prenom', commercial.first_name)
        commercial.email = data.get('email', commercial.email)
        commercial.telephone = data.get('telephone', commercial.telephone)
        
        # Mettre à jour le statut
        statut = data.get('statut', '').lower()
        if statut == 'actif':
            commercial.is_active = True
        elif statut == 'inactif':
            commercial.is_active = False
        
        # Sauvegarder
        commercial.save()
        
        return JsonResponse({
            'success': True,
            'message': 'commercial modifié avec succès!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        }, status=400)

# =======================GESTION ADMIN ======================
@login_required
def gestion_admin(request):
    """Liste et gestion des administrateurs"""
    if request.user.user_type != 'superadmin':  # Seuls les superadmins peuvent gérer les admins
        messages.error(request, 'Accès non autorisé.')
        return redirect('index')
    
    # Récupérer tous les admins (pas les superadmins)
    admins = User.objects.filter(user_type='admin').order_by('-date_joined')
    
    # Récupérer tous les superadmins
    superadmins = User.objects.filter(user_type='superadmin').order_by('-date_joined')
    
    context = {
        'admins': admins,
        'superadmins': superadmins,
    }
    
    return render(request, 'admin_supers/gestion_admin.html', context)

# ================== MODIFICATION DES PHOTO DE PROFIL ==================
@login_required
@require_http_methods(["POST"])
def update_photo_profil(request, user_id=None):
    if user_id is None:
        # Tout le monde peut modifier SA PROPRE photo
        target_user = request.user

    else:

        # Seulement admin et superadmin peuvent modifier la photo d'un autre utilisateur
        if request.user.user_type not in ('admin', 'superadmin'):
            return JsonResponse({'error': 'Permission refusée'}, status=403)
        target_user = get_object_or_404(User, id=user_id)

    action = request.POST.get('action', 'update')

    if action == 'delete':
        if target_user.photo:
            target_user.photo.delete(save=False)
            target_user.photo = None
            target_user.save()
        return JsonResponse({'success': True, 'photo_url': None})

    if 'photo' not in request.FILES:
        return JsonResponse({'error': 'Aucun fichier reçu'}, status=400)

    fichier = request.FILES['photo']

    # Validation
    max_size = 5 * 1024 * 1024  # 5MB
    types_autorises = ['image/jpeg', 'image/png', 'image/webp']

    if fichier.size > max_size:
        return JsonResponse({'error': 'Fichier trop volumineux (max 5MB)'}, status=400)
    if fichier.content_type not in types_autorises:
        return JsonResponse({'error': 'Format non supporté (JPG, PNG, WEBP uniquement)'}, status=400)

    # Supprimer l'ancienne photo
    if target_user.photo:
        target_user.photo.delete(save=False)

    target_user.photo = fichier
    target_user.save()
    print(request.FILES)
    return JsonResponse({'success': True, 'photo_url': target_user.photo.url})


# ==================== VUE DE DÉCONNEXION ====================

@require_http_methods(["GET", "POST"])
def user_logout(request):
    """Vue de déconnexion pour tous les utilisateurs"""
    logout(request) 
    return redirect('index')









