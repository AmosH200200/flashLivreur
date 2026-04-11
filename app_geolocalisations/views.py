from django.shortcuts import render
from app_users.models import *
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

def geolocalisation(request):
    return render(request, 'geolocalisation.html')

@login_required
def tracking_client(request, course_id):
    """
    Page de suivi pour le CLIENT.
    Affiche la carte avec la position du livreur en temps réel.
    """
    course = get_object_or_404(MaCourse, id=course_id, client=request.user)
    
    # Vérifier que la course est en cours (enroute ou encours)
    if course.etat not in ['enroute', 'encours']:
        # Rediriger ou afficher un message si la course n'est pas active
        return render(request, 'tracking/tracking_indisponible.html', {'course': course})
    
    context = {
        'course': course,
        'role': 'client',
    }
    return render(request, 'tracking/tracking_client.html', context)


@login_required
def tracking_livreur(request, course_id):
    """
    Page de suivi pour le LIVREUR.
    Active le GPS du navigateur et envoie la position au serveur.
    """
    course = get_object_or_404(MaCourse, id=course_id, livreur=request.user)
    
    context = {
        'course': course,
        'role': 'livreur',
    }
    return render(request, 'tracking/tracking_livreur.html', context)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def update_position(request, course_id):
    """
    Endpoint appelé par le LIVREUR toutes les 3 secondes.
    Met à jour latitude_actuelle et longitude_actuelle dans la base de données.
    """
    course = get_object_or_404(MaCourse, id=course_id, livreur=request.user)
    
    try:
        data = json.loads(request.body)
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat is None or lng is None:
            return JsonResponse({'success': False, 'error': 'Coordonnées manquantes'}, status=400)
        
        # Mise à jour de la position dans la base de données
        course.latitude_actuelle = float(lat)
        course.longitude_actuelle = float(lng)
        course.save(update_fields=['latitude_actuelle', 'longitude_actuelle'])
        
        return JsonResponse({'success': True, 'message': 'Position mise à jour'})
    
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def get_position(request, course_id):
    """
    Endpoint appelé par le CLIENT toutes les 3 secondes.
    Retourne la position actuelle du livreur + l'état de la course.
    """
    course = get_object_or_404(MaCourse, id=course_id, client=request.user)
    
    data = {
        'success': True,
        'etat': course.etat,
        'latitude_actuelle': course.latitude_actuelle,
        'longitude_actuelle': course.longitude_actuelle,
        'latitude_depart': course.latitude_depart,
        'longitude_depart': course.longitude_depart,
        'latitude_arrivee': course.latitude_arrivee,
        'longitude_arrivee': course.longitude_arrivee,
        'lieu_depart': course.lieu_depart,
        'lieu_arrivee': course.lieu_arrivee,
        'livreur_nom': course.livreur.get_full_name() if course.livreur else '',
        'numero_course': course.numero_course,
    }
    
    return JsonResponse(data)


@login_required
@require_http_methods(["POST"])
def update_etat_course(request, course_id):
    """
    Permet au LIVREUR de changer l'état de la course.
    ex: passer de 'enroute' à 'encours' ou 'livre'
    """
    course = get_object_or_404(MaCourse, id=course_id, livreur=request.user)
    
    try:
        data = json.loads(request.body)
        nouvel_etat = data.get('etat')
        
        etats_valides = ['enroute', 'encours', 'livre', 'annule']
        if nouvel_etat not in etats_valides:
            return JsonResponse({'success': False, 'error': 'État invalide'}, status=400)
        
        course.etat = nouvel_etat
        
        # Si livré, enregistrer la date de fin
        if nouvel_etat == 'livre':
            from django.utils import timezone
            course.date_fin = timezone.now()
        
        course.save()
        return JsonResponse({'success': True, 'etat': course.etat})
    
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)