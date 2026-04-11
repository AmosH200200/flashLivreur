from django.urls import path
from app_geolocalisations import views

app_name = 'tracking' 

urlpatterns = [
    path('geolocalisation/', views.geolocalisation, name='geolocalisation'),

       # Page de suivi pour le CLIENT (voir la carte)
    path('client/<int:course_id>/', views.tracking_client, name='tracking_client'),
    
    # Page de suivi pour le LIVREUR (GPS actif)
    path('livreur/<int:course_id>/', views.tracking_livreur, name='tracking_livreur'),
    
    # API : le livreur envoie sa position (POST)
    path('api/update-position/<int:course_id>/', views.update_position, name='update_position'),
    
    # API : le client récupère la position (GET, appelé toutes les 3s)
    path('api/get-position/<int:course_id>/', views.get_position, name='get_position'),
    
    # API : le livreur change l'état de la course
    path('api/update-etat/<int:course_id>/', views.update_etat_course, name='update_etat'),
]