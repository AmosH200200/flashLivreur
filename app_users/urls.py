from django.urls import path
from app_users import views 



urlpatterns = [
   # Routes pour les pages principales      
   path('', views.index, name="index"),
   path('tarifs', views.tarifs, name='tarifs'),
   path('supports', views.supports, name='supports'),
   path('contacts', views.contacts, name='contacts'),

   # ====================== Routes pour les clients =======================

   path('client_register/', views.client_register, name='client_register'),  # Inscription
   path('client_login/', views.client_login, name='client_login'),  # Connexion
   path('profil_client/', views.profil_client, name='profil_client'), 
   path('historique_client/', views.historique_client, name='historique_client'), 
   path('lancer_course/', views.lancer_course, name='lancer_course'),
   path('detail_course_client/<int:course_id>/', views.detail_course_client, name='detail_course_client'),
   path('historique_course_client/', views.historique_course_client, name='historique_course_client'),

   path('adresse/add/',                     views.add_adresse_client,    name='add_adresse_client'),
   path('adresse/<int:adresse_id>/edit/',   views.edit_adresse_client,   name='edit_adresse_client'),
   path('adresse/<int:adresse_id>/delete/', views.delete_adresse_client, name='delete_adresse_client'),

#ROUTES POUR LES COURSES 

   path('course/<int:course_id>/accepter/', views.accepter_course, name='accepter_course'),
   path('course/<int:course_id>/demarrer/', views.demarrer_course, name='demarrer_course'),
   path('course/<int:course_id>/livrer/',   views.livrer_course,   name='livrer_course'),
   path('course/<int:course_id>/annuler/',  views.annuler_course,  name='annuler_course'),
   path('course/<int:course_id>/annuler_livreur/',  views.annuler_course_livreur,  name='annuler_course_livreur'),
   path('course/<int:course_id>/refuser/',  views.refuser_course,  name='refuser_course'),
   path('course/detail_course_livreur/<int:course_id>/', views.detail_course_livreur, name='detail_course_livreur'),
   path('historique_course_livreur/', views.historique_course_livreur, name='historique_course_livreur'),



   # ====================== Routes pour les partenaires =======================
   path('partenaire_register/', views.partenaire_register, name='partenaire_register'),
   path('partenaire_login/', views.partenaire_login, name='partenaire_login'),
   path('confirmer_partenaire/<int:user_id>/', views.confirmer_partenaire, name='confirmer_partenaire'),

   #  ======================== Routes pour les livreurs =======================
   path('livreur_dashboard/', views.livreur_dashboard, name='livreur_dashboard'), 
   path('profil_livreur/', views.profil_livreur, name='profil_livreur'),
   path('profil/personal/',   views.update_profil_livreur,   name='update_profil_personal'),  
   path('profil/vehicule/',   views.update_vehicule,         name='update_profil_vehicule'), 

   # ======================= Routes pour les commercial =======================
   path('commercial_dashboard/', views.commercial_dashboard, name='commercial_dashboard'), 

   # ======================== Routes pour les admins =======================

   path('admin_login/', views.admin_login, name='admin_login'),  # Connexion 
  # path('admin_registration/', views.admin_register, name='admin_registration'),  # Formulaire d'ajout d'un admin 

   #  ======================== Routes du superadmin =======================

   path('super_admin_login/', views.super_admin_login, name='super_admin_login'),  
   #path('super/', views.super_admin_dashboard, name='super_admin_dashboard'), 
   path('gestion_admin/', views.gestion_admin, name='gestion_admin'),  # Gestion des admins

   # Gestion des clients
   path('gestion_client/', views.gestion_client, name='gestion_client'),
   path('add_client/', views.add_client, name='add_client'), #  Ajout d'un client 
   path('desactivate_client/<int:client_id>/', views.desactivate_client, name='desactivate_client'), # Suppression d'un client
   path('activate_client/<int:client_id>/', views.activate_client, name='activate_client'), # Activer d'un client
   path('detail_client/<int:client_id>/', views.detail_client, name='detail_client'), # Details d'un client
   path('update_client/<int:client_id>/', views.update_client, name='update_client'), # Mise à jour d'un client
   path("live-search-users/", views.live_search_users, name="live_search_users"),


   # Gestion des commerciaux
   path('gestion_commercial/', views.gestion_commercial, name='gestion_commercial'),  # Gestion des commercial
   path('add_commercial/', views.add_commercial, name='add_commercial'), #  Ajout d'un commercial
   path('detail_commercial/<int:commercial_id>/', views.detail_commercial, name='detail_commercial'), # Details d'un client
   path('activate_commercial/<int:commercial_id>/', views.activate_commercial, name='activate_commercial'), # Details d'un client
   path('update_commercial/<int:commercial_id>/', views.update_commercial, name='update_commercial'), # Mise à jour d'un client
   path('desactivate_commercial/<int:commercial_id>/', views.desactivate_commercial, name='desactivate_commercial'), # Details d'un client
   path("livreur_dashboard/", views.livreur_dashboard, name="livreur_dashboard"), # Tableau de bord livreur
   
   #Gestion de livreurs
   path('gestion_livreur/', views.gestion_livreur, name='gestion_livreur'),  # Gestion des livreurs
   path('add_livreur/', views.add_livreur, name='add_livreur'), #  Ajout d'un livreur
   path('detail_livreur/<int:livreur_id>/', views.detail_livreur, name='detail_livreur'),
   path('update_livreur/<int:livreur_id>/', views.update_livreur, name='update_livreur'), # Mise à jour d'un client
   path('activate_livreur/<int:livreur_id>/', views.activate_livreur, name='activate_livreur'), 
   path('desactivate_livreur/<int:livreur_id>/', views.desactivate_livreur, name='desactivate_livreur'), 
  
   # ========================= Routes pour les photos de profil =======================
   path('profil/photo/', views.update_photo_profil, name='update_photo_profil'),
   path('profil/photo/<int:user_id>/', views.update_photo_profil, name='update_photo_profil_user'),

   # ================================= Déconnexion des utilisateurs ==================================
   path('user_logout/', views.user_logout, name='user_logout'),


] 




