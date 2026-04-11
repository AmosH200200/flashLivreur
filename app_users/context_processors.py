from .models import User, LivreurProfile, CommercialProfile

def stats_processor(request):
    """
    Rend les statistiques disponibles dans tous les templates
    """
    if not request.user.is_authenticated:
        return {}
    
    if request.user.user_type not in ['superadmin', 'admin']:
        return {}

    stats = {
        # Clients
        'total_clients': User.objects.filter(user_type='client').count(),
        'clients_actifs': User.objects.filter(user_type='client', is_active=True).count(),
        'clients_bloquer': User.objects.filter(user_type='client', is_active=False).count(),
        
        # Livreurs
        'total_livreurs': User.objects.filter(user_type='livreur').count(),

        'livreurs_actifs': LivreurProfile.objects.filter(
            statut='approuve',
            user__is_active=True
        ).count(),

        'livreurs_en_attente': LivreurProfile.objects.filter(
            statut='en_attente'
        ).count(),

        'livreurs_bloques': LivreurProfile.objects.filter(
            statut='blocked'
        ).count(),
        
        # Commerciaux
        'total_commerciaux': User.objects.filter(user_type='commercial').count(),

        'commerciaux_actifs': CommercialProfile.objects.filter(
            statut='approuve',
            user__is_active=True
        ).count(),

        'commerciaux_en_attente': CommercialProfile.objects.filter(
            statut='en_attente'
        ).count(),

        'commerciaux_bloques': CommercialProfile.objects.filter(
            statut='blocked'
        ).count(),
        
        # Admins
        'total_admins': User.objects.filter(user_type='admin').count(),
        'admins_actifs': User.objects.filter(user_type='admin', is_active=True).count(),
        'total_superadmins': User.objects.filter(user_type='superadmin').count(),
        
        # Global
        'total_utilisateurs': User.objects.count(),
        'utilisateurs_actifs': User.objects.filter(is_active=True).count(),
    }

    return stats
